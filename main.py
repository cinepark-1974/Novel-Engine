from __future__ import annotations

from io import BytesIO
from typing import Dict

import streamlit as st
from anthropic import Anthropic
from docx import Document

from prompt import (
    SYSTEM_PROMPT,
    build_epilogue_prompt,
    build_gap_diagnosis_prompt,
    build_intake_merge_prompt,
    build_rewrite_prompt,
    build_story_reinforcement_prompt,
    build_title_review_prompt,
    build_unit_draft_prompt,
    build_unit_plan_prompt,
)

APP_TITLE = "BLUE JEANS NOVEL ENGINE"
ANTHROPIC_MODEL = "claude-sonnet-4-6"
DEFAULT_STYLE = "시드니 셀던 스타일의 대중 장편소설 감각. 빠르게 읽히고, 장면이 선명하며, 챕터 말미 후킹이 강한 문체."

st.set_page_config(page_title=APP_TITLE, page_icon="👖", layout="wide", initial_sidebar_state="collapsed")

DEFAULT_STATE = {
    "title": "",
    "working_title": "",
    "genre": "스릴러",
    "style_note": DEFAULT_STYLE,
    "overview": "",
    "characters": "",
    "synopsis": "",
    "extra_notes": "",
    "merged_summary": "",
    "gap_report": "",
    "reinforced_story": "",
    "unit_plan": "",
    "selected_unit": 1,
    "rewrite_mode": "더 상업적으로",
    "unit_drafts": {},
    "title_review": "",
}
for k, v in DEFAULT_STATE.items():
    st.session_state.setdefault(k, v)

st.markdown(
    """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
@import url('https://cdn.jsdelivr.net/gh/projectnoonnu/2408-3@latest/Paperlogy.css');
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&display=swap');
:root {
    --navy:#202A78; --y:#FFCB05; --bg:#F7F7F5; --card:#FFFFFF; --card-border:#DDDDE6;
    --t:#2A2A3A; --dim:#8A8FA3; --light-bg:#EEEEF6; --display:'Playfair Display','Paperlogy','Georgia',serif;
    --body:'Pretendard',-apple-system,BlinkMacSystemFont,sans-serif; --heading:'Paperlogy','Pretendard',sans-serif;
}
html, body, [class*="css"] { font-family:var(--body); color:var(--t); -webkit-font-smoothing:antialiased; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stMainBlockContainer"], [data-testid="stHeader"], [data-testid="stBottom"] { background-color:var(--bg)!important; color:var(--t)!important; }
section[data-testid="stSidebar"] { display:none; }
h1,h2,h3,h4,h5,h6 { color:var(--navy)!important; font-family:var(--heading)!important; }
p, span, label, div, li { color:var(--t); }
.stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div {
    background-color:var(--card)!important; color:var(--t)!important; border:1.5px solid var(--card-border)!important;
    border-radius:8px!important; font-family:var(--body)!important;
}
.stButton > button, .stDownloadButton > button {
    border-radius:8px!important; font-weight:800!important; border:1.5px solid var(--card-border)!important;
}
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"], .stDownloadButton > button {
    background-color:var(--y)!important; color:var(--navy)!important; border-color:var(--y)!important;
}
.brand-wrap { text-align:center; margin:0 0 1.3rem 0; }
.header { font-size:0.74rem; font-weight:700; color:var(--navy); letter-spacing:0.23em; font-family:var(--heading); }
.brand-title { font-size:2.15rem; font-weight:900; color:var(--navy); font-family:var(--display); letter-spacing:-0.02em; display:inline-block; position:relative; }
.brand-title::after { content:''; position:absolute; left:0; bottom:1px; width:100%; height:4px; background:var(--y); border-radius:2px; }
.sub { font-size:0.68rem; color:var(--dim); letter-spacing:0.18em; margin-top:.45rem; }
.section-header { background:var(--y); color:var(--navy); padding:.65rem 1rem; border-radius:6px; font-weight:800; font-size:1rem; font-family:var(--heading); margin:1.25rem 0 .8rem 0; display:flex; justify-content:space-between; align-items:center; }
.section-header .en { font-family:var(--display); font-size:.75rem; opacity:.8; }
.callout { background:var(--light-bg); border-left:4px solid var(--navy); padding:.95rem 1rem; border-radius:0 8px 8px 0; margin:.45rem 0 1rem 0; }
.small-meta { font-size:.78rem; color:var(--dim); margin-top:-.15rem; margin-bottom:.55rem; }
</style>
""",
    unsafe_allow_html=True,
)


