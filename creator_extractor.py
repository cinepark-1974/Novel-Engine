"""
creator_extractor.py — Creator Engine JSON → 소설화 변환 모듈 (Novel Engine v3.2)
================================================================================

Creator Engine(v2.5.x)이 출력한 영상 기획 JSON(영화/시리즈 format)을 받아,
Novel Engine STEP 1 입력 자료(12개 필드)로 변환한다.

설계 원칙
---------
1. Creator JSON은 항상 영상물(영화/시리즈) format으로만 존재한다.
   따라서 영상 언어(씬·지문·연출·트리트먼트)를 소설 언어로 "번역"하는
   LLM 재가공 단계가 반드시 필요하다.
2. 출력 딕셔너리의 키 구조는 scenario_extractor.extract_scenario_fields()와
   완전히 동일하다. 그래야 main.py STEP 1이 코드 수정 없이 그대로 읽는다.
   (logline/genre/overview/characters/synopsis/notes/
    profession_protagonist/profession_antagonist/period_keys/
    locked_text/open_text/unit_mapping)
3. "최대 보존" 방침 — char_bible의 말투·대사·관계·아크, structure_story,
   three_act, tone_doc까지 최대한 소설 재료로 살린다.

처리 흐름
---------
extract_creator_fields(creator_json, client)
  ├─ 1단계 build_creator_digest(): 파이썬으로 JSON에서 서사 필드만 뽑아
  │                                정돈된 텍스트로 압축 (영상 전용 필드 선별)
  └─ 2단계 LLM 호출: digest를 소설 언어로 번역 + 12키 구조로 추출

이 모듈은 Creator JSON 구조에 의존하므로 실제 샘플(상속/클레어)로 검증했다.
"""

import json
import re
from typing import Any, Dict, List, Optional


# ─────────────────────────────────────
# 안전 접근 헬퍼
# ─────────────────────────────────────
def _s(obj: Any, *keys, default: str = "") -> str:
    """중첩 dict에서 문자열을 안전하게 꺼낸다. 없으면 default."""
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


def _join_list(items: Any, sep: str = " / ", limit: Optional[int] = None) -> str:
    """리스트를 문자열로 결합. dict 항목은 대표 값을 추출."""
    if not isinstance(items, list):
        return ""
    out = []
    for it in items:
        if isinstance(it, str):
            out.append(it.strip())
        elif isinstance(it, dict):
            # dict면 주요 값 하나를 골라 표현
            for key in ("label", "name", "text", "value", "item", "motif", "rule"):
                if it.get(key):
                    out.append(str(it[key]).strip())
                    break
    if limit:
        out = out[:limit]
    return sep.join(x for x in out if x)


