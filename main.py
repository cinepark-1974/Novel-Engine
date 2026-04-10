import os
import re
from io import BytesIO
from typing import Optional, List

import streamlit as st

try:
    import anthropic
except ImportError:
    anthropic = None

from docx import Document

from prompt import (
    SYSTEM_PROMPT,
    STYLE_DNA_ANALYSIS_PROMPT,
    build_locked_block,
    build_merge_analysis_prompt,
    build_gap_diagnosis_prompt,
    build_story_reinforcement_prompt,
    build_unit_blueprint_prompt,
    build_unit_draft_prompt,
    build_unit_rewrite_prompt,
    build_title_review_prompt,
    build_epilogue_prompt,
    build_expand_incomplete_unit_prompt,
    build_ch1_stage_a_prompt,
    build_ch1_stage_b_prompt,
    build_ch1_stage_c_prompt,
)

# ─────────────────────────────────────
# CONFIG
# ─────────────────────────────────────
APP_TITLE = "NOVEL ENGINE"
APP_SUB = "NOVEL WRITER STUDIO"

DEFAULT_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
MODEL_OPUS = os.getenv("ANTHROPIC_MODEL_OPUS", "claude-opus-4-20250514")
MAX_TOKENS_SHORT = 4000
MAX_TOKENS_MID = 6000
MAX_TOKENS_LONG = 8192

UNIT_TARGET_LENGTHS = {
    1: 7000, 2: 7000, 3: 8000,
    4: 8000, 5: 8000, 6: 9000,
    7: 9000, 8: 9000, 9: 8000,
    10: 8000, 11: 8000, 12: 9000,
    13: 2500,
}

UNIT_MIN_LENGTHS = {
    1: 6000, 2: 6000, 3: 6500,
    4: 6500, 5: 6500, 6: 7000,
    7: 7000, 8: 7000, 9: 6500,
    10: 6500, 11: 6500, 12: 7000,
    13: 1800,
}

# ─────────────────────────────────────
# PAGE
# ─────────────────────────────────────
st.set_page_config(
    page_title="BLUE JEANS | Novel Engine",
    page_icon="👖",
    layout="wide",
)

# ─────────────────────────────────────
# CSS
# ─────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
@import url('https://cdn.jsdelivr.net/gh/projectnoonnu/2408-3@latest/Paperlogy.css');
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&display=swap');

:root {
    --navy: #202A78;
    --y: #FFCB05;
    --bg: #F7F7F5;
    --card: #FFFFFF;
    --card-border: #DDDDE6;
    --t: #2A2A3A;
    --dim: #8A8FA3;
    --light-bg: #EEEEF6;
    --display: 'Playfair Display', 'Paperlogy', 'Georgia', serif;
    --body: 'Pretendard', -apple-system, sans-serif;
    --heading: 'Paperlogy', 'Pretendard', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--body);
    color: var(--t);
    -webkit-font-smoothing: antialiased;
}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stMainBlockContainer"], [data-testid="stHeader"],
[data-testid="stBottom"] {
    background-color: var(--bg) !important;
    color: var(--t) !important;
}
.stMarkdown, .stText, .stCode { color: var(--t) !important; }
h1,h2,h3,h4,h5,h6 {
    color: var(--navy) !important;
    font-family: var(--heading) !important;
}
p, span, label, div, li { color: var(--t); }
section[data-testid="stSidebar"] { display: none; }

.stTextInput input, .stTextArea textarea,
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
    background-color: var(--card) !important;
    color: var(--t) !important;
    border: 1.5px solid var(--card-border) !important;
    border-radius: 8px !important;
    font-family: var(--body) !important;
    font-size: 0.92rem !important;
    padding: 0.65rem 0.85rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus,
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
    border-color: var(--navy) !important;
    box-shadow: 0 0 0 2px rgba(32,42,120,0.08) !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder,
[data-testid="stTextInput"] input::placeholder, [data-testid="stTextArea"] textarea::placeholder {
    color: var(--dim) !important;
    font-size: 0.85rem !important;
}
.stSelectbox > div > div, [data-baseweb="select"] > div, [data-baseweb="select"] input {
    background-color: var(--card) !important;
    color: var(--t) !important;
    border-color: var(--card-border) !important;
    border-radius: 8px !important;
}
[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"], [role="option"] {
    background-color: var(--card) !important;
    color: var(--t) !important;
}
[role="option"]:hover { background-color: var(--light-bg) !important; }
.stTextInput label, .stTextArea label, .stSelectbox label {
    color: var(--t) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    margin-bottom: 0.3rem !important;
}
.stButton > button {
    color: var(--t) !important;
    border: 1.5px solid var(--card-border) !important;
    background-color: var(--card) !important;
    border-radius: 8px !important;
    font-family: var(--body) !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 1.2rem !important;
    transition: all 0.2s;
}
.stButton > button:hover {
    border-color: var(--navy) !important;
    box-shadow: 0 2px 8px rgba(32,42,120,0.08) !important;
}
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background-color: var(--y) !important;
    color: var(--navy) !important;
    border-color: var(--y) !important;
    font-weight: 800 !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background-color: #E8B800 !important;
    box-shadow: 0 2px 12px rgba(255,203,5,0.3) !important;
}
.stDownloadButton > button {
    color: var(--navy) !important;
    border: 1.5px solid var(--y) !important;
    background-color: var(--y) !important;
    border-radius: 8px !important;
    font-family: var(--body) !important;
    font-weight: 800 !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 1.2rem !important;
}
.stExpander, details, details summary {
    background-color: var(--card) !important;
    color: var(--t) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 8px !important;
}
details[open] > div { background-color: var(--card) !important; }