def sec(title: str, en: str) -> None:
    st.markdown(f'<div class="section-header"><span>{title}</span><span class="en">{en}</span></div>', unsafe_allow_html=True)


def llm(prompt_text: str) -> str:
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.error("ANTHROPIC_API_KEY가 설정되어 있지 않습니다.")
        st.stop()
    client = Anthropic(api_key=api_key)
    res = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=6400,
        temperature=0.8,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt_text}],
    )
    return "".join(block.text for block in res.content if getattr(block, "type", "") == "text").strip()


def summarize_for_context(text: str, max_chars: int = 1200) -> str:
    t = (text or "").strip()
    if len(t) <= max_chars:
        return t
    return t[:max_chars].rstrip() + "\n..."


def ensure_final_line(text: str) -> str:
    body = (text or "").rstrip()
    if body.endswith("끝."):
        return body
    return f"{body}\n\n끝."


def can_generate_unit(unit_no: int) -> bool:
    if unit_no == 13:
        return bool(st.session_state["unit_drafts"].get(12))
    return bool(st.session_state["unit_plan"] and st.session_state["reinforced_story"])


def build_full_export_text() -> str:
    parts = []
    for i in range(1, 14):
        txt = st.session_state["unit_drafts"].get(i, "").strip()
        if txt:
            label = f"UNIT {i:02d}" if i < 13 else "UNIT 13 · 에필로그"
            parts.append(f"{label}\n\n{txt}")
    full = "\n\n".join(parts).strip()
    if full and (st.session_state["unit_drafts"].get(12) or st.session_state["unit_drafts"].get(13)):
        full = ensure_final_line(full)
    return full


def build_docx_bytes(text: str) -> bytes:
    doc = Document()
    for para in text.split("\n"):
        doc.add_paragraph(para)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio.read()