# ─────────────────────────────────────
# 1단계 — Creator JSON → 서사 다이제스트 텍스트
# ─────────────────────────────────────
def build_creator_digest(creator_json: Dict[str, Any]) -> Dict[str, Any]:
    """Creator JSON에서 소설화에 필요한 서사 필드만 뽑아 정돈된 텍스트로 만든다.

    영상 전용 필드(scene_design.key_scenes, treatment, visual_style,
    music_sound, reference_films)는 소설에 직접 쓰지 않으므로 제외하되,
    tone_doc의 dialogue_rules·motifs·emotion_chain 등 소설 문체에
    전용 가능한 부분은 남긴다.

    Returns:
        {
          "meta": {...},        # 제목/장르/format 등 확정 메타
          "digest_text": "...", # LLM에 넘길 정돈된 서사 텍스트
          "locked_items": [...] # 원본 locked (LOCKED 블록 생성용)
        }
    """
    p = creator_json.get("project", {})
    if not isinstance(p, dict):
        p = {}

    core = p.get("core", {}) if isinstance(p.get("core"), dict) else {}
    char_bible = p.get("char_bible", {}) if isinstance(p.get("char_bible"), dict) else {}
    structure_story = p.get("structure_story", {}) if isinstance(p.get("structure_story"), dict) else {}
    structure_diag = p.get("structure_diag", {}) if isinstance(p.get("structure_diag"), dict) else {}
    tone_doc = p.get("tone_doc", {}) if isinstance(p.get("tone_doc"), dict) else {}

    lines: List[str] = []

    # ── 기본 메타 ──
    title = _s(p, "title")
    genre = _s(p, "genre")
    fmt = _s(p, "format")
    idea_text = _s(p, "idea_text")

    lines.append(f"[작품 제목] {title}")
    lines.append(f"[원본 장르] {genre}")
    lines.append(f"[원본 매체] {fmt}  ← 이 기획은 영상용이다. 소설로 전환해야 한다.")
    if idea_text:
        lines.append(f"[최초 아이디어] {idea_text}")
    lines.append("")

    # ── 로그라인 팩 ──
    lp = core.get("logline_pack", {})
    if isinstance(lp, dict):
        lines.append("[로그라인]")
        for k in ("original", "washed", "투자자용", "감독용", "캐릭터훅", "character_hook"):
            v = _s(lp, k)
            if v:
                lines.append(f"  - {v}")
        lines.append("")

    # ── 기획의도 ──
    pi = core.get("project_intent", {})
    if isinstance(pi, dict):
        lines.append("[기획의도]")
        for k in ("subject", "genre_appeal", "market", "theme", "pitch", "differentiation"):
            v = _s(pi, k)
            if v:
                lines.append(f"  - {k}: {v}")
        lines.append("")

    # ── Goal / Need / Strategy ──
    gns = core.get("goal_need_strategy", {})
    if isinstance(gns, dict):
        lines.append("[드라마 구조 — Goal/Need/Strategy]")
        for k in ("goal", "need", "strategy", "risk", "ending_payoff"):
            v = _s(gns, k)
            if v:
                lines.append(f"  - {k}: {v}")
        lines.append("")

    # ── 서사 동력 ──
    nd = core.get("narrative_drive", {})
    if isinstance(nd, dict):
        lines.append("[서사 동력]")
        for k, v in nd.items():
            sv = _s(nd, k)
            if sv:
                lines.append(f"  - {k}: {sv}")
        lines.append("")

    # ── 세계관 ──
    wb = core.get("world_build", {})
    if isinstance(wb, dict):
        lines.append("[세계관]")
        for k in ("time", "space", "rules", "taboo", "power_structure"):
            v = _s(wb, k)
            if v:
                lines.append(f"  - {k}: {v}")
        # 한글 키도 시도
        for k in ("시간", "공간", "규칙", "금기", "권력구조"):
            v = _s(wb, k)
            if v:
                lines.append(f"  - {k}: {v}")
        lines.append("")

    # ── 캐릭터 바이블 (최대 보존의 핵심) ──
    chars = char_bible.get("characters", []) if isinstance(char_bible, dict) else []
    if not chars:
        chars = core.get("characters", [])  # 폴백
    if isinstance(chars, list) and chars:
        lines.append("[캐릭터 바이블 — 전원]")
        for c in chars:
            if not isinstance(c, dict):
                continue
            name = _s(c, "name")
            role = _s(c, "role")
            age = _s(c, "age")
            lines.append(f"◆ {name} ({role}, {age})")
            for label, key in (
                ("외형", "appearance"), ("직업", "occupation"),
                ("욕망/목표", "goal"), ("결핍/필요", "need"),
                ("결함", "flaw"), ("배경", "backstory"),
                ("비밀", "secret"), ("신념", "belief"), ("두려움", "fear"),
                ("전술", "tactics"), ("습관", "habits"),
                ("말투", "speech_pattern"), ("대사톤", "dialogue_tone"),
                ("아크", "arc_detail"),
            ):
                v = c.get(key)
                if isinstance(v, list):
                    v = _join_list(v, sep=" | ")
                elif v is not None:
                    v = str(v).strip()
                if v:
                    lines.append(f"    - {label}: {v}")
            # 대표 대사
            sl = c.get("sample_lines")
            if isinstance(sl, list) and sl:
                lines.append(f"    - 대표대사: {_join_list(sl, sep='  //  ', limit=3)}")
            elif isinstance(sl, str) and sl.strip():
                lines.append(f"    - 대표대사: {sl.strip()}")
            # 관계
            ra = c.get("relationship_attitudes")
            if isinstance(ra, list) and ra:
                lines.append(f"    - 관계: {_join_list(ra, sep=' | ')}")
            elif isinstance(ra, str) and ra.strip():
                lines.append(f"    - 관계: {ra.strip()}")
        lines.append("")

    # ── 관계도 ──
    rmap = core.get("relationship_map", [])
    if isinstance(rmap, list) and rmap:
        lines.append("[관계도]")
        for r in rmap:
            if isinstance(r, dict):
                a = _s(r, "from") or _s(r, "a") or _s(r, "char_a")
                b = _s(r, "to") or _s(r, "b") or _s(r, "char_b")
                rel = _s(r, "relation") or _s(r, "description") or _s(r, "note")
                if a and b:
                    lines.append(f"  - {a} → {b}: {rel}")
                elif rel:
                    lines.append(f"  - {rel}")
            elif isinstance(r, str):
                lines.append(f"  - {r}")
        lines.append("")

    # ── 시놉시스 1p ──
    syn = structure_story.get("synopsis_1p", {})
    if isinstance(syn, dict):
        lines.append("[시놉시스]")
        for k in ("opening", "catalyst", "development", "midpoint", "crisis", "climax", "resolution", "ending"):
            v = _s(syn, k)
            if v:
                lines.append(f"  - {k}: {v}")
        lines.append("")
    elif isinstance(syn, str) and syn.strip():
        lines.append("[시놉시스]")
        lines.append(f"  {syn.strip()}")
        lines.append("")

    # ── 스토리라인 (시퀀스) ──
    storyline = structure_story.get("storyline", [])
    if isinstance(storyline, list) and storyline:
        lines.append("[스토리라인 시퀀스]")
        for seq in storyline:
            if not isinstance(seq, dict):
                continue
            n = seq.get("seq", "?")
            label = _s(seq, "label")
            summary = _s(seq, "summary")
            conflict = _s(seq, "conflict")
            emotion = _s(seq, "emotion")
            line = f"  {n}. [{label}] {summary}"
            if conflict:
                line += f" / 갈등: {conflict}"
            if emotion:
                line += f" / 감정: {emotion}"
            lines.append(line)
        lines.append("")

    # ── 3막 구조 ──
    ta = structure_diag.get("three_act", {})
    if isinstance(ta, dict):
        lines.append("[3막 전환점]")
        for k in ("act1_end", "act2_midpoint", "act2_end", "act3_climax", "resolution"):
            v = _s(ta, k)
            if v:
                lines.append(f"  - {k}: {v}")
        lines.append("")

    # ── Plant/Payoff ──
    pp = structure_diag.get("planting_payoff", [])
    if isinstance(pp, list) and pp:
        lines.append("[복선-회수 Plant/Payoff]")
        for item in pp:
            if isinstance(item, dict):
                plant = _s(item, "plant") or _s(item, "설정")
                payoff = _s(item, "payoff") or _s(item, "회수")
                if plant or payoff:
                    lines.append(f"  - 심기: {plant} → 회수: {payoff}")
            elif isinstance(item, str):
                lines.append(f"  - {item}")
        lines.append("")

    # ── 캐릭터 아크 ──
    ca = structure_diag.get("character_arcs", [])
    if isinstance(ca, list) and ca:
        lines.append("[캐릭터 아크]")
        for a in ca:
            if isinstance(a, dict):
                nm = _s(a, "name") or _s(a, "character")
                arc = _s(a, "arc") or _s(a, "description") or _s(a, "change")
                if nm or arc:
                    lines.append(f"  - {nm}: {arc}")
            elif isinstance(a, str):
                lines.append(f"  - {a}")
        lines.append("")

    # ── tone_doc 중 소설 전용 가능 부분 (문체 재료) ──
    lines.append("[문체·톤 재료 — 소설 문체로 재해석할 것]")
    dr = tone_doc.get("dialogue_rules", {})
    if isinstance(dr, dict):
        ot = _s(dr, "overall_tone")
        if ot:
            lines.append(f"  - 대사 규칙: {ot}")
    elif isinstance(dr, str) and dr.strip():
        lines.append(f"  - 대사 규칙: {dr.strip()}")
    wi = _s(tone_doc, "writer_instruction")
    if wi:
        lines.append(f"  - 작가 지시(영상용, 소설로 번역 필요): {wi}")
    motifs = tone_doc.get("motifs", {})
    if isinstance(motifs, dict):
        mv = _join_list(list(motifs.values()), sep=" | ") if motifs else ""
        if mv:
            lines.append(f"  - 모티프: {mv}")
    elif isinstance(motifs, list):
        mv = _join_list(motifs, sep=" | ")
        if mv:
            lines.append(f"  - 모티프: {mv}")
    ec = tone_doc.get("emotion_chain", {})
    if isinstance(ec, dict) and ec:
        lines.append(f"  - 감정 연쇄: {_join_list(list(ec.values()), sep=' → ') or json.dumps(ec, ensure_ascii=False)[:300]}")
    guard = tone_doc.get("tone_guardrail", {})
    if isinstance(guard, dict) and guard:
        gv = _join_list(list(guard.values()), sep=" | ")
        if gv:
            lines.append(f"  - 톤 가드레일: {gv}")
    lines.append("")

    digest_text = "\n".join(lines).strip()

    return {
        "meta": {
            "title": title,
            "genre": genre,
            "format": fmt,
        },
        "digest_text": digest_text,
        "locked_items": p.get("locked_items", []) if isinstance(p.get("locked_items"), list) else [],
    }


