"""
👖 BLUE JEANS NOVEL ENGINE v3.1 — scenario_extractor.py
────────────────────────────────────────────────────────────
시나리오 파일을 읽어서 Novel Engine STEP 1 입력 필드와
STEP 4 12 Unit 매핑 가이드를 자동 추출하는 모듈.

입력: .docx / .txt / 붙여넣기 텍스트
출력: dict {
    'logline', 'genre', 'overview', 'characters', 'synopsis',
    'notes', 'locked_text', 'open_text', 'profession_protagonist',
    'profession_antagonist', 'period_keys', 'unit_mapping'
}

Sonnet API를 사용하여 1회 호출로 전체 필드를 추출한다.
────────────────────────────────────────────────────────────
"""

import re
import json
from typing import Optional, Dict, Any, List


# ─────────────────────────────────────
# DOCX 텍스트 추출
# ─────────────────────────────────────
def extract_text_from_docx(file_bytes: bytes) -> str:
    """업로드된 DOCX 파일 바이트 → 순수 텍스트 추출."""
    try:
        from io import BytesIO
        from docx import Document
        doc = Document(BytesIO(file_bytes))
        paragraphs = []
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                paragraphs.append(text)
        return "\n".join(paragraphs)
    except Exception as e:
        return ""


def extract_text_from_txt(file_bytes: bytes) -> str:
    """업로드된 TXT 파일 바이트 → 텍스트 추출."""
    for enc in ["utf-8", "utf-8-sig", "cp949", "euc-kr", "utf-16"]:
        try:
            return file_bytes.decode(enc)
        except UnicodeDecodeError:
            continue
    return ""


# ─────────────────────────────────────
# 시나리오 구조 분석 (추출 전 통계)
# ─────────────────────────────────────
def analyze_scenario_structure(text: str) -> Dict[str, Any]:
    """시나리오의 기본 구조 통계를 반환.
    - 총 글자 수, 문단 수, 추정 씬 수, V.O/CUT 지시 개수 등.
    """
    if not text or not text.strip():
        return {
            "char_count": 0, "paragraph_count": 0, "scene_count": 0,
            "vo_count": 0, "cut_count": 0, "flashback_count": 0,
        }

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    char_count = len(text)
    paragraph_count = len(lines)

    # 씬 헤더 패턴: "장소, 시간대" 형식 (오후/밤/낮/아침/저녁/새벽/오전)
    scene_pattern = re.compile(r",\s*(오후|밤|낮|아침|저녁|새벽|오전)$")
    scene_count = sum(1 for l in lines if len(l) < 60 and scene_pattern.search(l))

    # 시나리오 전용 지시 문법
    vo_count = sum(1 for l in lines if re.search(r"V\.O|\(V\.O\.?\)|보이스오버", l))
    cut_count = sum(1 for l in lines if re.search(r"CUT\s*TO|C\.U|F\.I|F\.O|DISSOLVE", l, re.IGNORECASE))
    flashback_count = sum(1 for l in lines if "(회상)" in l or "회상)" in l or "플래시백" in l.lower())

    return {
        "char_count": char_count,
        "paragraph_count": paragraph_count,
        "scene_count": scene_count,
        "vo_count": vo_count,
        "cut_count": cut_count,
        "flashback_count": flashback_count,
    }