.header-wrap {
    text-align: center;
    padding: 2.5rem 0 0.5rem 0;
}
.header {
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--navy);
    letter-spacing: 0.25em;
    font-family: var(--body);
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}
.brand-title {
    font-size: 2.8rem;
    font-weight: 900;
    color: var(--navy);
    font-family: var(--display);
    letter-spacing: -0.01em;
    position: relative;
    display: inline-block;
}
.brand-title::after {
    content: '';
    position: absolute;
    bottom: 2px;
    left: 0;
    width: 100%;
    height: 4px;
    background: var(--y);
    border-radius: 2px;
}
.sub {
    font-size: 0.68rem;
    color: var(--dim);
    letter-spacing: 0.22em;
    margin-top: 0.8rem;
    margin-bottom: 1.8rem;
    text-transform: uppercase;
}
.callout {
    background: var(--light-bg);
    border-left: 4px solid var(--navy);
    padding: 0.9rem 1.1rem;
    margin: 0.5rem 0 1.2rem 0;
    border-radius: 0 8px 8px 0;
    font-size: 0.88rem;
    color: var(--t);
}
.section-header {
    background: var(--y);
    color: var(--navy);
    padding: 0.6rem 1rem;
    border-radius: 6px;
    font-weight: 800;
    font-size: 1rem;
    font-family: var(--heading);
    margin: 1.5rem 0 0.8rem 0;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.small-meta {
    font-size: 0.78rem;
    color: var(--dim);
    margin-top: -0.2rem;
    margin-bottom: 0.5rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────
# STATE
# ─────────────────────────────────────
# FIX: unit_drafts 키를 zero-padded 형식("01"~"13")으로 통일
DEFAULT_STATE = {
    "style_dna": "",
    "merged_analysis": "",
    "gap_diagnosis": "",
    "story_reinforcement": {"기": "", "승": "", "전": "", "결": ""},
    "story_reinforcement_merged": "",
    "unit_blueprints": {
        "01-02": "",
        "03-04": "",
        "05-06": "",
        "07-08": "",
        "09-10": "",
        "11-12": "",
    },
    "unit_drafts": {f"{i:02d}" if i < 13 else "13": "" for i in range(1, 14)},
    "chapter_titles": {f"{i:02d}" if i < 13 else "13": "" for i in range(1, 14)},
    "ch1_stage_a": "",
    "ch1_stage_b": "",
    "ch1_stage_c": "",
    "unit_summaries": {},
    "quality_report": {},
    "character_tracker": {},
    "title_review": "",
    "status_message": "",
    "status_type": "info",
}

for k, v in DEFAULT_STATE.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────
# HELPERS
# ─────────────────────────────────────
def get_client() -> Optional["anthropic.Anthropic"]:
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key or anthropic is None:
        return None
    return anthropic.Anthropic(api_key=api_key)


def llm_call(user_prompt: str, max_tokens: int = MAX_TOKENS_MID, use_opus: bool = False) -> str:
    client = get_client()
    if client is None:
        return (
            "[오프라인 미리보기 모드]\n\n"
            "ANTHROPIC_API_KEY가 설정되지 않았거나 anthropic 패키지가 설치되지 않았습니다.\n"
            "실제 모델 호출 대신 프롬프트 초안만 구성된 상태입니다.\n\n"
            + user_prompt[:4000]
        )

    model = MODEL_OPUS if use_opus else DEFAULT_MODEL
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    parts = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "\n".join(parts).strip()


def merge_nonempty(parts: List[str], sep: str = "\n\n") -> str:
    return sep.join([p.strip() for p in parts if p and p.strip()])


def ensure_final_ending(text: str, unit_no: int) -> str:
    text = (text or "").rstrip()
    if unit_no in (12, 13) and not text.endswith("끝."):
        return f"{text}\n\n끝."
    return text


def is_incomplete_text(text: str, unit_no: int) -> bool:
    txt = (text or "").strip()
    if not txt:
        return True

    min_len = UNIT_MIN_LENGTHS.get(unit_no, 6000)
    if len(txt) < min_len:
        return True

    valid_endings = [".", "!", "?", "\u201d", "\"", "'", "\u2019", "끝."]
    if not any(txt.endswith(e) for e in valid_endings):
        return True

    lines = [line for line in txt.splitlines() if line.strip()]
    if len(lines) < 12:
        return True

    return False


# ─────────────────────────────────────
# 품질 자동 체크 (생성 후 즉시 경고)
# ─────────────────────────────────────
def analyze_unit_quality(text: str) -> dict:
    """생성된 Unit 원고의 품질 문제를 자동 감지한다."""
    import re
    if not text or not text.strip():
        return {}

    issues = []
    stats = {}

    # ── 종결어미 반복 ──
    cnt_isseotda = len(re.findall(r"있었다", text))
    cnt_geosieotda = len(re.findall(r"것이었다", text))
    stats["있었다"] = cnt_isseotda
    stats["것이었다"] = cnt_geosieotda
    if cnt_isseotda > 15:
        issues.append(f"⚠️ '있었다' {cnt_isseotda}회 — 15회 이하로 줄이세요. 구체적 동사로 대체.")
    if cnt_geosieotda > 3:
        issues.append(f"⚠️ '것이었다' 해설체 {cnt_geosieotda}회 — 3회 이하로.")

    # ── 대사 태그 반복 ──
    cnt_said = len(re.findall(r"말했다", text))
    cnt_asked = len(re.findall(r"물었다", text))
    cnt_answered = len(re.findall(r"대답했다", text))
    tag_total = cnt_said + cnt_asked + cnt_answered
    stats["대사태그 합계"] = tag_total
    if tag_total > 12:
        issues.append(f"⚠️ 대사 태그(말했다/물었다/대답했다) {tag_total}회 — 행동 태그로 대체하세요.")

    # ── 장면 반복 ──
    cnt_phone = len(re.findall(r"전화|휴대폰이|진동했다|문자|메시지가", text))
    cnt_window = len(re.findall(r"창밖|창 밖|유리창|내려다보", text))
    cnt_elevator = len(re.findall(r"엘리베이터|로비를|현관을", text))
    stats["전화/메시지"] = cnt_phone
    stats["창밖 묘사"] = cnt_window
    if cnt_phone > 4:
        issues.append(f"⚠️ 전화/메시지 장면 {cnt_phone}회 — 대면/발견/관찰로 대체하세요.")
    if cnt_window > 3:
        issues.append(f"⚠️ '창밖' 묘사 {cnt_window}회 — 다른 방식으로 인물 내면을 쓰세요.")
    if cnt_elevator > 2:
        issues.append(f"⚠️ 엘리베이터/로비 {cnt_elevator}회 — 이동 묘사를 줄이세요.")

    # ── 시제 체크 ──
    present_patterns = re.findall(
        r"(?:한다|된다|이다|간다|온다|본다|듣는다|만든다|열린다|닫힌다|울린다|채운다|넣는다|흐른다)\.",
        text,
    )
    cnt_present = len(present_patterns)
    stats["현재형 종결"] = cnt_present
    if cnt_present > 3:
        issues.append(f"🚨 현재형 종결어미 {cnt_present}회 감지 — 소설은 과거형(~했다)으로 써야 합니다!")

    # ── 접속부사 과잉 ──
    cnt_conj = len(re.findall(r"(?:그러나|하지만|그리고|또한|그래서|따라서)", text))
    stats["접속부사"] = cnt_conj
    if cnt_conj > 15:
        issues.append(f"⚠️ 접속부사 {cnt_conj}회 — 접속부사 없이 문장을 병치하세요.")

    # ── 같은 행동 반복 ──
    action_patterns = [
        (r"포크를 내려놓", "포크를 내려놓"),
        (r"잔을 내려놓", "잔을 내려놓"),
        (r"눈을 감", "눈을 감"),
        (r"한숨을 쉬", "한숨을 쉬"),
        (r"고개를 끄덕", "고개를 끄덕"),
        (r"고개를 저", "고개를 저"),
    ]
    for pattern, label in action_patterns:
        cnt = len(re.findall(pattern, text))
        if cnt >= 3:
            issues.append(f"⚠️ '{label}' {cnt}회 반복 — 같은 동작을 줄이세요.")

    # ── 분량 ──
    stats["총 글자수"] = len(text)

    return {"issues": issues, "stats": stats}


# ─────────────────────────────────────
# Unit 요약 자동 생성
# ─────────────────────────────────────
def generate_unit_summary(unit_no: int, text: str) -> str:
    """완성된 Unit의 1줄 요약을 생성한다."""
    client = get_client()
    if not client or not text or not text.strip():
        return ""
    try:
        resp = client.messages.create(
            model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": (
                    f"다음은 소설의 UNIT {unit_no:02d} 원고이다. "
                    "이 Unit의 핵심 사건, 인물 변화, 감정 상태를 1~2문장으로 요약하라. "
                    "요약만 출력하고 다른 말은 하지 마라.\n\n"
                    f"{text[:3000]}"
                ),
            }],
        )
        return resp.content[0].text.strip()
    except Exception:
        return ""