# ─────────────────────────────────────
# 2단계 — 소설화 번역 프롬프트
# ─────────────────────────────────────
CREATOR_TO_NOVEL_PROMPT = """당신은 BLUE JEANS NOVEL ENGINE v3.2의 '영상 기획 → 소설화' 변환 모듈이다.
아래는 Creator Engine이 영화/시리즈용으로 확정한 기획 데이터를 정돈한 것이다.
이 영상 기획을 장편 대중소설로 재창작하기 위한 Novel Engine STEP 1 입력 자료와
STEP 4 12 Unit 매핑 가이드를 추출하라.

★★★ 최우선 규칙 ★★★
출력은 반드시 순수 JSON 하나로만. 마크다운 코드블록(```) 금지.
설명문·서문·후기 일체 금지. 오직 JSON 객체 하나만.

★★★ 매체 전환 원칙 (가장 중요) ★★★
이 기획은 '영상용'으로 쓰였다. 씬·컷·지문·카메라·스크린 같은 영상 언어를
그대로 옮기지 말고, 반드시 '소설 언어'로 번역하라.
- 영상의 시각 연출("LED 스크린에 신호가 송출된다") → 소설의 서술·인물 지각으로
- 영상의 지문 지시("볼펜 상태를 지문에 명시하라") → 인물의 습관·내면 묘사 원칙으로
- 대사 규칙·톤은 소설 문장의 리듬·호칭·서술 태도로 재해석
확정된 서사(인물·관계·사건·결말)는 보존하되, 표현 매체만 소설로 바꾼다.

★ 추출 원칙 ★

1. [로그라인 logline] — 한 문장 25자 이내. 인물·사건·결핍 응축.

2. [장르 genre] — 소설 시장 기준으로 재판단. 복합 장르면 2개까지.

3. [작품 개요 overview] — 로그라인·기획의도·세계관·핵심질문·차별점을
   연결된 산문으로. 300~500자. 소설 독자 관점으로.

4. [캐릭터 characters] — 캐릭터 바이블을 최대한 보존하되 소설 언어로.
   주요 인물 전원. 각 인물별로:
   * 이름 / 나이 / 직업
   * Goal(외적 욕망) / Need(내적 결핍)
   * 비밀 / 말투·화법(소설 대사에 쓸 수 있게) / 반복 습관
   * 변화(소설 끝에서 어떻게 달라지는가)
   1인당 6~10줄. 원본의 말투·대사·관계 디테일을 아끼지 말고 살려라.

5. [줄거리 / 트리트먼트 synopsis] — 기승전결 4단으로.
   영상 시퀀스를 소설 서사 흐름으로 재배치. 반드시 살릴 사건 "[핵심]" 표시.
   각 단 200~400자.

6. [추가 메모 notes] — 소설화 시 주의점, 영상→소설 전환에서 확장·보강할 지점,
   문체 재료(대사 규칙·모티프·감정 연쇄를 소설 문체 지침으로 정리). 300~500자.

7. [주인공 직업 profession_protagonist] — 1~2 단어. 없으면 "".

8. [적대자/주요 조연 직업 profession_antagonist] — 1~2 단어. 주인공과 같으면 "".

9. [시대 키 period_keys] — 해당하는 것만 배열로. 현대면 [].
   ["조선_전기","조선_중기","조선_후기","구한말","일제강점기_전기",
    "일제강점기_후기","해방정국","한국전쟁","개발독재기","민주화기"]

10. [LOCKED 블록 locked_text] — 변경 절대 불가 항목. 줄 단위.
    엔딩·핵심 인물 관계·핵심 설정·기획의도 필수. 원본 locked_items를 반영.

11. [OPEN 블록 open_text] — 자유 창작 가능 영역. 줄 단위.
    캐릭터 외형·습관·내면 독백·감각 묘사·시간 확장·관계 디테일.

12. [12 Unit 매핑 가이드 unit_mapping] — 영상 서사를 소설 12 Unit으로 재배치.
    각 Unit별로 unit_no(1~12) / function(서사 기능) /
    source_scenes(반영할 원본 시퀀스·비트) / reorder_note(순서 재배치) /
    expansion_needed(소설에 필요한 확장) / plant_payoff(심기/회수).
    반드시 12개 전체.

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

[Creator Engine 영상 기획 데이터]
{digest_text}

[원본 LOCKED 항목 목록 — locked_text 생성에 반드시 반영]
{locked_block}

★ 반드시 유효한 JSON 하나만 출력. 마크다운 fence 금지. ★
""".strip()