# ─────────────────────────────────────
# 추출 프롬프트 (Sonnet 전용)
# ─────────────────────────────────────
SCENARIO_EXTRACTION_PROMPT = """당신은 BLUE JEANS NOVEL ENGINE v3.1의 시나리오 분석 모듈이다.
아래에 주어진 시나리오를 읽고, 이를 장편 대중소설로 재창작하기 위한
Novel Engine STEP 1 입력 자료와 STEP 4 12 Unit 매핑 가이드를 추출하라.

★★★ 최우선 규칙 ★★★
출력은 반드시 순수 JSON 형식 하나로만. 마크다운 코드블록(```) 감싸지 마라.
설명문, 서문, 후기 일체 금지. 오직 JSON 객체 하나만 출력한다.

★ 추출 원칙 ★

1. [로그라인 logline]
   - 한 문장. 25자 이내. 인물·사건·결핍을 응축.
   - 예: "생존자 마을에서 첫 살인사건의 누명을 쓴 남자의 추방."

2. [장르 genre]
   - 시나리오의 본질을 판단. 복합 장르면 2개까지.
   - 예: "SF 스릴러", "포스트 아포칼립스 드라마", "금융 스릴러 + 로맨스"

3. [작품 개요 overview]
   - 로그라인, 기획의도, 세계관, 장르 톤, 핵심 질문, 차별점을 연결된 산문으로.
   - 300~500자.

4. [캐릭터 characters]
   - 주요 인물 4~8명. 각 인물별로:
     * 이름 (시나리오 그대로) / 나이 / 직업
     * Goal (외적 욕망)
     * Need (내적 결핍, 자기 자신도 모를 수 있는)
     * 비밀 (다른 인물이 모르는 것)
     * 변화 (소설 끝에서 이 인물이 어떻게 달라져야 하는가)
   - 1인당 5~8줄.

5. [줄거리 / 트리트먼트 synopsis]
   - 기승전결 4단 구조로 분할된 전체 줄거리.
   - 시나리오 사건 순서 그대로가 아니라, 소설로 옮길 때 적합한 순서로.
   - 반드시 살릴 사건·장면을 "[핵심]" 표시.
   - 각 단 200~400자.

6. [추가 메모 notes]
   - 약한 부분, 엔진이 강화해야 할 지점, 작가가 주의할 점, 정보 레이어 메모.
   - 200~300자.

7. [주인공 직업 profession_protagonist]
   - 시나리오에서 주인공의 직업을 1~2 단어로.
   - 없거나 불명확하면 빈 문자열.

8. [적대자/주요 조연 직업 profession_antagonist]
   - 시나리오에서 적대자나 주요 조연의 직업을 1~2 단어로.
   - 주인공과 같으면 빈 문자열.

9. [시대 키 period_keys]
   - 다음 중 해당하는 시대 키만 배열로. 없으면 빈 배열.
   - ["조선_전기", "조선_중기", "조선_후기", "구한말", "일제강점기_전기",
      "일제강점기_후기", "해방정국", "한국전쟁", "개발독재기", "민주화기"]
   - 현대 배경(2000년대~현재)이면 빈 배열 []

10. [LOCKED 블록 locked_text]
    - 시나리오에서 변경 절대 불가 항목만. 줄 단위 목록.
    - 엔딩 결말, 핵심 인물 관계, 핵심 설정, 기획의도 필수.
    - 예: "- 주인공 석현은 Chapter 12에서 마을에서 추방된다."

11. [OPEN 블록 open_text]
    - 자유롭게 창작·확장 가능한 영역. 줄 단위 목록.
    - 캐릭터 외형, 습관, 내면 독백, 감각 묘사, 시간 확장, 관계 디테일.

12. [12 Unit 매핑 가이드 unit_mapping]
    - 시나리오를 소설 12 Unit 구조로 재배치한 가이드.
    - 각 Unit별로:
      * unit_no (1~12)
      * 서사 기능 (예: "Chapter 1 PEAK — 마을의 평온, 석현의 정상")
      * 반영할 시나리오 씬 (시나리오 씬 번호 또는 설명)
      * 순서 재배치 지시 (필요한 경우만)
      * 확장 필요 영역 (시나리오에 없지만 소설에 필요한 것)
      * Plant/Payoff 후보 (이 Unit에서 심을 것 / 회수할 것)
    - 반드시 12개 전체.

★ 특수 처리 규칙 ★
- 시나리오의 V.O, CUT TO, C.U, 괄호 지시문은 모두 무시하고 서사의 뼈대만 읽어라.
- "(회상)" 씬은 소설에서는 자연스러운 시간 흐름 또는 인물 내면으로 재배치하라.
- 액션 지문(배경 묘사, 인물 등장)을 인물의 감각·내면으로 전환할 가능성을 매핑 가이드에 반영하라.
- 시나리오의 엔딩(마지막 씬)은 LOCKED로 반드시 보호하라.

★ JSON 스키마 (이 키명을 정확히 사용) ★
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
    {
      "unit_no": 1,
      "function": "string",
      "source_scenes": "string",
      "reorder_note": "string",
      "expansion_needed": "string",
      "plant_payoff": "string"
    }
  ]
}

[시나리오 원문]
{scenario_text}

★ 반드시 유효한 JSON 하나만 출력. 마크다운 fence 금지. ★
""".strip()


# ─────────────────────────────────────
# JSON 파싱 (관대한 파서)
# ─────────────────────────────────────
def _extract_json_from_response(text: str) -> Optional[Dict[str, Any]]:
    """LLM 응답에서 JSON 블록을 찾아 파싱.
    - 마크다운 코드블록으로 감싸여 있어도 처리.
    - 앞뒤 설명문이 있어도 첫 { 부터 마지막 } 까지 추출 시도.
    """
    if not text:
        return None

    # 1. 마크다운 fence 제거
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"```\s*$", "", cleaned.strip(), flags=re.MULTILINE)

    # 2. 직접 파싱 시도
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 3. 첫 { 부터 마지막 } 까지 추출
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(cleaned[start:end + 1])
        except json.JSONDecodeError:
            pass

    return None