def gather_all_summaries() -> str:
    """모든 Unit 요약을 모아 반환한다."""
    summaries = st.session_state.get("unit_summaries", {})
    lines = []
    for i in range(1, 14):
        key = f"{i:02d}" if i < 13 else "13"
        s = summaries.get(key, "")
        if s:
            lines.append(f"[UNIT {key} 요약] {s}")
    return "\n".join(lines)


# ─────────────────────────────────────
# 캐릭터 등장 추적
# ─────────────────────────────────────
def extract_characters_from_text(text: str) -> str:
    """Unit 원고에서 등장 인물 목록을 추출한다."""
    client = get_client()
    if not client or not text or not text.strip():
        return ""
    try:
        resp = client.messages.create(
            model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": (
                    "다음 소설 원고에서 등장하는 인물의 이름만 쉼표로 구분해서 나열하라. "
                    "이름만 출력하고 다른 말은 하지 마라. 이름이 없으면 '없음'.\n\n"
                    f"{text[:4000]}"
                ),
            }],
        )
        return resp.content[0].text.strip()
    except Exception:
        return ""


def track_characters(unit_key: str, text: str):
    """캐릭터 등장을 추적하고 세션에 저장한다."""
    if "character_tracker" not in st.session_state:
        st.session_state["character_tracker"] = {}
    names_str = extract_characters_from_text(text)
    if names_str and names_str != "없음":
        names = [n.strip() for n in names_str.split(",") if n.strip()]
        st.session_state["character_tracker"][unit_key] = names


def get_character_report() -> dict:
    """캐릭터 등장 추적 리포트를 생성한다."""
    tracker = st.session_state.get("character_tracker", {})
    if not tracker:
        return {}
    first_appearance = {}
    all_chars = set()
    for key in sorted(tracker.keys()):
        for name in tracker[key]:
            all_chars.add(name)
            if name not in first_appearance:
                first_appearance[name] = key
    # 입력된 캐릭터 목록과 비교
    input_chars = st.session_state.get("characters", "")
    warnings = []
    for name, unit in first_appearance.items():
        if unit != "01" and name not in input_chars:
            warnings.append(f"⚠️ '{name}' — UNIT {unit}에서 처음 등장. STEP 1 캐릭터 입력에 없는 인물.")
    return {
        "first_appearance": first_appearance,
        "warnings": warnings,
        "total": len(all_chars),
    }


def get_story_reinforcement_text() -> str:
    sr = st.session_state["story_reinforcement"]
    merged = []
    for k in ["기", "승", "전", "결"]:
        if sr.get(k):
            merged.append(f"[{k} 보강]\n{sr[k]}")
    merged_text = merge_nonempty(merged)
    st.session_state["story_reinforcement_merged"] = merged_text
    return merged_text


def gather_blueprints_text() -> str:
    bp = st.session_state["unit_blueprints"]
    keys = ["01-02", "03-04", "05-06", "07-08", "09-10", "11-12"]
    merged = []
    for key in keys:
        if bp.get(key):
            merged.append(f"[UNIT {key} 설계]\n{bp[key]}")
    return merge_nonempty(merged)


def gather_all_drafts_text() -> str:
    """전체 원고 — 내보내기용"""
    drafts = st.session_state["unit_drafts"]
    titles = st.session_state["chapter_titles"]
    merged = []
    for i in range(1, 14):
        key = f"{i:02d}" if i < 13 else "13"
        txt = drafts.get(key, "")
        if txt.strip():
            ch_title = titles.get(key, "")
            if ch_title:
                merged.append(f"{ch_title}\n{txt}")
            else:
                merged.append(txt)
    return merge_nonempty(merged)


def gather_recent_drafts(current_unit: int, window: int = 2) -> str:
    """이전 Unit 요약 + 최근 N개 Unit 원고 — 연결성과 컨텍스트 동시 확보"""
    drafts = st.session_state["unit_drafts"]
    titles = st.session_state["chapter_titles"]
    summaries = st.session_state.get("unit_summaries", {})
    merged = []

    # ── 1. 이전 전체 Unit의 1줄 요약 (컨텍스트 유지) ──
    summary_lines = []
    for i in range(1, current_unit):
        key = f"{i:02d}" if i < 13 else "13"
        s = summaries.get(key, "")
        if s:
            summary_lines.append(f"  UNIT {key}: {s}")
    if summary_lines:
        merged.append("[이전 Unit 요약 — 전체 흐름 파악용]\n" + "\n".join(summary_lines))

    # ── 2. 최근 N개 Unit의 실제 텍스트 (연결성) ──
    start = max(1, current_unit - window)
    for i in range(start, current_unit):
        key = f"{i:02d}" if i < 13 else "13"
        txt = drafts.get(key, "")
        if txt.strip():
            ch_title = titles.get(key, "")
            label = ch_title if ch_title else f"[UNIT {key}]"
            if len(txt) > 3000:
                txt = "(...전략...)\n" + txt[-3000:]
            merged.append(f"{label}\n{txt}")
    return merge_nonempty(merged)


def export_txt(content: str) -> bytes:
    return export_clean_content(content).encode("utf-8")


def export_clean_content(content: str) -> str:
    """최종 원고에서 내부 마커를 제거하고 소설 포맷으로 정리"""
    import re
    lines = content.split("\n")
    cleaned = []
    for line in lines:
        s = line.strip()
        # 내부 라벨 제거
        if s.startswith("[UNIT ") and s.endswith("]"):
            continue
        # Stage A/B/C 내부 라벨 제거
        if s.startswith("# Chapter") and ("Stage A" in s or "Stage B" in s or "Stage C" in s):
            continue
        if s.startswith("# Chapter") and "Unit" in s:
            continue
        if s.startswith("## ") or s.startswith("### "):
            continue
        # markdown # CHAPTER → [CHAPTER] 변환
        m = re.match(r"^#\s*(CHAPTER\s*\d+)\s*[—\-]\s*(.+)$", s)
        if m:
            cleaned.append(f"[{m.group(1)}] — {m.group(2)}")
            continue
        # 기타 markdown # 헤더 → 일반 텍스트
        if s.startswith("# "):
            cleaned.append(s[2:])
            continue
        cleaned.append(line)

    result = "\n".join(cleaned)

    # ── 곧은 따옴표 → 둥근 따옴표 변환 ──
    # 큰따옴표: " → " / "
    result = re.sub(r'(?<=^)"', '\u201c', result, flags=re.MULTILINE)       # 줄 시작의 "
    result = re.sub(r'(?<=\s)"', '\u201c', result)                          # 공백 뒤의 "
    result = re.sub(r'"(?=\s)', '\u201d', result)                           # 공백 앞의 "
    result = re.sub(r'"(?=[.,!?\n])', '\u201d', result)                     # 구두점 앞의 "
    result = re.sub(r'"(?=$)', '\u201d', result, flags=re.MULTILINE)        # 줄 끝의 "
    # 남은 곧은 큰따옴표 처리 (짝 맞추기)
    remaining = []
    is_open = True
    for ch in result:
        if ch == '"':
            remaining.append('\u201c' if is_open else '\u201d')
            is_open = not is_open
        else:
            remaining.append(ch)
    result = "".join(remaining)

    # 작은따옴표: ' → ' / '  (대화 안 인용 등)
    result = result.replace("\u2018", "\u2018").replace("\u2019", "\u2019")  # 이미 둥근이면 유지
    # 곧은 작은따옴표는 한국 소설에서 거의 안 쓰이므로 최소 처리
    result = re.sub(r"(?<=\s)'", '\u2018', result)
    result = re.sub(r"'(?=[\s.,!?])", '\u2019', result)

    return result