# ─────────────────────────────────────
# JSON 파싱 (scenario_extractor와 동일 로직)
# ─────────────────────────────────────
def _extract_json_from_response(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"```\s*$", "", cleaned.strip(), flags=re.MULTILINE)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(cleaned[start:end + 1])
        except json.JSONDecodeError:
            pass
    return None


# ─────────────────────────────────────
# 메인 진입점
# ─────────────────────────────────────
def load_creator_json(file_bytes: bytes) -> Dict[str, Any]:
    """업로드된 Creator JSON 파일 바이트를 파싱. 실패 시 _error 포함."""
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


def is_creator_json(data: Dict[str, Any]) -> bool:
    """이 JSON이 Creator Engine 출력인지 판별."""
    if not isinstance(data, dict):
        return False
    meta = data.get("_meta", {})
    if isinstance(meta, dict) and "Creator Engine" in str(meta.get("blue_jeans_engine", "")):
        return True
    # 폴백 — project.core + char_bible 구조가 있으면 Creator로 간주
    p = data.get("project", {})
    if isinstance(p, dict) and isinstance(p.get("core"), dict) and "char_bible" in p:
        return True
    return False


def get_creator_meta(data: Dict[str, Any]) -> Dict[str, str]:
    """UI 미리보기용 메타 정보 추출."""
    meta = data.get("_meta", {}) if isinstance(data.get("_meta"), dict) else {}
    p = data.get("project", {}) if isinstance(data.get("project"), dict) else {}
    return {
        "engine": str(meta.get("blue_jeans_engine", "")),
        "engine_version": str(meta.get("engine_version", "")),
        "stage": str(meta.get("stage", "") or p.get("stage", "")),
        "title": str(p.get("title", "(제목 미정)")),
        "genre": str(p.get("genre", "")),
        "format": str(p.get("format", "")),
        "final_score": str(p.get("final_score", "")),
        "char_count": str(len(p.get("char_bible", {}).get("characters", []))
                          if isinstance(p.get("char_bible"), dict) else 0),
    }


