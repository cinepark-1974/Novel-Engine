"""
idea_extractor.py — Idea Engine JSON → 소설화 변환 모듈 (Novel Engine v3.3)
================================================================================

Idea Engine(v2.0)이 출력한 IdeaSeed JSON을 받아,
Novel Engine STEP 1 입력 자료(12개 필드)로 변환한다.

Creator Engine 입력과의 결정적 차이
-----------------------------------
Creator JSON은 open_items=0 인 '확정 완료' 데이터지만,
Idea JSON은 pending_decisions / locked_creator_questions 에
'아직 결정되지 않은 항목'이 남아 있는 초안 상태다.

이 모듈은 미결정을 빈칸으로 두지 않는다.
엔진이 각 미결정에 대해 '제안'을 채워 넣되, 반드시 [엔진 제안] 표식을 붙여
작가가 무엇이 원본 확정이고 무엇이 엔진 판단인지 구분할 수 있게 한다.
(사고 패턴 F — 추출값을 확정으로 취급하지 않는다)

설계 원칙
---------
1. 출력 딕셔너리의 키 구조는 scenario_extractor / creator_extractor 와
   완전히 동일하다. STEP 1은 코드 수정 없이 그대로 읽는다.
2. Idea JSON에는 캐릭터 프로필(char_bible 상당)이 없다.
   로그라인·테마·훅·펀치신·엔딩·빌런 구조로부터 캐릭터를 엔진이 제안 구성한다.
3. locked_* 필드는 LOCKED 블록으로 보호한다. 미결정은 OPEN 쪽에 가깝다.

처리 흐름
---------
extract_idea_fields(idea_json, client)
  ├─ 1단계 build_idea_digest(): 파이썬으로 locked_seed 서사 필드를 정돈,
  │                              미결정 항목을 별도 수집
  └─ 2단계 LLM 호출: digest를 소설화 + 미결정에 [엔진 제안] 부여 + 12키 추출
"""

import json
import re
from typing import Any, Dict, List, Optional


# ─────────────────────────────────────
# 안전 접근 헬퍼
# ─────────────────────────────────────
def _s(obj: Any, *keys, default: str = "") -> str:
    """중첩 dict에서 문자열을 안전하게 꺼낸다."""
    cur = obj
    for k in keys:
        if isinstance(cur, dict):
            cur = cur.get(k)
        else:
            return default
    if cur is None:
        return default
    if isinstance(cur, (list, dict)):
        return default
    return str(cur).strip()