def export_docx(title: str, content: str) -> bytes:
    """한국 소설 원고 표준 DOCX — MS Word 소설 원고 포맷"""
    from docx.shared import Pt, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn

    content = export_clean_content(content)

    doc = Document()

    # ── 페이지: A4, 여백 (상 3cm, 하좌우 2.54cm) ──
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(3)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(2.54)
    section.right_margin = Cm(2.54)

    # ── 기본 스타일: 바탕 10pt, 줄간격 160%, 양쪽정렬, 첫 줄 들여쓰기 1글자 ──
    style_normal = doc.styles["Normal"]
    style_normal.font.name = "Batang"
    style_normal.font.size = Pt(10)
    style_normal.paragraph_format.line_spacing = 1.6
    style_normal.paragraph_format.space_before = Pt(0)
    style_normal.paragraph_format.space_after = Pt(0)
    style_normal.paragraph_format.first_line_indent = Cm(0.35)
    style_normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # 한글 폰트 (eastAsia)
    rpr = style_normal.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        from lxml import etree
        rfonts = etree.SubElement(rpr, qn("w:rFonts"))
    rfonts.set(qn("w:eastAsia"), "Batang")

    # ── 헬퍼 ──
    def add_normal(text):
        return doc.add_paragraph(text)

    def add_dialogue(text):
        """대화문 — 들여쓰기 없음"""
        p = doc.add_paragraph(text)
        p.paragraph_format.first_line_indent = Cm(0)
        return p

    def add_centered(text, size=10, bold=False, before=0, after=0):
        p = doc.add_paragraph(text)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_before = Pt(before)
        p.paragraph_format.space_after = Pt(after)
        if p.runs:
            p.runs[0].font.size = Pt(size)
            p.runs[0].font.bold = bold

    def add_scene_break():
        """장면 전환 — 빈 줄 1개"""
        p = doc.add_paragraph("")
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.first_line_indent = Cm(0)

    def add_page_break():
        """페이지 나누기"""
        from docx.oxml.ns import qn as _qn
        p = doc.add_paragraph()
        run = p.add_run()
        br = run._element.makeelement(_qn('w:br'), {_qn('w:type'): 'page'})
        run._element.append(br)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)

    # ── 파싱 ──
    lines = content.split("\n")
    i = 0
    is_first_line = True
    chapter_count = 0

    while i < len(lines):
        s = lines[i].strip()

        # 빈 줄 = 장면 전환
        if not s:
            add_scene_break()
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            continue

        # 작품 제목 (첫 줄)
        if is_first_line and len(s) < 80:
            add_centered(s, size=16, bold=True, before=72, after=24)
            is_first_line = False
            i += 1
            continue
        is_first_line = False

        # 챕터 제목: [CHAPTER X] — ...
        if s.startswith("[CHAPTER"):
            if chapter_count > 0:
                add_page_break()
            add_centered(s, size=14, bold=True, before=36, after=18)
            chapter_count += 1
            i += 1
            continue

        # "끝."
        if s == "끝.":
            add_centered(s, size=11, bold=False, before=18, after=0)
            i += 1
            continue

        # 대화문 — 따옴표로 시작하면 들여쓰기 없음
        if s.startswith('"') or s.startswith('\u201c') or s.startswith('\u300c') or s.startswith("'"):
            add_dialogue(s)
            i += 1
            continue

        # 일반 본문 — 들여쓰기 적용 (기본 스타일)
        add_normal(s)
        i += 1

    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio.read()


def final_manuscript_text(current_title: str) -> str:
    parts = []
    if current_title.strip():
        parts.append(current_title.strip())

    # 본문
    drafts = gather_all_drafts_text().strip()
    if drafts:
        parts.append(drafts)
    manuscript = "\n\n".join(parts).rstrip()
    if manuscript and not manuscript.endswith("끝."):
        manuscript += "\n\n끝."
    return manuscript


def safe_filename(name: str) -> str:
    name = (name or "novel_draft").strip()
    name = re.sub(r"[^0-9A-Za-z가-힣_-]+", "_", name)
    return name or "novel_draft"


def parse_chapter_title(text: str) -> tuple:
    """원고 첫 줄에서 [CHAPTER X] — 서브타이틀을 추출한다.
    Returns (chapter_title, body) — 제목이 없으면 ("", text)"""
    if not text or not text.strip():
        return ("", text)
    lines = text.strip().split("\n", 1)
    first_line = lines[0].strip()
    if first_line.startswith("[CHAPTER"):
        body = lines[1].strip() if len(lines) > 1 else ""
        return (first_line, body)
    return ("", text.strip())


def set_status(message: str, status_type: str = "info") -> None:
    st.session_state["status_message"] = message
    st.session_state["status_type"] = status_type


def render_status() -> None:
    msg = st.session_state.get("status_message", "").strip()
    status_type = st.session_state.get("status_type", "info")
    if not msg:
        return
    if status_type == "success":
        st.success(msg)
    elif status_type == "error":
        st.error(msg)
    elif status_type == "warning":
        st.warning(msg)
    else:
        st.info(msg)


def run_with_status(start_message: str, done_message: str, fn):
    set_status(start_message, "info")
    with st.spinner(start_message):
        try:
            result = fn()
            set_status(done_message, "success")
            return result
        except Exception as e:
            set_status(f"작업 중 오류가 발생했습니다: {e}", "error")
            return None


def generate_or_expand_unit(unit_no: int, prompt: str) -> str:
    result = llm_call(prompt, max_tokens=MAX_TOKENS_LONG, use_opus=True)
    result = ensure_final_ending(result, unit_no)

    if is_incomplete_text(result, unit_no):
        expand_prompt = build_expand_incomplete_unit_prompt(
            unit_no=unit_no,
            current_text=result,
            target_length=UNIT_TARGET_LENGTHS.get(unit_no, 8000),
            min_length=UNIT_MIN_LENGTHS.get(unit_no, 6000),
        )
        extra = llm_call(expand_prompt, max_tokens=MAX_TOKENS_MID, use_opus=True)
        result = (result.rstrip() + "\n\n" + extra.strip()).strip()
        result = ensure_final_ending(result, unit_no)

    return result


