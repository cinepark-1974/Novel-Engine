from __future__ import annotations

import os
from datetime import datetime
from io import BytesIO
from typing import Dict, List

import streamlit as st

try:
    from anthropic import Anthropic
except ImportError:  # pragma: no cover
    Anthropic = None

from prompt import (
    SYSTEM_PROMPT,
    build_gap_diagnosis_prompt,
    build_intake_merge_prompt,
    build_rewrite_prompt,
    build_story_reinforcement_prompt,
    build_unit_draft_prompt,
    build_unit_plan_prompt,
)

APP_TITLE = "BLUE JEANS NOVEL ENGINE"
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")
GENRES = ["드라마", "스릴러", "느와르", "멜로/로맨스", "미스터리", "액션", "SF/판타지"]
REWRITE_MODES = [
    "더 상업적으로",
    "더 빠르게",
    "더 감정적으로",
    "더 차갑게",
    "더 스릴러답게",
    "더 여성서사 중심으로",
    "더 영상적으로",
]


def init_state() -> None:
    defaults = {
        "title": "",
        "genre": "스릴러",
        "style_note": "시드니 셀던 스타일의 대중 장편소설 감각. 영상화 가능한 장면 추진력 유지.",
        "chunk_1": "",
        "chunk_2": "",
        "chunk_3": "",
        "chunk_4": "",
        "merged_summary": "",
        "gap_report": "",
        "reinforced_story": "",
        "unit_plan": "",
        "current_unit": 1,
        "current_draft": "",
        "unit_drafts": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_client():
    api_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY"))
    if not api_key or Anthropic is None:
        return None
    return Anthropic(api_key=api_key)


def ask_model(prompt: str, max_tokens: int = 7000) -> str:
    client = get_client()
    if client is None:
        return "❌ ANTHROPIC_API_KEY가 없거나 anthropic 패키지가 설치되지 않았습니다."
    try:
        resp = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=max_tokens,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        parts = []
        for block in resp.content:
            text = getattr(block, "text", "")
            if text:
                parts.append(text)
        return "".join(parts).strip()
    except Exception as exc:  # pragma: no cover
        return f"❌ 오류: {exc}"


def collect_chunks() -> List[str]:
    return [
        st.session_state.get("chunk_1", ""),
        st.session_state.get("chunk_2", ""),
        st.session_state.get("chunk_3", ""),
        st.session_state.get("chunk_4", ""),
    ]


def previous_unit_summary(unit_number: int) -> str:
    if unit_number <= 1:
        return ""
    drafts: Dict[int, str] = st.session_state.get("unit_drafts", {})
    prev = drafts.get(unit_number - 1, "")
    if not prev:
        return ""
    return prev[-2500:]


def all_drafts_text() -> str:
    drafts: Dict[int, str] = st.session_state.get("unit_drafts", {})
    blocks = []
    for unit_no in sorted(drafts.keys()):
        blocks.append(f"{'='*60}\nUNIT {unit_no:02d}\n{'='*60}\n\n{drafts[unit_no]}")
    return "\n\n\n".join(blocks)


def make_docx_bytes(title: str, genre: str, drafts: Dict[int, str]) -> bytes:
    from docx import Document as DocxDocument
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt, RGBColor

    doc = DocxDocument()
    style = doc.styles["Normal"]
    style.font.name = "맑은 고딕"
    style.font.size = Pt(10)
    style.paragraph_format.space_after = Pt(4)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("BLUE JEANS PICTURES")
    r.font.size = Pt(10)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x19, 0x19, 0x70)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("NOVEL ENGINE")
    r.font.size = Pt(26)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x19, 0x19, 0x70)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"제목: {title or '-'} | 장르: {genre}")
    r.font.size = Pt(10)

    doc.add_page_break()

    for unit_no in sorted(drafts.keys()):
        h = doc.add_heading(f"Unit {unit_no:02d}", level=1)
        for run in h.runs:
            run.font.color.rgb = RGBColor(0x19, 0x19, 0x70)
        for line in drafts[unit_no].split("\n"):
            doc.add_paragraph(line)
        doc.add_page_break()

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


init_state()
st.set_page_config(page_title=APP_TITLE, page_icon="👖", layout="wide")

st.markdown(
    "<div style='text-align:center;padding:1rem 0 0 0'>"
    "<div style='font-size:13px;letter-spacing:4px;color:#191970;font-weight:700'>BLUE JEANS PICTURES</div>"
    "<div style='font-size:34px;font-weight:800;margin-top:4px'>NOVEL ENGINE</div>"
    "<div style='font-size:12px;color:#666;margin-top:6px'>Simple UI · Planning Doc In · Novel Out</div>"
    "</div>",
    unsafe_allow_html=True,
)

st.markdown("---")

left, right = st.columns([1.2, 1])
with left:
    st.session_state["title"] = st.text_input("작품 제목", value=st.session_state["title"])
with right:
    st.session_state["genre"] = st.selectbox("장르", GENRES, index=GENRES.index(st.session_state["genre"]))

st.session_state["style_note"] = st.text_area(
    "문체 / 방향",
    value=st.session_state["style_note"],
    height=80,
    help="길게 쓰지 않아도 됩니다. 예: 시드니 셀던 스타일의 대중 장편소설 감각, 영화적 추진력 유지",
)

