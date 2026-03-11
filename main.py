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
    build_merge_analysis_prompt,
    build_gap_diagnosis_prompt,
    build_story_reinforcement_prompt,
    build_unit_blueprint_prompt,
    build_unit_draft_prompt,
    build_unit_rewrite_prompt,
    build_title_review_prompt,
    build_epilogue_prompt,
    build_expand_incomplete_unit_prompt,
)

# ─────────────────────────────────────
# Page Config
# ─────────────────────────────────────
st.set_page_config(
    page_title="BLUE JEANS · Novel Engine",
    page_icon="👖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────
# CSS
# ─────────────────────────────────────
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
@import url('https://cdn.jsdelivr.net/gh/projectnoonnu/2408-3@latest/Paperlogy.css');
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&display=swap');

:root {
    --navy: #191970; --y: #FFCB05; --bg: #F7F7F5;
    --card: #FFFFFF; --card-border: #E2E2E0; --t: #1A1A2E;
    --g: #2EC484; --dim: #8E8E99; --light-bg: #EEEEF6;
    --display: 'Playfair Display', 'Paperlogy', 'Georgia', serif;
    --body: 'Pretendard', -apple-system, sans-serif;
    --heading: 'Paperlogy', 'Pretendard', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--body); color: var(--t); -webkit-font-smoothing: antialiased;
}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stMainBlockContainer"], [data-testid="stHeader"],
[data-testid="stBottom"] {
    background-color: var(--bg) !important; color: var(--t) !important;
}
.stMarkdown, .stText, .stCode { color: var(--t) !important; }
h1,h2,h3,h4,h5,h6 { color: var(--navy) !important; font-family: var(--heading) !important; }
p, span, label, div, li { color: inherit; }
section[data-testid="stSidebar"] { display: none; }

.stTextInput input, .stTextArea textarea,
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
    background-color: var(--card) !important; color: var(--t) !important;
    border: 1.5px solid var(--card-border) !important; border-radius: 8px !important;
    font-family: var(--body) !important; font-size: 0.92rem !important;
    padding: 0.65rem 0.85rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus,
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
    border-color: var(--navy) !important;
    box-shadow: 0 0 0 2px rgba(25,25,112,0.08) !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder,
[data-testid="stTextInput"] input::placeholder, [data-testid="stTextArea"] textarea::placeholder {
    color: var(--dim) !important; font-size: 0.85rem !important;
}
.stSelectbox > div > div, [data-baseweb="select"] > div, [data-baseweb="select"] input {
    background-color: var(--card) !important; color: var(--t) !important;
    border-color: var(--card-border) !important; border-radius: 8px !important;
}
[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"], [role="option"] {
    background-color: var(--card) !important; color: var(--t) !important;
}
[role="option"]:hover { background-color: var(--light-bg) !important; }
.stTextInput label, .stTextArea label, .stSelectbox label {
    color: var(--t) !important; font-weight: 600 !important;
    font-size: 0.82rem !important; margin-bottom: 0.3rem !important;
}