# ─────────────────────────────────────
# HEADER
# ─────────────────────────────────────
st.markdown(
    f"""
<div class="header-wrap">
    <div class="header">BLUE JEANS PICTURES</div>
    <div class="brand-title">{APP_TITLE}</div>
    <div class="sub">YOUNG · VINTAGE · FREE · INNOVATIVE</div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="callout">
기획 자료를 넣으면 엔진이 분석 → 부족한 점 진단 → 기승전결 보강 → 12 Unit 설계 → Unit 원고 생성 →
가제 검토/제목 제안까지 순서대로 진행합니다.
</div>
""",
    unsafe_allow_html=True,
)

render_status()

# ─────────────────────────────────────
# STEP 1
# ─────────────────────────────────────
st.markdown('<div class="section-header">🔥 STEP 1 · 작품 자료 입력</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    working_title = st.text_input("현재 가제", placeholder="예: 감각구역 / 머지 앤 어퀴지션 / 검은 항구")
    genre = st.text_input("장르", placeholder="예: 스릴러, 역사드라마, 금융 스릴러, 첩보물")
    format_mode = st.selectbox("형식", ["장편소설", "웹소설", "하이브리드"], index=0)

with col2:
    pov = st.selectbox("시점", ["3인칭 제한", "1인칭", "듀얼 POV", "다중시점"], index=0)
    target_length = st.text_input("목표 분량", placeholder="예: 12만자 / 12 Units / Unit당 1만자")
    style_strength = st.selectbox("문체 반영 강도", ["약", "중", "강"], index=1)

overview = st.text_area(
    "작품 개요",
    height=220,
    placeholder="로그라인, 기획의도, 세계관, 장르 톤, 작품의 핵심 질문, 차별점",
)

characters = st.text_area(
    "캐릭터",
    height=220,
    placeholder="주인공 / 적대자 / 조력자 / 핵심 관계, 각 인물의 욕망 / 결핍 / 비밀 / 변화",
)

synopsis = st.text_area(
    "줄거리 / 트리트먼트",
    height=260,
    placeholder="시작, 중반, 위기, 클라이맥스, 엔딩 방향, 반드시 살릴 사건",
)

notes = st.text_area(
    "추가 메모 (선택)",
    height=180,
    placeholder="약한 부분, 반드시 살릴 장면, 정보 레이어, 역사 고증 메모, 참고 톤",
)

style_sample = st.text_area(
    "문체 샘플 (선택)",
    height=220,
    placeholder="Mr.MOON이 직접 쓴 소설/산문/블로그 문장 일부",
)

lock_col1, lock_col2 = st.columns([1, 1])

with lock_col1:
    locked_text = st.text_area(
        "🔒 LOCKED 설정 (절대 변경 불가)",
        height=180,
        placeholder="변경 금지 항목을 줄 단위로 입력\n예:\n- 한유진: QLCP 대표. 직책 변경 금지.\n- 마이클 모건: 적대자. 동맹으로 변경 금지.\n- 기획의도: 글로벌 금융 권력 비판이 테마에 반영되어야 함.",
    )

with lock_col2:
    open_text = st.text_area(
        "🔓 OPEN 설정 (창작 가능 범위)",
        height=180,
        placeholder="자유롭게 창작 가능한 항목\n예:\n- 캐릭터 외형, 습관, 말투 디테일은 자유롭게 확장 가능.\n- 장면별 감정 변화와 감각 묘사는 자유롭게 창작 가능.",
    )

locked_block = build_locked_block(locked_text, open_text)

# ─────────────────────────────────────
# STEP 2
# ─────────────────────────────────────
st.markdown('<div class="section-header">🔬 STEP 2 · 문체 / 분석</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    if st.button("문체 샘플 분석", type="primary", use_container_width=True):
        def _job():
            prompt = STYLE_DNA_ANALYSIS_PROMPT.format(style_sample=style_sample or "샘플 없음")
            return llm_call(prompt, max_tokens=MAX_TOKENS_SHORT)
        result = run_with_status("문체 샘플을 분석 중입니다...", "문체 샘플 분석이 완료되었습니다.", _job)
        if result is not None:
            st.session_state["style_dna"] = result

with c2:
    if st.button("기획서 통합 분석", use_container_width=True):
        def _job():
            prompt = build_merge_analysis_prompt(
                working_title=working_title,
                genre=genre,
                format_mode=format_mode,
                pov=pov,
                target_length=target_length,
                overview=overview,
                characters=characters,
                synopsis=synopsis,
                notes=notes,
                style_dna=st.session_state["style_dna"],
                style_strength=style_strength,
                locked_block=locked_block,
            )
            return llm_call(prompt, max_tokens=MAX_TOKENS_MID)
        result = run_with_status("기획서 통합 분석 중입니다...", "기획서 통합 분석이 완료되었습니다.", _job)
        if result is not None:
            st.session_state["merged_analysis"] = result

with c3:
    if st.button("부족한 점 진단", use_container_width=True):
        def _job():
            prompt = build_gap_diagnosis_prompt(
                working_title=working_title,
                merged_analysis=st.session_state["merged_analysis"],
                overview=overview,
                characters=characters,
                synopsis=synopsis,
                notes=notes,
                style_dna=st.session_state["style_dna"],
                locked_block=locked_block,
            )
            return llm_call(prompt, max_tokens=MAX_TOKENS_MID)
        result = run_with_status("부족한 점을 진단 중입니다...", "부족한 점 진단이 완료되었습니다.", _job)
        if result is not None:
            st.session_state["gap_diagnosis"] = result

if st.session_state["style_dna"]:
    with st.expander("STYLE DNA 보기", expanded=False):
        st.markdown(st.session_state["style_dna"])

if st.session_state["merged_analysis"]:
    with st.expander("기획서 통합 분석 보기", expanded=False):
        st.markdown(st.session_state["merged_analysis"])

if st.session_state["gap_diagnosis"]:
    with st.expander("부족한 점 진단 보기", expanded=False):
        st.markdown(st.session_state["gap_diagnosis"])

# ─────────────────────────────────────
# STEP 3
# ─────────────────────────────────────
st.markdown('<div class="section-header">📖 STEP 3 · 전체 줄거리 보강 (기승전결 분할)</div>', unsafe_allow_html=True)

sr_col1, sr_col2, sr_col3, sr_col4 = st.columns(4)

def reinforce_segment(segment_name: str):
    def _job():
        prompt = build_story_reinforcement_prompt(
            segment_name=segment_name,
            working_title=working_title,
            genre=genre,
            overview=overview,
            characters=characters,
            synopsis=synopsis,
            notes=notes,
            merged_analysis=st.session_state["merged_analysis"],
            gap_diagnosis=st.session_state["gap_diagnosis"],
            style_dna=st.session_state["style_dna"],
            locked_block=locked_block,
        )
        return llm_call(prompt, max_tokens=MAX_TOKENS_MID)

    result = run_with_status(
        f"{segment_name} 구간을 장편소설 구조로 보강 중입니다...",
        f"{segment_name} 구간 보강이 완료되었습니다.",
        _job,
    )
    if result is not None:
        st.session_state["story_reinforcement"][segment_name] = result
        get_story_reinforcement_text()

with sr_col1:
    if st.button("기 보강", use_container_width=True):
        reinforce_segment("기")
with sr_col2:
    if st.button("승 보강", use_container_width=True):
        reinforce_segment("승")
with sr_col3:
    if st.button("전 보강", use_container_width=True):
        reinforce_segment("전")
with sr_col4:
    if st.button("결 보강", use_container_width=True):
        reinforce_segment("결")

story_merged_text = get_story_reinforcement_text()

for seg in ["기", "승", "전", "결"]:
    seg_text = st.session_state["story_reinforcement"].get(seg, "")
    if seg_text:
        with st.expander(f"{seg} 보강 보기", expanded=False):
            st.markdown(seg_text)

# ─────────────────────────────────────
# STEP 4
# ─────────────────────────────────────
st.markdown('<div class="section-header">🏗️ STEP 4 · 12 Unit 설계 (2 Unit씩 6개 버튼)</div>', unsafe_allow_html=True)

bp_cols_top = st.columns(3)
bp_cols_bottom = st.columns(3)

def build_blueprint(group_key: str):
    def _job():
        prompt = build_unit_blueprint_prompt(
            group_key=group_key,
            working_title=working_title,
            genre=genre,
            format_mode=format_mode,
            pov=pov,
            overview=overview,
            characters=characters,
            story_reinforcement_merged=story_merged_text,
            synopsis=synopsis,
            notes=notes,
            style_dna=st.session_state["style_dna"],
            locked_block=locked_block,
        )
        return llm_call(prompt, max_tokens=MAX_TOKENS_MID)

    result = run_with_status(
        f"UNIT {group_key} 설계를 생성 중입니다...",
        f"UNIT {group_key} 설계가 완료되었습니다.",
        _job,
    )
    if result is not None:
        st.session_state["unit_blueprints"][group_key] = result

buttons = [
    ("UNIT 01~02 설계", "01-02"),
    ("UNIT 03~04 설계", "03-04"),
    ("UNIT 05~06 설계", "05-06"),
    ("UNIT 07~08 설계", "07-08"),
    ("UNIT 09~10 설계", "09-10"),
    ("UNIT 11~12 설계", "11-12"),
]

for idx, (label, group_key) in enumerate(buttons):
    target_col = bp_cols_top[idx] if idx < 3 else bp_cols_bottom[idx - 3]
    with target_col:
        if st.button(label, use_container_width=True):
            build_blueprint(group_key)

for group_key in ["01-02", "03-04", "05-06", "07-08", "09-10", "11-12"]:
    if st.session_state["unit_blueprints"].get(group_key):
        with st.expander(f"UNIT {group_key} 설계 보기", expanded=False):
            st.markdown(st.session_state["unit_blueprints"][group_key])

all_blueprints_text = gather_blueprints_text()

# ─────────────────────────────────────
# STEP 5
# ─────────────────────────────────────
st.markdown('<div class="section-header">✍️ STEP 5 · Unit 원고 생성 / 다시 쓰기</div>', unsafe_allow_html=True)

unit_options = [f"{i:02d}" for i in range(1, 13)] + ["13"]
selected_unit = st.selectbox(
    "작업할 Unit 선택",
    unit_options,
    format_func=lambda x: "UNIT 13 · 에필로그" if x == "13" else f"UNIT {x}",
)

# ─── Chapter 1 다단계 생성 시스템 ───
if selected_unit == "01":
    st.markdown(
        '<div class="callout" style="border-left-color:var(--y)">'
        '<b>Chapter 1 다단계 생성</b> — 오프닝은 소설의 얼굴입니다. 3단계로 나눠서 각 단계를 확인하고 승인한 뒤 다음 단계로 넘어갑니다.'
        '<br>Stage A: PEAK (정상) → Stage B: WORLD (전개) → Stage C: LOSS (균열)'
        '</div>',
        unsafe_allow_html=True,
    )

    ch1_a, ch1_b, ch1_c = st.columns(3)

    with ch1_a:
        st.markdown("**Stage A · PEAK**")
        st.markdown('<div class="small-meta">오프닝 장면 · 음식 시그니처 · 인물 정의 · ~2000자</div>', unsafe_allow_html=True)
        if st.button("Stage A 생성", type="primary", use_container_width=True, key="ch1_a_btn"):
            def _job():
                prompt = build_ch1_stage_a_prompt(
                    working_title=working_title, genre=genre, format_mode=format_mode,
                    pov=pov, overview=overview, characters=characters,
                    synopsis=synopsis, notes=notes,
                    style_dna=st.session_state["style_dna"], style_strength=style_strength,
                    locked_block=locked_block,
                )
                return llm_call(prompt, max_tokens=MAX_TOKENS_MID, use_opus=True)
            result = run_with_status("Stage A: PEAK 오프닝을 생성 중입니다...", "Stage A 생성 완료.", _job)
            if result is not None:
                st.session_state["ch1_stage_a"] = result

    with ch1_b:
        st.markdown("**Stage B · WORLD**")
        st.markdown('<div class="small-meta">세계관 · 관계 · 권력 구조를 장면 안에 · ~2500자</div>', unsafe_allow_html=True)
        has_a = bool(st.session_state["ch1_stage_a"].strip())
        if st.button("Stage B 생성", use_container_width=True, disabled=not has_a, key="ch1_b_btn"):
            def _job():
                prompt = build_ch1_stage_b_prompt(
                    working_title=working_title, genre=genre, format_mode=format_mode,
                    pov=pov, overview=overview, characters=characters,
                    synopsis=synopsis, notes=notes,
                    style_dna=st.session_state["style_dna"], style_strength=style_strength,
                    stage_a_text=st.session_state["ch1_stage_a"],
                    locked_block=locked_block,
                )
                return llm_call(prompt, max_tokens=MAX_TOKENS_MID, use_opus=True)
            result = run_with_status("Stage B: WORLD 전개를 생성 중입니다...", "Stage B 생성 완료.", _job)
            if result is not None:
                st.session_state["ch1_stage_b"] = result

    with ch1_c:
        st.markdown("**Stage C · LOSS**")
        st.markdown('<div class="small-meta">균열 · 상실의 신호 · 클리프행어 · ~1500자</div>', unsafe_allow_html=True)
        has_b = bool(st.session_state["ch1_stage_b"].strip())
        if st.button("Stage C 생성", use_container_width=True, disabled=not has_b, key="ch1_c_btn"):
            def _job():
                prompt = build_ch1_stage_c_prompt(
                    working_title=working_title, genre=genre, format_mode=format_mode,
                    pov=pov, overview=overview, characters=characters,
                    synopsis=synopsis, notes=notes,
                    style_dna=st.session_state["style_dna"], style_strength=style_strength,
                    stage_a_text=st.session_state["ch1_stage_a"],
                    stage_b_text=st.session_state["ch1_stage_b"],
                    locked_block=locked_block,
                )
                return llm_call(prompt, max_tokens=MAX_TOKENS_MID, use_opus=True)
            result = run_with_status("Stage C: LOSS 균열을 생성 중입니다...", "Stage C 생성 완료.", _job)
            if result is not None:
                st.session_state["ch1_stage_c"] = result

    # 각 Stage 미리보기
    for stage_key, stage_label in [("ch1_stage_a", "Stage A · PEAK"), ("ch1_stage_b", "Stage B · WORLD"), ("ch1_stage_c", "Stage C · LOSS")]:
        stage_text = st.session_state.get(stage_key, "")
        if stage_text.strip():
            with st.expander(f"{stage_label} 보기", expanded=True):
                st.text_area(stage_label, value=stage_text, height=300, label_visibility="collapsed", key=f"preview_{stage_key}")

    # 3단계 완성 시 합치기 버튼
    all_stages_done = all(st.session_state.get(k, "").strip() for k in ["ch1_stage_a", "ch1_stage_b", "ch1_stage_c"])
    if all_stages_done:
        st.markdown("---")
        if st.button("✅ Chapter 1 확정 — 3단계를 합쳐서 UNIT 01로 저장", type="primary", use_container_width=True, key="ch1_merge_btn"):
            merged = (
                st.session_state["ch1_stage_a"].strip()
                + "\n\n"
                + st.session_state["ch1_stage_b"].strip()
                + "\n\n"
                + st.session_state["ch1_stage_c"].strip()
            )
            # 챕터 제목 파싱
            ch_title, ch_body = parse_chapter_title(merged)
            if ch_title:
                st.session_state["unit_drafts"]["01"] = ch_body
                st.session_state["chapter_titles"]["01"] = ch_title
            else:
                st.session_state["unit_drafts"]["01"] = merged
            set_status("Chapter 1이 확정되었습니다. UNIT 01로 저장 완료.", "success")
            # 품질 자동 체크
            final_text = ch_body if ch_title else merged
            qr = analyze_unit_quality(final_text)
            st.session_state["quality_report"] = qr
            # Unit 요약 자동 생성
            summary = generate_unit_summary(1, final_text)
            if summary:
                if "unit_summaries" not in st.session_state:
                    st.session_state["unit_summaries"] = {}
                st.session_state["unit_summaries"]["01"] = summary
            # 캐릭터 등장 추적
            track_characters("01", final_text)

# ─── 일반 Unit 생성 (Unit 02~13) ───
else:
    draft_col1, draft_col2, draft_col3 = st.columns([1, 1, 1])

    with draft_col1:
        if st.button("Unit 원고 생성", type="primary", use_container_width=True):
            unit_no = int(selected_unit)

            if unit_no == 13:
                def _job():
                    prompt = build_epilogue_prompt(
                        working_title=working_title,
                        genre=genre,
                        overview=overview,
                        characters=characters,
                        synopsis=synopsis,
                        story_reinforcement_merged=story_merged_text,
                        all_blueprints_text=all_blueprints_text,
                        all_drafts_text=gather_recent_drafts(13, window=3),
                        style_dna=st.session_state["style_dna"],
                        locked_block=locked_block,
                    )
                    return generate_or_expand_unit(13, prompt)

                result = run_with_status(
                    "UNIT 13 에필로그를 생성 중입니다...",
                    "UNIT 13 에필로그 생성이 완료되었습니다.",
                    _job,
                )
                if result is not None:
                    ch_title, ch_body = parse_chapter_title(result)
                    st.session_state["unit_drafts"][selected_unit] = ch_body if ch_title else result
                    if ch_title:
                        st.session_state["chapter_titles"][selected_unit] = ch_title
            else:
                def _job():
                    prompt = build_unit_draft_prompt(
                        unit_no=unit_no,
                        working_title=working_title,
                        genre=genre,
                        format_mode=format_mode,
                        pov=pov,
                        overview=overview,
                        characters=characters,
                        synopsis=synopsis,
                        notes=notes,
                        story_reinforcement_merged=story_merged_text,
                        all_blueprints_text=all_blueprints_text,
                        previous_drafts=gather_recent_drafts(unit_no),
                        style_dna=st.session_state["style_dna"],
                        style_strength=style_strength,
                        target_length=UNIT_TARGET_LENGTHS.get(unit_no, 8000),
                        min_length=UNIT_MIN_LENGTHS.get(unit_no, 6000),
                        locked_block=locked_block,
                    )
                    return generate_or_expand_unit(unit_no, prompt)

                done_msg = f"UNIT {unit_no:02d} 원고 생성이 완료되었습니다."
                if unit_no == 12:
                    done_msg = "UNIT 12 본편 마무리 생성이 완료되었습니다."

                result = run_with_status(
                    f"UNIT {unit_no:02d} 원고를 생성 중입니다...",
                    done_msg,
                    _job,
                )
                if result is not None:
                    ch_title, ch_body = parse_chapter_title(result)
                    st.session_state["unit_drafts"][selected_unit] = ch_body if ch_title else result
                    if ch_title:
                        st.session_state["chapter_titles"][selected_unit] = ch_title
                    check_text = ch_body if ch_title else result
                    if is_incomplete_text(check_text, unit_no):
                        set_status(
                            f"UNIT {unit_no:02d}는 생성되었지만 아직 짧거나 미완성일 수 있습니다. 다시 쓰기나 재생성을 권장합니다.",
                            "warning",
                        )
                    # 품질 자동 체크
                    qr = analyze_unit_quality(check_text)
                    st.session_state["quality_report"] = qr
                    # Unit 요약 자동 생성
                    summary = generate_unit_summary(unit_no, check_text)
                    if summary:
                        if "unit_summaries" not in st.session_state:
                            st.session_state["unit_summaries"] = {}
                        st.session_state["unit_summaries"][selected_unit] = summary
                    # 캐릭터 등장 추적
                    track_characters(selected_unit, check_text)

    with draft_col2:
        rewrite_mode = st.selectbox(
            "다시 쓰기 모드",
            ["더 상업적으로", "더 빠르게", "더 감정적으로", "더 차갑게", "더 영상적으로", "더 문학적으로"],
            index=0,
        )
        if st.button("Unit 다시 쓰기", use_container_width=True):
            source_text = st.session_state["unit_drafts"].get(selected_unit, "")
            if source_text.strip():
                def _job():
                    prompt = build_unit_rewrite_prompt(
                        unit_no=int(selected_unit),
                        rewrite_mode=rewrite_mode,
                        source_text=source_text,
                        style_dna=st.session_state["style_dna"],
                        target_length=UNIT_TARGET_LENGTHS.get(int(selected_unit), 8000),
                        min_length=UNIT_MIN_LENGTHS.get(int(selected_unit), 6000),
                    )
                    return generate_or_expand_unit(int(selected_unit), prompt)

                result = run_with_status(
                    f"UNIT {selected_unit}를 다시 쓰는 중입니다...",
                    f"UNIT {selected_unit} 다시 쓰기가 완료되었습니다.",
                    _job,
                )
                if result is not None:
                    st.session_state["unit_drafts"][selected_unit] = result

    with draft_col3:
        unit_num = int(selected_unit)
        st.markdown(
            f'<div class="small-meta">목표 분량 {UNIT_TARGET_LENGTHS.get(unit_num, 8000):,}자 / 최소 {UNIT_MIN_LENGTHS.get(unit_num, 6000):,}자</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="small-meta">UNIT 12는 본편을 반드시 마무리합니다. UNIT 13은 선택형 에필로그입니다.</div>',
            unsafe_allow_html=True,
        )

current_draft = st.session_state["unit_drafts"].get(selected_unit, "")
current_ch_title = st.session_state["chapter_titles"].get(selected_unit, "")
if current_draft:
    label = current_ch_title if current_ch_title else (
        "UNIT 13 · 에필로그" if selected_unit == "13" else f"UNIT {selected_unit}"
    )
    with st.expander(f"{label} 보기", expanded=True):
        st.text_area("원고", value=current_draft, height=420, label_visibility="collapsed")

# 품질 리포트 표시
qr = st.session_state.get("quality_report", {})
if qr.get("issues") or qr.get("stats"):
    with st.expander("📊 품질 리포트", expanded=True):
        stats = qr.get("stats", {})
        if stats:
            stat_cols = st.columns(4)
            stat_items = list(stats.items())
            for idx, (k, v) in enumerate(stat_items[:4]):
                with stat_cols[idx]:
                    st.metric(k, v)
            if len(stat_items) > 4:
                stat_cols2 = st.columns(4)
                for idx, (k, v) in enumerate(stat_items[4:8]):
                    with stat_cols2[idx]:
                        st.metric(k, v)
        issues = qr.get("issues", [])
        if issues:
            for issue in issues:
                st.warning(issue)
        else:
            st.success("✅ 주요 품질 문제 없음")

# Unit 요약 표시
summaries = st.session_state.get("unit_summaries", {})
filled = {k: v for k, v in summaries.items() if v}
if filled:
    with st.expander("📋 Unit 요약 (전체 흐름)", expanded=False):
        for key in sorted(filled.keys()):
            st.markdown(f"**UNIT {key}**: {filled[key]}")

# 캐릭터 등장 추적 표시
char_report = get_character_report()
if char_report.get("first_appearance"):
    with st.expander(f"👥 캐릭터 등장 추적 ({char_report.get('total', 0)}명)", expanded=False):
        fa = char_report["first_appearance"]
        for name in sorted(fa.keys(), key=lambda x: fa[x]):
            st.markdown(f"- **{name}** — 첫 등장: UNIT {fa[name]}")
        warnings = char_report.get("warnings", [])
        if warnings:
            st.markdown("---")
            for w in warnings:
                st.warning(w)

# ─────────────────────────────────────
# STEP 6
# ─────────────────────────────────────
st.markdown('<div class="section-header">🏷️ STEP 6 · 가제 검토 / 제목 제안</div>', unsafe_allow_html=True)

title_col1, title_col2 = st.columns([1, 1])

with title_col1:
    if st.button("원고 기반 제목 검토", use_container_width=True):
        def _job():
            prompt = build_title_review_prompt(
                current_title=working_title,
                overview=overview,
                synopsis=synopsis,
                story_reinforcement_merged=story_merged_text,
                all_blueprints_text=all_blueprints_text,
                all_drafts_text=gather_all_drafts_text(),
                style_dna=st.session_state["style_dna"],
            )
            return llm_call(prompt, max_tokens=MAX_TOKENS_MID)

        result = run_with_status(
            "원고를 다시 읽고 제목을 검토 중입니다...",
            "제목 검토 / 대안 제안이 완료되었습니다.",
            _job,
        )
        if result is not None:
            st.session_state["title_review"] = result

with title_col2:
    st.markdown(
        '<div class="small-meta">가제를 버리는 단계가 아니라, 원고를 읽고 현재 가제가 맞는지 검토하고 대안을 비교하는 단계입니다.</div>',
        unsafe_allow_html=True,
    )

if st.session_state["title_review"]:
    with st.expander("제목 검토 / 대안 보기", expanded=True):
        st.markdown(st.session_state["title_review"])

# ─────────────────────────────────────
# STEP 7
# ─────────────────────────────────────
st.markdown('<div class="section-header">💾 STEP 7 · 저장 / 내보내기</div>', unsafe_allow_html=True)

safe_title = safe_filename(working_title)
manuscript = final_manuscript_text(working_title)

current_unit_text = st.session_state["unit_drafts"].get(selected_unit, "").strip()
current_unit_label = "UNIT_13_에필로그" if selected_unit == "13" else f"UNIT_{selected_unit}"

txt_bytes = export_txt(manuscript) if manuscript.strip() else b""
docx_bytes = export_docx(working_title or "Novel Draft", manuscript) if manuscript.strip() else b""

unit_txt_bytes = export_txt(current_unit_text) if current_unit_text else b""
unit_docx_bytes = (
    export_docx(f"{working_title or 'Novel Draft'} {current_unit_label}", current_unit_text)
    if current_unit_text
    else b""
)

if not manuscript.strip():
    st.warning("아직 저장할 최종 원고가 없습니다. 먼저 Unit 원고를 생성해 주세요.")
else:
    st.info("다운로드 버튼을 누르면 브라우저로 바로 저장됩니다.")

st.markdown("**현재 Unit 저장**")
u1, u2 = st.columns(2)

with u1:
    st.download_button(
        "현재 Unit TXT 저장",
        data=unit_txt_bytes,
        file_name=f"{safe_title}_{current_unit_label}.txt",
        mime="text/plain",
        use_container_width=True,
        disabled=not bool(current_unit_text),
        key=f"download_unit_txt_{selected_unit}",
    )

with u2:
    st.download_button(
        "현재 Unit DOCX 저장",
        data=unit_docx_bytes,
        file_name=f"{safe_title}_{current_unit_label}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
        disabled=not bool(current_unit_text),
        key=f"download_unit_docx_{selected_unit}",
    )

st.markdown("**최종 원고 저장**")
exp1, exp2 = st.columns(2)

with exp1:
    st.download_button(
        "최종 원고 TXT 저장",
        data=txt_bytes,
        file_name=f"{safe_title}_final.txt",
        mime="text/plain",
        use_container_width=True,
        disabled=not bool(manuscript.strip()),
        key="download_final_txt",
    )

with exp2:
    st.download_button(
        "최종 원고 DOCX 저장",
        data=docx_bytes,
        file_name=f"{safe_title}_final.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
        disabled=not bool(manuscript.strip()),
        key="download_final_docx",
    )

with st.expander("최종 원고 미리보기", expanded=False):
    st.text_area("최종 원고", value=manuscript, height=420, label_visibility="collapsed")
