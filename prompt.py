"""BLUE JEANS NOVEL ENGINE v1.0
prompt.py — planning-doc-to-commercial-novel builders
"""

from __future__ import annotations

from typing import List

SYSTEM_PROMPT = """
당신은 BLUE JEANS NOVEL ENGINE이다.
당신의 역할은 사용자가 입력한 기획서, 시놉시스, 인물 문서, 세계관 문서를 분석하여
장편 대중소설 설계와 초안 집필을 돕는 것이다.

핵심 규칙:
- 설명보다 체험을 우선한다.
- 기획서 문장을 그대로 늘이지 말고 소설 문법으로 변환한다.
- 상업 장편소설의 흡입력과 영화서사의 추진력을 동시에 유지한다.
- 문장은 읽히기 쉬워야 하지만 얕아 보이면 안 된다.
- 장면, 선택, 대가, 비밀, 반전, 감정 변화가 지속적으로 작동해야 한다.
- 추상어를 남발하지 말고 사건과 행동으로 증명한다.
- Unit 마지막에는 다음 Unit으로 넘어가게 하는 압력을 남긴다.

출력 공통 규칙:
- 한국어.
- 실무적으로 바로 쓸 수 있게 제목과 소제목을 분명히 준다.
- 불필요한 장광설 금지.
- 같은 말을 반복하지 않는다.
- 작품을 더 강하게 만드는 구체적 대안을 준다.
""".strip()

NOVEL_THEORY_RULES = {
    "commercial": [
        "주인공 욕망은 초반에 선명해야 한다.",
        "각 Unit에는 기능이 있어야 한다.",
        "중반부를 버틸 갈등 연료를 반드시 설계한다.",
        "정보는 한 번에 설명하지 말고 사건과 대화 속에 분산한다.",
        "반전은 놀라움뿐 아니라 이전 정보의 재해석이어야 한다.",
        "엔딩은 플롯 정리보다 정서 회수가 중요하다.",
    ],
    "cinematic": [
        "오프닝 이미지는 강해야 한다.",
        "장면 전환은 시각적으로 선명해야 한다.",
        "행동과 선택이 서사를 끌고 가야 한다.",
        "세계관 설명은 장면화한다.",
    ],
    "unit": [
        "총 12 Units 기준으로 설계한다.",
        "각 Unit 목표 분량은 약 10,000자다.",
        "Unit마다 목적, 갈등, 감정 변화, 공개 정보, 숨긴 정보를 정리한다.",
    ],
}

UNIT_BLUEPRINTS = [
    {"unit": 1, "role": "오프닝 / 세계 진입 / 이상 징후"},
    {"unit": 2, "role": "문제 확대 / 목표 발생"},
    {"unit": 3, "role": "새 규칙 진입 / 전개 가속"},
    {"unit": 4, "role": "첫 승리 / 첫 대가"},
    {"unit": 5, "role": "관계 심화 / 위험 증폭"},
    {"unit": 6, "role": "중반 반전"},
    {"unit": 7, "role": "균열 / 오해 / 상실"},
    {"unit": 8, "role": "추락 / 붕괴"},
    {"unit": 9, "role": "재정렬 / 진실 접근"},
    {"unit": 10, "role": "결전 준비"},
    {"unit": 11, "role": "클라이맥스 진입"},
    {"unit": 12, "role": "결전 / 엔딩 / 여운"},
]


def _truncate(text: str, limit: int) -> str:
    return (text or "").strip()[:limit]


def _joined_chunks(chunks: List[str], limit_each: int = 5000) -> str:
    cleaned = []
    for i, chunk in enumerate(chunks, start=1):
        value = (chunk or "").strip()
        if value:
            cleaned.append(f"[기획서 조각 {i}]\n{value[:limit_each]}")
    return "\n\n".join(cleaned) if cleaned else "(입력 없음)"


def build_intake_merge_prompt(title: str, genre: str, style_note: str, chunks: List[str]) -> str:
    return f"""
[TASK] 기획서 통합 분석

[작품명]
{title}

[장르]
{genre}

[목표 문체 / 지향]
{_truncate(style_note, 1200) or '(기본값: 시드니 셀던 스타일의 대중 장편소설 감각)'}

[입력 자료]
{_joined_chunks(chunks, 4500)}

[요청]
입력된 기획서 조각들을 하나의 통합 요약본으로 재구성하라.

[반드시 포함할 것]
1. 작품 핵심 한 줄
2. 장르 정의
3. 주인공 / 적대자 / 핵심 관계 축
4. 세계관 핵심
5. 핵심 사건 흐름
6. 영상화 포인트
7. 소설화 시 가장 강한 매력 5개
8. 현재 기획서 상태에서 바로 보이는 리스크 5개

[출력 형식]
## 통합 요약
## 핵심 매력
## 즉시 보이는 리스크
""".strip()