def _flat(obj: Any, indent: str = "    ") -> List[str]:
    """dict/list를 사람이 읽을 수 있는 줄 목록으로 평탄화."""
    out: List[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                sub = _flat(v, indent + "  ")
                if sub:
                    out.append(f"{indent}{k}:")
                    out.extend(sub)
            else:
                sv = str(v).strip() if v is not None else ""
                if sv:
                    out.append(f"{indent}{k}: {sv}")
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                sub = _flat(item, indent + "  ")
                if sub:
                    out.append(f"{indent}-")
                    out.extend(sub)
            else:
                sv = str(item).strip() if item is not None else ""
                if sv:
                    out.append(f"{indent}- {sv}")
    return out


# ─────────────────────────────────────
# 미결정 항목 수집
# ─────────────────────────────────────
def collect_pending_items(idea_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """미결정 항목을 통합 수집.

    두 소스를 합친다.
    - locked_seed.locked_creator_questions : {question, options, importance} 구조
    - pending_decisions                    : 자연문 리스트

    Returns:
        [{"question": str, "options": [str], "importance": str, "source": str}, ...]
    """
    items: List[Dict[str, Any]] = []

    # 1) 정본 — locked_creator_questions
    #    {question, options, importance} 구조라 엔진 제안에 필요한 정보가 다 있다.
    ls = idea_json.get("locked_seed", {})
    if isinstance(ls, dict):
        for q in ls.get("locked_creator_questions", []) or []:
            if not isinstance(q, dict):
                continue
            question = str(q.get("question", "")).strip()
            if not question:
                continue
            opts = q.get("options", [])
            opts = [str(o).strip() for o in opts if str(o).strip()] if isinstance(opts, list) else []
            items.append({
                "question": question,
                "options": opts,
                "importance": str(q.get("importance", "")).strip(),
                "source": "locked_creator_questions",
            })

    # 2) 폴백 — pending_decisions
    #    Idea Engine은 같은 논점을 questions(구조화)와 pending_decisions(자연문)
    #    양쪽에 중복 기록한다. 정본이 이미 있으면 자연문 쪽은 쓰지 않는다.
    #    정본이 비어 있을 때만 자연문을 미결정 목록으로 사용한다.
    if not items:
        for pd in idea_json.get("pending_decisions", []) or []:
            text = str(pd).strip()
            if not text:
                continue
            items.append({
                "question": text,
                "options": [],
                "importance": "",
                "source": "pending_decisions",
            })

    return items


# ─────────────────────────────────────
# 1단계 — Idea JSON → 서사 다이제스트
# ─────────────────────────────────────
def build_idea_digest(idea_json: Dict[str, Any]) -> Dict[str, Any]:
    """Idea JSON에서 소설화에 필요한 서사 필드를 뽑아 정돈된 텍스트로 만든다.

    Returns:
        {"meta": {...}, "digest_text": str,
         "pending_items": [...], "locked_lines": [str]}
    """
    ls = idea_json.get("locked_seed", {})
    if not isinstance(ls, dict):
        ls = {}

    lines: List[str] = []

    # ── 기본 메타 ──
    title = _s(ls, "title_kr") or _s(idea_json, "title")
    genre_raw = idea_json.get("genre", "")
    genre = genre_raw if isinstance(genre_raw, str) else _s(ls, "locked_genre", "primary")
    fmt = _s(ls, "locked_format", "primary") or _s(idea_json, "format")
    raw_idea = _s(idea_json, "raw_idea")

    lines.append(f"[작품 제목] {title}")
    lines.append(f"[원본 장르] {genre}")
    lines.append(f"[원본 매체] {fmt}  ← 이 기획은 영상/기획 단계다. 소설로 전환해야 한다.")
    if raw_idea:
        lines.append(f"[최초 아이디어] {raw_idea}")
    lines.append("")

    # ── 로그라인 ──
    ll = _s(ls, "locked_logline")
    if ll:
        lines.append("[확정 로그라인]")
        lines.append(f"  {ll}")
        lines.append("")

    # ── 장르 (다층) ──
    lg = ls.get("locked_genre")
    if isinstance(lg, dict) and lg:
        lines.append("[확정 장르]")
        lines.extend(_flat(lg, "  "))
        lines.append("")

    # ── 테마 ──
    th = ls.get("locked_theme")
    if isinstance(th, dict) and th:
        lines.append("[확정 테마]")
        lines.extend(_flat(th, "  "))
        lines.append("")
    elif isinstance(th, str) and th.strip():
        lines.append(f"[확정 테마] {th.strip()}")
        lines.append("")

    # ── 훅 시그니처 ──
    hs = ls.get("locked_hook_signature")
    if isinstance(hs, dict) and hs:
        lines.append("[훅 시그니처 — 작품의 핵심 매력]")
        lines.extend(_flat(hs, "  "))
        lines.append("")

    # ── 공감 앵커 ──
    ea = ls.get("locked_empathy_anchor")
    if isinstance(ea, dict) and ea:
        lines.append("[공감 앵커 — 독자 감정이입 설계]")
        lines.extend(_flat(ea, "  "))
        lines.append("")

    # ── 펀치 신 ──
    ps = ls.get("locked_punch_scene")
    if isinstance(ps, dict) and ps:
        lines.append("[펀치 신 — 반드시 살릴 결정적 장면]")
        lines.extend(_flat(ps, "  "))
        lines.append("")

    # ── 엔딩 형태 / 엔딩 약속 ──
    ef = ls.get("locked_ending_form")
    if isinstance(ef, dict) and ef:
        lines.append("[확정 엔딩 형태]")
        lines.extend(_flat(ef, "  "))
        lines.append("")

    ep = ls.get("locked_ending_promise")
    if isinstance(ep, dict) and ep:
        lines.append("[엔딩 약속 — 독자에게 주어야 할 정서]")
        lines.extend(_flat(ep, "  "))
        lines.append("")

    # ── 핵심 결정 사항 (구조·시점·포맷 LOCK) ──
    cd = ls.get("locked_core_decisions")
    if isinstance(cd, list) and cd:
        lines.append("[핵심 확정 결정 — 변경 불가]")
        for item in cd:
            if isinstance(item, dict):
                cat = str(item.get("category", "")).strip()
                rule = str(item.get("rule", "")).strip()
                rat = str(item.get("rationale", "")).strip()
                if rule:
                    lines.append(f"  ◆ [{cat}] {rule}")
                    if rat:
                        lines.append(f"      근거: {rat}")
            elif isinstance(item, str):
                lines.append(f"  ◆ {item.strip()}")
        lines.append("")

    # ── 비주얼 모티프 (소설 상징으로 전용) ──
    vm = ls.get("locked_visual_motifs")
    if isinstance(vm, list) and vm:
        lines.append("[모티프 — 소설의 반복 상징으로 전용할 것]")
        for item in vm:
            if isinstance(item, dict):
                m = str(item.get("motif", "")).strip()
                fn = str(item.get("function", "")).strip()
                if m:
                    lines.append(f"  - {m}")
                    if fn:
                        lines.append(f"      기능: {fn}")
            elif isinstance(item, str):
                lines.append(f"  - {item.strip()}")
        lines.append("")

    # ── 리스크 (소설화 시 보강 지점) ──
    rk = ls.get("locked_risks_to_address")
    if isinstance(rk, list) and rk:
        lines.append("[해결해야 할 리스크 — 소설에서 반드시 보강]")
        for r in rk:
            lines.append(f"  - {str(r).strip()}")
        lines.append("")

    # ── 타겟 / 레퍼런스 ──
    tg = ls.get("locked_target")
    if isinstance(tg, dict) and tg:
        lines.append("[타겟 독자]")
        lines.extend(_flat(tg, "  "))
        lines.append("")

    rf = ls.get("locked_references")
    if isinstance(rf, list) and rf:
        lines.append("[레퍼런스 좌표]")
        for r in rf:
            lines.append(f"  - {str(r).strip()}")
        lines.append("")

    # ── executive_summary ──
    es = idea_json.get("executive_summary")
    if isinstance(es, dict) and es:
        lines.append("[기획 요약]")
        lines.extend(_flat(es, "  "))
        lines.append("")
    elif isinstance(es, str) and es.strip():
        lines.append("[기획 요약]")
        lines.append(f"  {es.strip()}")
        lines.append("")

    digest_text = "\n".join(lines).strip()

    # LOCKED 라인 (locked_* 중 서사 확정 항목)
    locked_lines: List[str] = []
    if ll:
        locked_lines.append(f"로그라인: {ll}")
    if isinstance(cd, list):
        for item in cd:
            if isinstance(item, dict) and item.get("rule"):
                locked_lines.append(f"[{item.get('category','')}] {item['rule']}")
    if isinstance(ef, dict):
        for k in ("type", "emotional_resolution", "final_image", "forbidden"):
            v = _s(ef, k)
            if v:
                locked_lines.append(f"엔딩({k}): {v}")

    return {
        "meta": {
            "title": title,
            "genre": genre,
            "format": fmt,
            "verdict": _s(idea_json, "_idea_engine_meta", "verdict"),
            "hook_score": _s(idea_json, "_idea_engine_meta", "hook_score"),
        },
        "digest_text": digest_text,
        "pending_items": collect_pending_items(idea_json),
        "locked_lines": locked_lines,
    }


# ─────────────────────────────────────
# 2단계 — 소설화 + 엔진 제안 프롬프트
# ─────────────────────────────────────
IDEA_TO_NOVEL_PROMPT = """당신은 BLUE JEANS NOVEL ENGINE v3.3의 'Idea 기획 → 소설화' 변환 모듈이다.
아래는 Idea Engine이 확정한 기획 씨앗(IdeaSeed)을 정돈한 것이다.
이를 장편 대중소설로 재창작하기 위한 Novel Engine STEP 1 입력 자료와
STEP 4 12 Unit 매핑 가이드를 추출하라.

★★★ 최우선 규칙 ★★★
출력은 반드시 순수 JSON 하나로만. 마크다운 코드블록(```) 금지.
설명문·서문·후기 일체 금지. 오직 JSON 객체 하나만.

★★★ 미결정 항목 처리 원칙 (가장 중요) ★★★
이 기획은 Idea 단계라 '아직 결정되지 않은 항목'이 남아 있다.
빈칸으로 남기지 마라. 엔진이 각 미결정에 대해 가장 타당한 선택을 **제안**하라.
단, 제안한 자리에는 반드시 다음 표식을 붙여라.

  [엔진 제안 — 작가 확정 필요]

예시:
  Need: 어머니가 겪은 가정폭력 목격에서 비롯된 불안형 애착 [엔진 제안 — 작가 확정 필요]

제안 선택 기준:
- 원본에 options가 주어졌으면 그것을 우선 검토하되, **반드시 하나만 골라야 하는 것은 아니다.**
  둘 이상을 결합하거나, 선택지를 포괄하는 상위 구조를 세우는 편이 서사적으로 더 강하면 그렇게 하라.
  (예: '아버지 부재'와 '어머니의 가정폭력 목격'은 배타적 선택지가 아니라
   '폭력 가정에서 어머니가 아버지를 쫓아냈고 그 관계 문법이 딸에게 대물림됐다'는
   하나의 구조로 통합될 수 있다. 이런 통합이 가능하면 통합을 우선하라.)
- 필요하면 원본에 없던 인물·설정을 새로 세워 미결정을 해소해도 좋다.
  단, 새로 세운 것에도 [엔진 제안 — 작가 확정 필요] 표식을 붙여라.
- 소설 매체 특성(내면 서술 가능, 시점 통제, 분량 여유)에 가장 잘 맞는 선택을 우선하라.
- 확정된 LOCKED 항목(엔딩·구조·시점)과 충돌하지 않는 선택이어야 한다.
- 선택한 이유를 한 구절로 덧붙여라. 작가가 판단을 검토할 수 있어야 한다.
원본에서 이미 확정된 항목에는 이 표식을 붙이지 마라. 확정과 제안은 반드시 구분되어야 한다.

★★★ 매체 전환 원칙 ★★★
이 기획은 영상(OTT 시리즈 등)을 전제로 쓰였다. 씬·컷·화(話)·러닝타임 같은
영상 단위를 그대로 옮기지 말고 소설 언어로 번역하라.
- 회차(N화) 단위 → 소설 Unit(권) 흐름으로 재배치
- 시각 연출·카메라 지시 → 인물의 지각·내면·서술로
- 비주얼 모티프 → 소설의 반복 상징·감각 이미지로
확정된 서사(인물 관계·사건·결말·테마)는 보존하되 표현 매체만 소설로 바꾼다.

★ 추출 원칙 ★

1. [로그라인 logline] — 한 문장 25자 이내. 인물·사건·결핍 응축.

2. [장르 genre] — 소설 시장 기준으로 재판단. 복합 장르면 2개까지.

3. [작품 개요 overview] — 로그라인·테마·훅·차별점·타겟을 연결된 산문으로.
   300~500자. 소설 독자 관점으로.

4. [캐릭터 characters] — ★원본에 캐릭터 프로필이 없다. 엔진이 구성하라.★
   로그라인·훅·펀치신·엔딩·빌런 구조로부터 주요 인물 4~6명을 추론해 설계하라.
   각 인물별로:
   * 이름(원본에 있으면 그대로, 없으면 제안) / 나이 / 직업
   * Goal(외적 욕망) / Need(내적 결핍)
   * 비밀 / 말투·화법 / 반복 습관
   * 변화(소설 끝에서 어떻게 달라지는가)
   1인당 6~10줄. 원본에 근거가 없는 항목에는 [엔진 제안 — 작가 확정 필요] 표식.

5. [줄거리 / 트리트먼트 synopsis] — 기승전결 4단으로.
   원본의 회차 구조·빌런 구조·펀치신·엔딩을 소설 서사 흐름으로 재배치.
   반드시 살릴 사건 "[핵심]" 표시. 각 단 200~400자.

6. [추가 메모 notes] — 소설화 시 주의점, 원본이 지적한 리스크의 소설적 해결 방향,
   모티프를 소설 상징으로 쓰는 방법, 그리고 ★미결정 항목에 대한 엔진 제안 요약★.
   400~600자.

7. [주인공 직업 profession_protagonist] — 1~2 단어. 없으면 "".

8. [적대자/주요 조연 직업 profession_antagonist] — 1~2 단어. 주인공과 같으면 "".

9. [시대 키 period_keys] — 해당하는 것만 배열로. 현대면 [].
   ["조선_전기","조선_중기","조선_후기","구한말","일제강점기_전기",
    "일제강점기_후기","해방정국","한국전쟁","개발독재기","민주화기"]

10. [LOCKED 블록 locked_text] — 변경 절대 불가 항목만. 줄 단위.
    원본 locked_* 확정 항목(엔딩 형태·금지 사항·핵심 구조·테마)을 반영.
    ★엔진이 제안한 항목은 여기 넣지 마라. LOCKED는 원본 확정만.★

11. [OPEN 블록 open_text] — 자유 창작 가능 영역. 줄 단위.
    캐릭터 외형·습관·내면 독백·감각 묘사·시간 확장·관계 디테일.
    ★미결정 항목은 여기에 "엔진 제안: OOO / 작가 확정 필요" 형태로 명시하라.★

12. [12 Unit 매핑 가이드 unit_mapping] — 원본 서사를 소설 12 Unit으로 재배치.
    각 Unit별로 unit_no(1~12) / function / source_scenes(반영할 원본 회차·비트) /
    reorder_note / expansion_needed / plant_payoff. 반드시 12개 전체.

★ JSON 스키마 (이 키명을 정확히) ★
{
  "logline": "string",
  "genre": "string",
  "overview": "string",
  "characters": "string",
  "synopsis": "string",
  "notes": "string",
  "profession_protagonist": "string",
  "profession_antagonist": "string",
  "period_keys": ["string", ...],
  "locked_text": "string",
  "open_text": "string",
  "unit_mapping": [
    {"unit_no": 1, "function": "string", "source_scenes": "string",
     "reorder_note": "string", "expansion_needed": "string", "plant_payoff": "string"}
  ]
}

[Idea Engine 기획 데이터]
{digest_text}

[★ 미결정 항목 — 엔진이 제안으로 채우고 [엔진 제안 — 작가 확정 필요] 표식을 붙일 것]
{pending_block}

[원본 LOCKED 확정 항목 — locked_text 생성에 반영]
{locked_block}

★ 반드시 유효한 JSON 하나만 출력. 마크다운 fence 금지. ★
""".strip()


# ─────────────────────────────────────
# 응답 텍스트 안전 추출 (v3.3.2)
# ─────────────────────────────────────
def _response_text(response) -> str:
    """Anthropic 응답에서 텍스트 블록만 골라 결합한다.

    adaptive thinking이 켜진 모델(Sonnet 5, Opus 4.8 등)은 응답의 첫 블록이
    ThinkingBlock일 수 있다. content[0].text로 접근하면
    'ThinkingBlock' object has no attribute 'text' 오류가 난다.
    따라서 type이 'text'인 블록만 수집한다.
    """
    if response is None or not getattr(response, "content", None):
        return ""
    parts = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            t = getattr(block, "text", "")
            if t:
                parts.append(t)
    if parts:
        return "\n".join(parts).strip()
    # 폴백 — type 속성이 없는 SDK 변형 대응
    for block in response.content:
        t = getattr(block, "text", None)
        if isinstance(t, str) and t.strip():
            return t.strip()
    return ""


def _call_with_streaming(client, model: str, max_tokens: int,
                         system: str, prompt: str):
    """Anthropic API 호출. 긴 응답을 위해 스트리밍을 사용한다. (v3.3.4)

    max_tokens가 크면 SDK가 'Streaming is required for operations that may
    take longer than 10 minutes' 오류로 non-streaming 호출을 거부한다.
    따라서 스트리밍으로 받아 누적한다.

    Returns:
        (raw_text, stop_reason)
    """
    # 1) 스트리밍 (권장 경로)
    try:
        text_parts = []
        with client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for chunk in stream.text_stream:
                text_parts.append(chunk)
            final = stream.get_final_message()
            stop_reason = getattr(final, "stop_reason", "") or ""
            joined = "".join(text_parts).strip()
            if joined:
                return joined, stop_reason
            # 스트림 텍스트가 비면 최종 메시지에서 재추출
            return (_response_text(final) or ""), stop_reason
    except (AttributeError, TypeError):
        pass  # 구버전 SDK — stream 미지원 또는 시그니처 불일치

    # 2) 폴백 — 일반 호출
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return (_response_text(response) or ""), (getattr(response, "stop_reason", "") or "")


# ─────────────────────────────────────
# JSON 파싱
# ─────────────────────────────────────
def _repair_truncated_json(text: str) -> str:
    """잘린 JSON을 복구 시도. (v3.3.3)

    max_tokens 상한에 걸려 응답이 중간에 끊기면 닫는 괄호가 없어 파싱이 실패한다.
    문자열 안쪽인지 판별하며 열린 괄호를 세고, 부족한 만큼 닫아준다.
    마지막 미완성 항목은 잘라낸다.
    """
    if not text:
        return text

    stack = []          # '{' 또는 '[' 스택
    in_str = False
    escaped = False
    last_safe = -1      # 마지막으로 값이 완결된 위치

    for i, ch in enumerate(text):
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch == '"':
            in_str = not in_str
            if not in_str:
                last_safe = i
            continue
        if in_str:
            continue
        if ch in "{[":
            stack.append(ch)
        elif ch in "}]":
            if stack:
                stack.pop()
            last_safe = i
        elif ch in ",":
            last_safe = i - 1 if last_safe < 0 else last_safe
        elif ch.isdigit() or ch in "eltruafsn.-+":
            last_safe = i

    if not stack and not in_str:
        return text  # 잘리지 않음

    body = text

    # 문자열 도중에 끊겼으면 그 미완성 쌍을 통째로 버린다.
    # 예: {"a":"완결", "b":"미완성 도중에 끊 → {"a":"완결"
    if in_str:
        # 마지막으로 열린 따옴표 위치를 찾아 그 앞의 쉼표까지 되돌린다
        depth_scan_escaped = False
        open_quote = -1
        scan_in_str = False
        for i, ch in enumerate(body):
            if depth_scan_escaped:
                depth_scan_escaped = False
                continue
            if ch == "\\":
                depth_scan_escaped = True
                continue
            if ch == '"':
                if not scan_in_str:
                    open_quote = i
                scan_in_str = not scan_in_str
        if open_quote > 0:
            head = body[:open_quote]
            # 그 앞의 쉼표(또는 여는 괄호)까지 잘라낸다
            cut = max(head.rfind(","), head.rfind("{"), head.rfind("["))
            if cut > 0:
                body = head[:cut] if head[cut] == "," else head[:cut + 1]
            else:
                body = head

    # 끝에 남은 쉼표·콜론·미완성 키 제거
    body = re.sub(r'[,:]\s*$', '', body.rstrip())
    body = re.sub(r',\s*"[^"]*$', '', body.rstrip())
    body = re.sub(r'[,:]\s*$', '', body.rstrip())

    # 남은 괄호를 역순으로 닫는다
    closers = {"{": "}", "[": "]"}
    tail = "".join(closers[c] for c in reversed(stack))
    return body + tail


def _extract_json_from_response(text: str) -> Optional[Dict[str, Any]]:
    """LLM 응답에서 JSON을 추출. 여러 단계로 관대하게 시도한다. (v3.3.3)"""
    if not text:
        return None

    # 1) 마크다운 fence 제거
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"```\s*$", "", cleaned.strip(), flags=re.MULTILINE)

    # 2) 직접 파싱
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 3) 첫 { ~ 마지막 } 구간
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = cleaned[start:end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
        # 3-b) 제어문자 완화 (문자열 안 raw 개행 등)
        try:
            return json.loads(candidate, strict=False)
        except json.JSONDecodeError:
            pass

    # 4) 잘린 JSON 복구 시도
    if start != -1:
        truncated = cleaned[start:]
        repaired = _repair_truncated_json(truncated)
        for parser_kw in ({}, {"strict": False}):
            try:
                return json.loads(repaired, **parser_kw)
            except json.JSONDecodeError:
                continue

    return None


# ─────────────────────────────────────
# 진입점
# ─────────────────────────────────────
def load_idea_json(file_bytes: bytes) -> Dict[str, Any]:
    """업로드된 Idea JSON 파일 바이트를 파싱."""
    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = file_bytes.decode("utf-8-sig")
        except Exception:
            return {"_error": "JSON 파일 인코딩을 읽지 못했습니다. UTF-8인지 확인하세요."}
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return {"_error": f"JSON 파싱 실패: {e}"}
    return data


def is_idea_json(data: Dict[str, Any]) -> bool:
    """이 JSON이 Idea Engine 출력인지 판별."""
    if not isinstance(data, dict):
        return False
    if isinstance(data.get("_idea_engine_meta"), dict):
        return True
    # 폴백 — locked_seed 구조가 있으면 Idea로 간주
    if isinstance(data.get("locked_seed"), dict):
        return True
    return False


def get_idea_meta(data: Dict[str, Any]) -> Dict[str, str]:
    """UI 미리보기용 메타 정보."""
    meta = data.get("_idea_engine_meta", {}) if isinstance(data.get("_idea_engine_meta"), dict) else {}
    ls = data.get("locked_seed", {}) if isinstance(data.get("locked_seed"), dict) else {}
    genre_raw = data.get("genre", "")
    genre = genre_raw if isinstance(genre_raw, str) and genre_raw else _s(ls, "locked_genre", "primary")
    return {
        "engine": "Idea Engine",
        "engine_version": str(meta.get("version", "")),
        "verdict": str(meta.get("verdict", "")),
        "hook_score": str(meta.get("hook_score", "")),
        "title": str(ls.get("title_kr", "") or data.get("title", "(제목 미정)")),
        "genre": genre,
        "format": _s(ls, "locked_format", "primary") or str(data.get("format", "")),
        "pending_count": str(len(collect_pending_items(data))),
    }


def extract_idea_fields(
    idea_json: Dict[str, Any],
    anthropic_client,
    model: str = "claude-sonnet-5",
    max_tokens: int = 32000,
) -> Dict[str, Any]:
    """Idea JSON → Novel Engine STEP 1 필드 (소설화 + 미결정 엔진 제안).

    출력 키는 scenario_extractor / creator_extractor 와 동일.
    """
    if not isinstance(idea_json, dict) or "_error" in idea_json:
        return {"_error": idea_json.get("_error", "유효하지 않은 Idea JSON입니다.")
                if isinstance(idea_json, dict) else "유효하지 않은 입력입니다."}

    if anthropic_client is None:
        return {"_error": "Anthropic 클라이언트가 설정되지 않았습니다."}

    digest = build_idea_digest(idea_json)
    digest_text = digest["digest_text"]
    if not digest_text.strip():
        return {"_error": "Idea JSON에서 서사 필드를 찾지 못했습니다. 구조를 확인하세요."}

    # 미결정 블록
    pending_items = digest["pending_items"]
    if pending_items:
        pl = []
        for i, item in enumerate(pending_items, 1):
            line = f"{i}. {item['question']}"
            if item.get("importance"):
                line += f"  (중요도: {item['importance']})"
            pl.append(line)
            if item.get("options"):
                for o in item["options"]:
                    pl.append(f"     · 선택지: {o}")
        pending_block = "\n".join(pl)
    else:
        pending_block = "(미결정 항목 없음 — 모든 항목이 확정 상태)"

    # LOCKED 블록
    locked_lines = digest["locked_lines"]
    if locked_lines:
        locked_block = "\n".join(f"- {x}" for x in locked_lines[:60])
    else:
        locked_block = "(명시된 LOCKED 항목 없음 — 엔딩·핵심 관계·핵심 설정을 스스로 판단해 지정)"

    MAX_DIGEST = 60000
    if len(digest_text) > MAX_DIGEST:
        digest_text = digest_text[:MAX_DIGEST] + "\n\n[...이하 생략...]"

    prompt = (
        IDEA_TO_NOVEL_PROMPT
        .replace("{digest_text}", digest_text)
        .replace("{pending_block}", pending_block)
        .replace("{locked_block}", locked_block)
    )

    try:
        raw_text, _stop_reason = _call_with_streaming(
            anthropic_client, model, max_tokens,
            "당신은 JSON만 출력하는 기획→소설 변환기다. 다른 텍스트 일체 금지.", prompt,
        )
    except Exception as e:
        return {"_error": f"Anthropic API 호출 실패: {str(e)}"}

    parsed = _extract_json_from_response(raw_text)
    if parsed is None:
        _hint = ""
        if _stop_reason == "max_tokens":
            _hint = (" 응답이 최대 토큰에 도달해 잘렸습니다. "
                     "입력 자료가 매우 길 때 발생합니다.")
        elif not raw_text.strip():
            _hint = " 모델이 빈 응답을 반환했습니다."
        elif "{" not in raw_text:
            _hint = " 응답에 JSON 구조가 전혀 없습니다. 모델이 설명문만 출력했을 수 있습니다."
        return {
            "_error": (f"JSON 파싱 실패. 응답에서 유효한 JSON을 찾지 못했습니다.{_hint}"),
            "_raw_response": raw_text[:3000],
            "_diagnostic": {
                "응답_길이": f"{len(raw_text):,}자",
                "중단_사유": _stop_reason or "(없음)",
                "JSON_시작_포함": "{" in raw_text,
                "JSON_종료_포함": "}" in raw_text,
                "응답_끝_50자": raw_text[-50:] if raw_text else "(빈 응답)",
            },
        }

    defaults = {
        "logline": "",
        "genre": digest["meta"].get("genre", ""),
        "overview": "",
        "characters": "",
        "synopsis": "",
        "notes": "",
        "profession_protagonist": "",
        "profession_antagonist": "",
        "period_keys": [],
        "locked_text": "",
        "open_text": "",
        "unit_mapping": [],
    }
    for k, default in defaults.items():
        if k not in parsed or parsed[k] is None:
            parsed[k] = default

    # 출처 표식 + 미결정 정보 (UI 표시용)
    parsed["_source"] = "idea_engine"
    parsed["_source_title"] = digest["meta"].get("title", "")
    parsed["_source_format"] = digest["meta"].get("format", "")
    parsed["_pending_items"] = [it["question"] for it in pending_items]

    return parsed


# ─────────────────────────────────────
# VERSION INFO
# ─────────────────────────────────────
IDEA_EXTRACTOR_VERSION = "v3.3.0"
IDEA_EXTRACTOR_BUILD_DATE = "2026-07-23"