# ─────────────────────────────────────
# 메인 추출 함수
# ─────────────────────────────────────
def extract_scenario_fields(
    scenario_text: str,
    anthropic_client,
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 8192,
) -> Dict[str, Any]:
    """시나리오 텍스트 → Novel Engine 입력 필드 자동 추출.

    Args:
        scenario_text: 시나리오 원문 (DOCX/TXT에서 추출된 순수 텍스트)
        anthropic_client: anthropic.Anthropic 클라이언트 인스턴스
        model: Sonnet 모델명
        max_tokens: 최대 토큰

    Returns:
        추출 결과 dict. 실패 시 "_error" 키 포함.
    """
    if not scenario_text or not scenario_text.strip():
        return {"_error": "시나리오 텍스트가 비어 있습니다."}

    if anthropic_client is None:
        return {"_error": "Anthropic 클라이언트가 설정되지 않았습니다."}

    # 시나리오가 너무 길면 헤드/테일로 자름 (안전장치)
    MAX_INPUT_CHARS = 120000
    if len(scenario_text) > MAX_INPUT_CHARS:
        head = scenario_text[:MAX_INPUT_CHARS // 2]
        tail = scenario_text[-MAX_INPUT_CHARS // 2:]
        scenario_text = f"{head}\n\n[...중략...]\n\n{tail}"

    # 프롬프트 조립 — {scenario_text} 치환만
    prompt = SCENARIO_EXTRACTION_PROMPT.replace("{scenario_text}", scenario_text)

    # Sonnet 호출
    try:
        response = anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system="당신은 JSON만 출력하는 추출기다. 다른 텍스트 일체 금지.",
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = response.content[0].text if response.content else ""
    except Exception as e:
        return {"_error": f"Anthropic API 호출 실패: {str(e)}"}

    # JSON 파싱
    parsed = _extract_json_from_response(raw_text)
    if parsed is None:
        return {
            "_error": "JSON 파싱 실패. 응답에서 유효한 JSON을 찾지 못했습니다.",
            "_raw_response": raw_text[:2000],
        }

    # 필수 키 검증 + 기본값 채우기
    defaults = {
        "logline": "",
        "genre": "",
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

    return parsed


# ─────────────────────────────────────
# Unit 매핑 → 프롬프트 텍스트 변환
# ─────────────────────────────────────
def build_unit_mapping_text(unit_mapping: List[Dict[str, Any]]) -> str:
    """12 Unit 매핑 가이드를 STEP 4 blueprint 프롬프트에 주입할 텍스트로 변환.

    Args:
        unit_mapping: [{unit_no, function, source_scenes, ...}, ...]

    Returns:
        프롬프트 삽입용 텍스트. 빈 리스트면 빈 문자열.
    """
    if not unit_mapping:
        return ""

    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "[시나리오 → 12 Unit 매핑 가이드 (v3.1 시나리오 소설화 모드)]",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        "이 작품은 기존 시나리오를 기반으로 소설화하는 작업이다.",
        "아래 매핑 가이드는 시나리오 씬과 소설 Unit의 대응 관계를 제안한다.",
        "각 Unit 설계 시 이 가이드를 참고하여 해당 Unit의 서사 기능과 반영할 시나리오 씬을 정확히 배치하라.",
        "단, 시나리오를 그대로 옮기지 말고 Novel Engine의 구조 원칙(BJND, Plant/Payoff, Reader Retention Curve 등)에 맞게 재구성하라.",
        "",
    ]

    for item in unit_mapping:
        unit_no = item.get("unit_no", "?")
        function = item.get("function", "")
        source_scenes = item.get("source_scenes", "")
        reorder_note = item.get("reorder_note", "")
        expansion_needed = item.get("expansion_needed", "")
        plant_payoff = item.get("plant_payoff", "")

        lines.append(f"[UNIT {unit_no:02d}] {function}" if isinstance(unit_no, int) else f"[UNIT {unit_no}] {function}")
        if source_scenes:
            lines.append(f"  - 반영할 시나리오 씬: {source_scenes}")
        if reorder_note:
            lines.append(f"  - 순서 재배치: {reorder_note}")
        if expansion_needed:
            lines.append(f"  - 확장 필요 영역: {expansion_needed}")
        if plant_payoff:
            lines.append(f"  - Plant/Payoff 후보: {plant_payoff}")
        lines.append("")

    lines.append("★ 위 매핑은 가이드이지 강제 지시가 아니다. Novel Engine 구조 원칙이 충돌할 경우 구조 원칙이 우선한다. ★")

    return "\n".join(lines)


# ─────────────────────────────────────
# VERSION INFO
# ─────────────────────────────────────
SCENARIO_EXTRACTOR_VERSION = "v3.1.0"
SCENARIO_EXTRACTOR_BUILD_DATE = "2026-04-24"