def build_gap_diagnosis_prompt(title: str, genre: str, merged_summary: str) -> str:
    return f"""
[TASK] 장편화 부족 요소 진단

[작품명]
{title}

[장르]
{genre}

[통합 요약]
{_truncate(merged_summary, 12000)}

[요청]
이 작품을 12만자급 장편 대중소설로 확장한다고 가정하고, 부족한 점을 분석하라.

[진단 항목]
1. 주인공 욕망
2. 결핍 / 상처
3. 적대 구조
4. 중반부 연료
5. 관계축 밀도
6. 반전 포인트
7. 비밀 / 공개 타이밍
8. 엔딩 회수 장치
9. 영상성
10. 12 Unit 구조 적합성

[출력 형식]
## 강점
## 부족한 요소
## 장편화 위험
## 우선 보강해야 할 5개 항목
## 구체적 보강 제안
""".strip()


def build_story_reinforcement_prompt(title: str, genre: str, merged_summary: str, gap_report: str) -> str:
    return f"""
[TASK] 전체 줄거리 보강

[작품명]
{title}

[장르]
{genre}

[통합 요약]
{_truncate(merged_summary, 9000)}

[부족 요소 진단]
{_truncate(gap_report, 9000)}

[요청]
현재 기획서를 장편 대중소설로 확장하기 위해 전체 줄거리를 보강하라.

[목표]
- 12 Unit 장편 구조에 견딜 것
- 중반부가 약하지 않을 것
- 관계축과 배신, 반전, 대가가 강화될 것
- 영상화 가능한 장면성이 살아 있을 것

[출력 형식]
## 보강된 전체 줄거리
## 추가된 핵심 갈등
## 중반부 유지 장치
## 엔딩 회수 장치
## 작가 판단 포인트
""".strip()


def build_unit_plan_prompt(title: str, genre: str, reinforced_story: str) -> str:
    roles = "\n".join([f"- Unit {item['unit']:02d}: {item['role']}" for item in UNIT_BLUEPRINTS])
    return f"""
[TASK] 12 Unit 설계

[작품명]
{title}

[장르]
{genre}

[보강된 전체 줄거리]
{_truncate(reinforced_story, 12000)}

[기본 Unit 역할]
{roles}

[요청]
이 작품을 총 12 Units로 설계하라. Unit당 목표 분량은 약 10,000자다.

[각 Unit마다 반드시 포함할 것]
- Unit 제목
- 기능
- 핵심 사건
- 감정 변화
- 공개 정보
- 숨긴 정보
- 엔딩 훅

[출력 형식]
Unit 01 ~ Unit 12를 각각 아래 포맷으로 작성:
### Unit 01. 제목
- 기능:
- 핵심 사건:
- 감정 변화:
- 공개 정보:
- 숨긴 정보:
- 엔딩 훅:
""".strip()


def build_unit_draft_prompt(
    title: str,
    genre: str,
    style_note: str,
    reinforced_story: str,
    unit_plan: str,
    unit_number: int,
    previous_unit_summary: str = "",
) -> str:
    return f"""
[TASK] Unit {unit_number:02d} 초안 집필

[작품명]
{title}

[장르]
{genre}

[문체 지향]
{_truncate(style_note, 1500) or '시드니 셀던 스타일의 대중 장편소설 감각'}

[보강된 전체 줄거리]
{_truncate(reinforced_story, 7000)}

[12 Unit 설계]
{_truncate(unit_plan, 12000)}

{f'[직전 Unit 요약]\n{_truncate(previous_unit_summary, 2500)}\n' if previous_unit_summary else ''}

[집필 규칙]
1. Unit {unit_number:02d}에 해당하는 내용만 쓴다.
2. 목표 분량은 약 8,000~10,000자 수준의 밀도를 지향하되, 초안 단계에서는 핵심 장면이 살아 있어야 한다.
3. 설명보다 장면, 행동, 대화, 선택을 우선한다.
4. 문체는 상업 장편소설답게 빠르고 선명하게 간다.
5. 마지막에는 다음 Unit으로 넘어가게 하는 엔딩 훅을 남긴다.
6. 소제목이나 번호를 남발하지 말고 소설 본문 형태로 써라.

[출력 형식]
## Unit {unit_number:02d} Draft
(바로 소설 원고 본문 시작)
""".strip()


def build_rewrite_prompt(mode: str, text: str) -> str:
    return f"""
[TASK] 소설 원고 리라이트

[리라이트 모드]
{mode}

[원고]
{_truncate(text, 15000)}

[요청]
원고의 내용은 유지하되 아래 방향으로 다시 써라.

가능한 모드 예시:
- 더 상업적으로
- 더 빠르게
- 더 감정적으로
- 더 차갑게
- 더 스릴러답게
- 더 여성서사 중심으로
- 더 영상적으로

[출력 형식]
## Rewrite
(리라이트 본문)
""".strip()