st.markdown(
    """
<div class="brand-wrap">
  <div class="header">BLUE JEANS PICTURES</div>
  <div class="brand-title">NOVEL ENGINE</div>
  <div class="sub">CINEMATIC · COMMERCIAL · LONG-FORM</div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="callout"><b>FLOW TIP</b><br>입력 → 통합 분석 → 부족한 점 진단 → 전체 줄거리 보강 → 12 Unit 설계 → Unit 원고 생성 → 필요하면 Unit 13 에필로그 → 저장 → 제목 검토 순서로 진행합니다.</div>',
    unsafe_allow_html=True,
)

sec("STEP 1 · 기획서 입력", "INTAKE")
col1, col2 = st.columns(2)
with col1:
    st.session_state["title"] = st.text_input("작품명", value=st.session_state["title"], placeholder="예: 머지 앤 어퀴지션")
with col2:
    st.session_state["genre"] = st.selectbox("장르", ["스릴러", "미스터리", "로맨스", "역사", "첩보", "금융", "범죄", "드라마", "SF", "기타"], index=["스릴러", "미스터리", "로맨스", "역사", "첩보", "금융", "범죄", "드라마", "SF", "기타"].index(st.session_state["genre"]) if st.session_state["genre"] in ["스릴러", "미스터리", "로맨스", "역사", "첩보", "금융", "범죄", "드라마", "SF", "기타"] else 0)
col3, col4 = st.columns([1, 2])
with col3:
    st.session_state["working_title"] = st.text_input("현재 가제", value=st.session_state["working_title"], placeholder="예: 감각구역")
with col4:
    st.session_state["style_note"] = st.text_input("문체 지향", value=st.session_state["style_note"])

st.session_state["overview"] = st.text_area("작품 개요", value=st.session_state["overview"], height=180, placeholder="로그라인, 기획의도, 세계관, 핵심 질문")
col5, col6 = st.columns(2)
with col5:
    st.session_state["characters"] = st.text_area("캐릭터", value=st.session_state["characters"], height=220, placeholder="주인공, 적대자, 조력자, 관계, 욕망, 결핍, 비밀")
with col6:
    st.session_state["synopsis"] = st.text_area("줄거리 / 트리트먼트", value=st.session_state["synopsis"], height=220, placeholder="시작, 중반, 위기, 클라이맥스, 결말 방향")
st.session_state["extra_notes"] = st.text_area("추가 메모(선택)", value=st.session_state["extra_notes"], height=140, placeholder="꼭 살릴 장면, 참고 문체, 조사 메모, 약한 부분")

sec("STEP 2 · 분석과 설계", "ANALYSIS")
btn1, btn2, btn3, btn4 = st.columns(4)
with btn1:
    if st.button("기획서 통합 분석", use_container_width=True, type="primary"):
        prompt_text = build_intake_merge_prompt(
            st.session_state["title"], st.session_state["genre"], st.session_state["working_title"], st.session_state["style_note"],
            st.session_state["overview"], st.session_state["characters"], st.session_state["synopsis"], st.session_state["extra_notes"],
        )
        with st.spinner("통합 분석 중..."):
            st.session_state["merged_summary"] = llm(prompt_text)
with btn2:
    if st.button("부족한 점 진단", use_container_width=True, disabled=not st.session_state["merged_summary"]):
        with st.spinner("부족한 점 진단 중..."):
            st.session_state["gap_report"] = llm(build_gap_diagnosis_prompt(st.session_state["title"], st.session_state["genre"], st.session_state["merged_summary"]))
with btn3:
    if st.button("전체 줄거리 보강", use_container_width=True, disabled=not (st.session_state["merged_summary"] and st.session_state["gap_report"])):
        with st.spinner("전체 줄거리 보강 중..."):
            st.session_state["reinforced_story"] = llm(build_story_reinforcement_prompt(st.session_state["title"], st.session_state["genre"], st.session_state["merged_summary"], st.session_state["gap_report"]))
with btn4:
    if st.button("12 Unit 설계", use_container_width=True, disabled=not st.session_state["reinforced_story"]):
        with st.spinner("12 Unit 설계 중..."):
            st.session_state["unit_plan"] = llm(build_unit_plan_prompt(st.session_state["title"], st.session_state["genre"], st.session_state["reinforced_story"]))

if st.session_state["merged_summary"]:
    st.markdown("### 통합 분석")
    st.write(st.session_state["merged_summary"])
if st.session_state["gap_report"]:
    st.markdown("### 부족한 점 진단")
    st.write(st.session_state["gap_report"])
if st.session_state["reinforced_story"]:
    st.markdown("### 전체 줄거리 보강")
    st.write(st.session_state["reinforced_story"])
if st.session_state["unit_plan"]:
    st.markdown("### 12 Unit 설계")
    st.write(st.session_state["unit_plan"])

sec("STEP 3 · Unit 집필", "DRAFT")
unit_options = list(range(1, 13)) + [13]
unit_labels = {i: f"UNIT {i:02d}" for i in range(1, 13)}
unit_labels[13] = "UNIT 13 · 에필로그"
col7, col8 = st.columns([1, 1])
with col7:
    selected = st.selectbox("집필할 Unit 선택", unit_options, index=unit_options.index(st.session_state["selected_unit"]), format_func=lambda x: unit_labels[x])
    st.session_state["selected_unit"] = selected
with col8:
    st.session_state["rewrite_mode"] = st.selectbox("다시 쓰기 모드", ["더 상업적으로", "더 감정적으로", "더 빠르게", "더 차갑게", "더 문학적으로", "더 영상적으로"], index=["더 상업적으로", "더 감정적으로", "더 빠르게", "더 차갑게", "더 문학적으로", "더 영상적으로"].index(st.session_state["rewrite_mode"]) if st.session_state["rewrite_mode"] in ["더 상업적으로", "더 감정적으로", "더 빠르게", "더 차갑게", "더 문학적으로", "더 영상적으로"] else 0)

prev_summary = summarize_for_context(st.session_state["unit_drafts"].get(selected - 1, "")) if selected > 1 else ""
if selected == 13:
    st.markdown('<div class="callout"><b>EPILOGUE RULE</b><br>UNIT 13은 선택형 에필로그입니다. UNIT 12가 먼저 완성되어 있어야 하며, 약 2페이지 분량으로 정서적 여운과 최종 이미지를 제공합니다.</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    if st.button("Unit 원고 생성", use_container_width=True, type="primary", disabled=not can_generate_unit(selected)):
        with st.spinner("원고 생성 중..."):
            if selected == 13:
                draft = llm(build_epilogue_prompt(
                    st.session_state["title"], st.session_state["genre"], st.session_state["working_title"], st.session_state["style_note"],
                    st.session_state["reinforced_story"], st.session_state["unit_plan"], st.session_state["unit_drafts"].get(12, "")
                ))
                draft = ensure_final_line(draft)
            else:
                draft = llm(build_unit_draft_prompt(
                    st.session_state["title"], st.session_state["genre"], st.session_state["working_title"], st.session_state["style_note"],
                    st.session_state["reinforced_story"], st.session_state["unit_plan"], selected, prev_summary,
                ))
                if selected == 12 and 13 not in st.session_state["unit_drafts"]:
                    # main story must still feel closed even without epilogue.
                    draft = draft.rstrip()
            st.session_state["unit_drafts"][selected] = draft
with c2:
    if st.button("현재 Unit 다시 쓰기", use_container_width=True, disabled=not st.session_state["unit_drafts"].get(selected)):
        with st.spinner("다시 쓰는 중..."):
            rewritten = llm(build_rewrite_prompt(
                st.session_state["rewrite_mode"], st.session_state["unit_drafts"].get(selected, ""), st.session_state["title"], st.session_state["genre"], st.session_state["style_note"]
            ))
            if selected == 13:
                rewritten = ensure_final_line(rewritten)
            st.session_state["unit_drafts"][selected] = rewritten

current_text = st.session_state["unit_drafts"].get(selected, "")
st.text_area("원고", value=current_text, height=500, key=f"draft_view_{selected}")

sec("STEP 4 · 저장하기", "EXPORT")
export_text = build_full_export_text()
col9, col10 = st.columns(2)
with col9:
    st.download_button("TXT 저장", data=export_text.encode("utf-8"), file_name=f"{(st.session_state['working_title'] or st.session_state['title'] or 'novel')}.txt", mime="text/plain", use_container_width=True, disabled=not export_text)
with col10:
    st.download_button("DOCX 저장", data=build_docx_bytes(export_text) if export_text else b"", file_name=f"{(st.session_state['working_title'] or st.session_state['title'] or 'novel')}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True, disabled=not export_text)

sec("STEP 5 · 제목 검토 / 제안", "TITLE REVIEW AFTER DRAFT")
st.markdown('<div class="callout"><b>TITLE LOGIC</b><br>이 단계는 현재 가제를 버리는 기능이 아니라, 완성된 설계와 생성 원고를 다시 읽고 가제를 유지할지, 보강할지, 더 강한 대안을 붙일지 검토하는 단계입니다.</div>', unsafe_allow_html=True)
if st.button("원고 기반 제목 검토 / 제안", use_container_width=True, disabled=not export_text):
    with st.spinner("제목 검토 중..."):
        st.session_state["title_review"] = llm(build_title_review_prompt(
            st.session_state["title"], st.session_state["working_title"], st.session_state["genre"], st.session_state["reinforced_story"], st.session_state["unit_plan"], export_text
        ))
if st.session_state["title_review"]:
    st.write(st.session_state["title_review"])