def extract_creator_fields(
    creator_json: Dict[str, Any],
    anthropic_client,
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 8192,
) -> Dict[str, Any]:
    """Creator JSON → Novel Engine STEP 1 필드 (소설화 번역).

    출력 딕셔너리 키는 scenario_extractor.extract_scenario_fields()와 동일.

    Args:
        creator_json: load_creator_json()이 반환한 dict
        anthropic_client: anthropic.Anthropic 인스턴스
        model: Sonnet 모델명
        max_tokens: 최대 토큰

    Returns:
        12키 딕셔너리. 실패 시 "_error" 포함.
    """
    if not isinstance(creator_json, dict) or "_error" in creator_json:
        return {"_error": creator_json.get("_error", "유효하지 않은 Creator JSON입니다.")
                if isinstance(creator_json, dict) else "유효하지 않은 입력입니다."}

    if anthropic_client is None:
        return {"_error": "Anthropic 클라이언트가 설정되지 않았습니다."}

    # 1단계 — 다이제스트
    digest = build_creator_digest(creator_json)
    digest_text = digest["digest_text"]
    if not digest_text.strip():
        return {"_error": "Creator JSON에서 서사 필드를 찾지 못했습니다. 구조를 확인하세요."}

    # LOCKED 항목 텍스트
    locked_items = digest["locked_items"]
    if locked_items:
        locked_block = "\n".join(f"- {str(x).strip()}" for x in locked_items[:60])
    else:
        locked_block = "(원본에 명시된 LOCKED 항목 없음 — 엔딩·핵심 관계·핵심 설정을 스스로 판단해 LOCKED로 지정)"

    # 입력 과다 방지
    MAX_DIGEST = 60000
    if len(digest_text) > MAX_DIGEST:
        digest_text = digest_text[:MAX_DIGEST] + "\n\n[...이하 생략...]"

    prompt = (
        CREATOR_TO_NOVEL_PROMPT
        .replace("{digest_text}", digest_text)
        .replace("{locked_block}", locked_block)
    )

    # 2단계 — LLM 호출
    try:
        response = anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system="당신은 JSON만 출력하는 영상→소설 변환기다. 다른 텍스트 일체 금지.",
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = response.content[0].text if response.content else ""
    except Exception as e:
        return {"_error": f"Anthropic API 호출 실패: {str(e)}"}

    parsed = _extract_json_from_response(raw_text)
    if parsed is None:
        return {
            "_error": "JSON 파싱 실패. 응답에서 유효한 JSON을 찾지 못했습니다.",
            "_raw_response": raw_text[:2000],
        }

    # 기본값 채우기 (scenario_extractor와 동일 키)
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

    # 출처 표식 (디버깅·미리보기용, STEP 1은 무시)
    parsed["_source"] = "creator_engine"
    parsed["_source_title"] = digest["meta"].get("title", "")
    parsed["_source_format"] = digest["meta"].get("format", "")

    return parsed


# ─────────────────────────────────────
# VERSION INFO
# ─────────────────────────────────────
CREATOR_EXTRACTOR_VERSION = "v3.2.0"
CREATOR_EXTRACTOR_BUILD_DATE = "2026-07-21"