st.markdown("### STEP 1 · 기획서 입력")
st.caption("기획서를 4개 조각까지 나누어 붙여넣으세요. 나머지 분석과 대안 제시는 프로그램이 맡습니다.")

c1, c2 = st.columns(2)
with c1:
    st.session_state["chunk_1"] = st.text_area("기획서 조각 1", value=st.session_state["chunk_1"], height=180)
    st.session_state["chunk_3"] = st.text_area("기획서 조각 3", value=st.session_state["chunk_3"], height=180)
with c2:
    st.session_state["chunk_2"] = st.text_area("기획서 조각 2", value=st.session_state["chunk_2"], height=180)
    st.session_state["chunk_4"] = st.text_area("기획서 조각 4", value=st.session_state["chunk_4"], height=180)

st.markdown("### STEP 2 · 분석과 설계")
col_a, col_b, col_c, col_d = st.columns(4)

if col_a.button("기획서 분석", use_container_width=True):
    prompt = build_intake_merge_prompt(st.session_state["title"], st.session_state["genre"], st.session_state["style_note"], collect_chunks())
    st.session_state["merged_summary"] = ask_model(prompt, max_tokens=5000)

if col_b.button("부족한 점 진단", use_container_width=True):
    prompt = build_gap_diagnosis_prompt(st.session_state["title"], st.session_state["genre"], st.session_state["merged_summary"])
    st.session_state["gap_report"] = ask_model(prompt, max_tokens=5000)

if col_c.button("전체 줄거리 보강", use_container_width=True):
    prompt = build_story_reinforcement_prompt(
        st.session_state["title"],
        st.session_state["genre"],
        st.session_state["merged_summary"],
        st.session_state["gap_report"],
    )
    st.session_state["reinforced_story"] = ask_model(prompt, max_tokens=6500)

if col_d.button("12 Unit 생성", use_container_width=True):
    prompt = build_unit_plan_prompt(st.session_state["title"], st.session_state["genre"], st.session_state["reinforced_story"])
    st.session_state["unit_plan"] = ask_model(prompt, max_tokens=6500)

r1, r2 = st.columns(2)
with r1:
    st.text_area("통합 요약", value=st.session_state["merged_summary"], height=280)
    st.text_area("전체 줄거리 보강", value=st.session_state["reinforced_story"], height=320)
with r2:
    st.text_area("부족한 점 진단", value=st.session_state["gap_report"], height=280)
    st.text_area("12 Unit 설계", value=st.session_state["unit_plan"], height=320)

st.markdown("### STEP 3 · Unit 집필")
cu1, cu2, cu3 = st.columns([1, 1, 2])
with cu1:
    st.session_state["current_unit"] = st.number_input("Unit 번호", min_value=1, max_value=12, value=int(st.session_state["current_unit"]), step=1)
with cu2:
    rewrite_mode = st.selectbox("다시 쓰기 모드", REWRITE_MODES)
with cu3:
    st.caption("권장 순서: 분석 → 진단 → 보강 → 12 Unit 생성 → Unit 1부터 집필")

w1, w2 = st.columns(2)
if w1.button("선택 Unit 쓰기", use_container_width=True):
    prompt = build_unit_draft_prompt(
        st.session_state["title"],
        st.session_state["genre"],
        st.session_state["style_note"],
        st.session_state["reinforced_story"],
        st.session_state["unit_plan"],
        int(st.session_state["current_unit"]),
        previous_unit_summary(int(st.session_state["current_unit"])),
    )
    result = ask_model(prompt, max_tokens=8000)
    st.session_state["current_draft"] = result
    drafts = dict(st.session_state.get("unit_drafts", {}))
    drafts[int(st.session_state["current_unit"])] = result
    st.session_state["unit_drafts"] = drafts

if w2.button("선택 Unit 다시 쓰기", use_container_width=True):
    current_text = st.session_state.get("current_draft", "")
    if current_text.strip():
        rewritten = ask_model(build_rewrite_prompt(rewrite_mode, current_text), max_tokens=8000)
        st.session_state["current_draft"] = rewritten
        drafts = dict(st.session_state.get("unit_drafts", {}))
        drafts[int(st.session_state["current_unit"])] = rewritten
        st.session_state["unit_drafts"] = drafts

st.text_area("현재 Unit 원고", value=st.session_state["current_draft"], height=420)

st.markdown("### STEP 4 · 저장")
drafts = st.session_state.get("unit_drafts", {})
if drafts:
    txt_data = all_drafts_text()
    dl1, dl2 = st.columns(2)
    with dl1:
        st.download_button(
            label=f"TXT 저장 ({len(drafts)}/12 Units)",
            data=txt_data,
            file_name=f"novel_{st.session_state['genre']}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with dl2:
        try:
            docx_bytes = make_docx_bytes(st.session_state["title"], st.session_state["genre"], drafts)
            st.download_button(
                label=f"DOCX 저장 ({len(drafts)}/12 Units)",
                data=docx_bytes,
                file_name=f"novel_{st.session_state['genre']}_{datetime.now().strftime('%Y%m%d_%H%M')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        except ImportError:
            st.caption("DOCX 저장을 위해 python-docx 설치가 필요합니다.")

st.markdown("---")
cr1, cr2 = st.columns([5, 1])
with cr2:
    if st.button("전체 초기화", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.caption("© 2026 BLUE JEANS PICTURES · Novel Engine v1.0")