.stButton > button {
    color: var(--t) !important; border: 1.5px solid var(--card-border) !important;
    background-color: var(--card) !important; border-radius: 8px !important;
    font-family: var(--body) !important; font-weight: 700 !important;
    font-size: 0.88rem !important; padding: 0.55rem 1.2rem !important;
    transition: all 0.2s;
}
.stButton > button:hover {
    border-color: var(--navy) !important;
    box-shadow: 0 2px 8px rgba(25,25,112,0.08) !important;
}
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background-color: var(--y) !important; color: var(--navy) !important;
    border-color: var(--y) !important; font-weight: 800 !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background-color: #E8B800 !important;
    box-shadow: 0 2px 12px rgba(255,203,5,0.3) !important;
}
.stDownloadButton > button {
    color: var(--navy) !important; border: 1.5px solid var(--y) !important;
    background-color: var(--y) !important; border-radius: 8px !important;
    font-family: var(--body) !important; font-weight: 800 !important;
    font-size: 0.88rem !important; padding: 0.55rem 1.2rem !important;
}
.stExpander, details, details summary {
    background-color: var(--card) !important; color: var(--t) !important;
    border: 1px solid var(--card-border) !important; border-radius: 8px !important;
}
details[open] > div { background-color: var(--card) !important; }
.stExpander summary, .stExpander summary span { color: var(--t) !important; }
.stAlert { color: var(--t) !important; border-radius: 8px !important; }
[data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"],
[data-testid="stColumn"] { background-color: transparent !important; }

.header {
    font-size: 0.85rem; font-weight: 700; color: var(--navy);
    letter-spacing: 0.15em; font-family: var(--heading);
}
.brand-title {
    font-size: 2.6rem; font-weight: 900; color: var(--navy);
    font-family: var(--display); letter-spacing: -0.02em;
    position: relative; display: inline-block;
}
.brand-title::after {
    content: ''; position: absolute; bottom: 2px; left: 0;
    width: 100%; height: 4px; background: var(--y); border-radius: 2px;
}
.sub {
    font-size: 0.7rem; color: var(--dim); letter-spacing: 0.15em;
    margin-top: 0.5rem; margin-bottom: 1.5rem;
}
.callout {
    background: var(--light-bg); border-left: 4px solid var(--navy);
    padding: 0.9rem 1.1rem; margin: 0.5rem 0;
    border-radius: 0 8px 8px 0; font-size: 0.88rem; color: var(--t);
}
.cl {
    color: var(--navy); font-weight: 700; font-size: 0.72rem;
    letter-spacing: 0.03em; margin-bottom: 0.3rem; text-transform: uppercase;
}
.section-header {
    background: var(--y); color: var(--navy);
    padding: 0.6rem 1rem; border-radius: 6px;
    font-weight: 800; font-size: 1rem; font-family: var(--heading);
    margin: 1.5rem 0 0.8rem 0;
    display: flex; justify-content: space-between; align-items: center;
}
.section-header .en {
    font-family: var(--display); font-size: 0.75rem;
    font-weight: 700; letter-spacing: 0.05em; opacity: 0.7;
}
.small-meta {
    font-size: 0.78rem; color: var(--dim);
    margin-top: -0.2rem; margin-bottom: 0.5rem;
}
.beat-tag {
    background: var(--navy); color: var(--y);
    display: inline-block; padding: 0.2rem 0.7rem;
    border-radius: 4px; font-size: 0.78rem; font-weight: 800;
    letter-spacing: 0.04em; margin-bottom: 0.4rem;
}
.act-tag {
    background: var(--navy); color: #fff;
    display: inline-block; padding: 0.25rem 0.8rem;
    border-radius: 4px; font-size: 0.82rem; font-weight: 800;
    letter-spacing: 0.06em;
}
</style>
""", unsafe_allow_html=True)

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

DEFAULT_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
MAX_TOKENS_SHORT = 3000
MAX_TOKENS_MID = 5000
MAX_TOKENS_LONG = 7000

def llm_call(user_prompt: str, max_tokens: int | None = None) -> str:
    if max_tokens is None:
        max_tokens = MAX_TOKENS_MID

    client = get_client()
    if client is None:
        return (
            "[오프라인 미리보기 모드]\n\n"
            "ANTHROPIC_API_KEY가 설정되지 않았거나 anthropic 패키지가 설치되지 않았습니다.\n"
            "실제 모델 호출 대신 프롬프트 초안만 구성된 상태입니다.\n\n"
            + user_prompt[:4000]
        )

    response = client.messages.create(
        model=DEFAULT_MODEL,
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
    drafts = st.session_state["unit_drafts"]
    merged = []
    for i in range(1, 14):
        key = f"{i:02d}" if i < 13 else "13"
        txt = drafts.get(key, "")
        if txt.strip():
            label = "UNIT 13 · 에필로그" if i == 13 else f"UNIT {i:02d}"
            merged.append(f"[{label}]\n{txt}")
    return merge_nonempty(merged)


def export_txt(content: str) -> bytes:
    return content.encode("utf-8")


def export_docx(title: str, content: str) -> bytes:
    doc = Document()
    doc.add_heading(title or "Novel Draft", level=1)
    for para in content.split("\n"):
        doc.add_paragraph(para)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio.read()


def final_manuscript_text(current_title: str) -> str:
    parts = []
    if current_title.strip():
        parts.append(current_title.strip())
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
    result = llm_call(prompt, max_tokens=MAX_TOKENS_LONG)
    result = ensure_final_ending(result, unit_no)

    if is_incomplete_text(result, unit_no):
        expand_prompt = build_expand_incomplete_unit_prompt(
            unit_no=unit_no,
            current_text=result,
            target_length=UNIT_TARGET_LENGTHS.get(unit_no, 8000),
            min_length=UNIT_MIN_LENGTHS.get(unit_no, 6000),
        )
        extra = llm_call(expand_prompt, max_tokens=MAX_TOKENS_MID)
        result = (result.rstrip() + "\n\n" + extra.strip()).strip()
        result = ensure_final_ending(result, unit_no)

    return result


# ─────────────────────────────────────
# HEADER
# ─────────────────────────────────────
st.markdown('<div class="header">BLUE JEANS PICTURES</div>', unsafe_allow_html=True)
st.markdown(f'<div class="brand-title">{APP_TITLE}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub">{APP_SUB}</div>', unsafe_allow_html=True)

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
st.markdown('<div class="section-header">STEP 1 · 작품 자료 입력</div>', unsafe_allow_html=True)

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

# ─────────────────────────────────────
# STEP 2
# ─────────────────────────────────────
st.markdown('<div class="section-header">STEP 2 · 문체 / 분석</div>', unsafe_allow_html=True)

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
st.markdown('<div class="section-header">STEP 3 · 전체 줄거리 보강 (기승전결 분할)</div>', unsafe_allow_html=True)

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
st.markdown('<div class="section-header">STEP 4 · 12 Unit 설계 (2 Unit씩 6개 버튼)</div>', unsafe_allow_html=True)

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
st.markdown('<div class="section-header">STEP 5 · Unit 원고 생성 / 다시 쓰기</div>', unsafe_allow_html=True)

unit_options = [f"{i:02d}" for i in range(1, 13)] + ["13"]
selected_unit = st.selectbox(
    "작업할 Unit 선택",
    unit_options,
    format_func=lambda x: "UNIT 13 · 에필로그" if x == "13" else f"UNIT {x}",
)

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
                    all_drafts_text=gather_all_drafts_text(),
                    style_dna=st.session_state["style_dna"],
                )
                return generate_or_expand_unit(13, prompt)

            result = run_with_status(
                "UNIT 13 에필로그를 생성 중입니다...",
                "UNIT 13 에필로그 생성이 완료되었습니다.",
                _job,
            )
            if result is not None:
                st.session_state["unit_drafts"][selected_unit] = result
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
                    previous_drafts=gather_all_drafts_text(),
                    style_dna=st.session_state["style_dna"],
                    style_strength=style_strength,
                    target_length=UNIT_TARGET_LENGTHS.get(unit_no, 8000),
                    min_length=UNIT_MIN_LENGTHS.get(unit_no, 6000),
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
                st.session_state["unit_drafts"][selected_unit] = result
                if is_incomplete_text(result, unit_no):
                    set_status(
                        f"UNIT {unit_no:02d}는 생성되었지만 아직 짧거나 미완성일 수 있습니다. 다시 쓰기나 재생성을 권장합니다.",
                        "warning",
                    )

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
if current_draft:
    label = "UNIT 13 · 에필로그" if selected_unit == "13" else f"UNIT {selected_unit}"
    with st.expander(f"{label} 보기", expanded=True):
        st.text_area("원고", value=current_draft, height=420, label_visibility="collapsed")

# ─────────────────────────────────────
# STEP 6
# ─────────────────────────────────────
st.markdown('<div class="section-header">STEP 6 · 가제 검토 / 제목 제안</div>', unsafe_allow_html=True)

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
st.markdown('<div class="section-header">STEP 7 · 저장 / 내보내기</div>', unsafe_allow_html=True)

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
