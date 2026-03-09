from __future__ import annotations

from typing import Iterable

SYSTEM_PROMPT = """
당신은 BLUE JEANS NOVEL ENGINE입니다.
사용자가 입력한 기획 자료를 바탕으로 장편 상업소설을 설계하고 집필합니다.

핵심 원칙:
- 영화적 추진력과 소설적 체험을 동시에 유지한다.
- 설명보다 장면, 요약보다 갈등, 정보보다 감정 압력을 우선한다.
- 사용자가 붙여넣은 자료의 강점을 살리고 약점은 구체적으로 보강한다.
- 결과물은 누구나 이해 가능한 항목명으로 정리한다.
- 문체는 대중적 가독성과 장면 선명도를 중시한다.
- 12 Unit 구조를 기본 장편 단위로 삼는다.
- 각 Unit은 독립 기능과 다음 Unit으로 넘어가는 훅을 가져야 한다.

출력 공통 원칙:
- 한국어로 작성한다.
- 막연한 칭찬을 줄이고 실제로 쓰는 데 필요한 대안과 문장을 준다.
- 제목과 소제목은 분명하게 쓴다.
- 불필요한 군더더기 이론 설명은 줄인다.
""".strip()


def _clean_chunks(chunks: Iterable[str]) -> str:
    labels = [
        "작품 개요",
        "캐릭터",
        "줄거리 / 트리트먼트",
        "추가 메모",
    ]
    parts = []
    for idx, text in enumerate(chunks):
        text = (text or "").strip()
        if text:
            label = labels[idx] if idx < len(labels) else f"입력 자료 {idx+1}"
            parts.append(f"[{label}]\n{text}")
    return "\n\n".join(parts) if parts else "[입력 자료 없음]"



def build_intake_merge_prompt(title: str, genre: str, style_note: str, chunks: list[str]) -> str:
    materials = _clean_chunks(chunks)
    return f"""
[TASK] 기획서 통합 분석

[작품 제목]
{title or '(제목 미입력)'}

[장르]
{genre}

[문체 지향]
{style_note}

[입력 자료]
{materials}

[해야 할 일]
1. 입력 자료를 하나의 통합 기획서로 재구성하라.
2. 작품의 핵심 콘셉트, 장르 약속, 주인공 중심 갈등을 정리하라.
3. 장편소설로 갈 때 중요한 축을 추려라.
4. 모순되거나 비어 있는 부분이 있으면 명시하라.
5. 지나치게 추상적인 표현은 걷어내고 실무형 언어로 정리하라.

[OUTPUT FORMAT]
# 작품 한 줄 정의
- 한 문장

# 통합 분석
## 1. 작품의 중심축
- 5개 내외

## 2. 주인공 / 적대자 / 핵심 관계
- 핵심만 정리

## 3. 세계와 장르의 매력
- 독자가 기대할 요소

## 4. 장편화의 강점
- 5개 내외

## 5. 현재 비어 있는 지점
- 5개 내외

## 6. 추천 소설 방향
- 시점
- 문체
- 전개 방식
- 영화서사 유지 포인트
""".strip()



def build_gap_diagnosis_prompt(title: str, genre: str, merged_summary: str) -> str:
    return f"""
[TASK] 부족한 점 진단

[작품 제목]
{title or '(제목 미입력)'}

[장르]
{genre}

[통합 분석]
{merged_summary}

[해야 할 일]
장편 상업소설 기준으로 무엇이 부족한지 정확히 진단하라.
특히 다음 항목을 보라.
- 주인공 욕망
- 주인공 결핍
- 적대 압력
- 관계 갈등
- 중반부 연료
- 정보 공개 리듬
- 엔딩 회수 가능성
- 대중소설 후킹 포인트

[OUTPUT FORMAT]
# 부족한 점 진단

## 1. 반드시 보강해야 할 점
- 우선순위 1~5

## 2. 현재 약한 이유
- 항목별로 이유 설명

## 3. 보강 방식
- 각 항목마다 구체적 대안 제시

## 4. 장편화 리스크
- 3개 내외

## 5. 바로 고치면 좋아지는 포인트
- 실제 작업용 체크리스트
""".strip()



def build_story_reinforcement_prompt(title: str, genre: str, merged_summary: str, gap_report: str) -> str:
    return f"""
[TASK] 전체 줄거리 보강

[작품 제목]
{title or '(제목 미입력)'}

[장르]
{genre}

[통합 분석]
{merged_summary}

[부족한 점 진단]
{gap_report}

[해야 할 일]
1. 현재 자료를 장편 대중소설용으로 보강하라.
2. 중반부가 약해지지 않도록 갈등 연료를 추가하라.
3. 인물의 감정선, 관계 변화, 반전, 대가를 강화하라.
4. 영상화를 염두에 둔 장면성을 유지하라.
5. 이야기를 12만자 장편소설의 뼈대로 쓸 수 있을 정도로 탄탄하게 만들어라.

[OUTPUT FORMAT]
# 보강된 전체 줄거리

## 1. 작품의 최종 방향
- 한 줄 정리

## 2. 시작 / 전개 / 중반 반전 / 위기 / 클라이맥스 / 결말
- 각 단계 1~3문단

## 3. 주인공 감정선
- 시작 → 변화 → 결말

## 4. 핵심 관계선
- 관계별 변화 정리

## 5. 대중소설 후킹 장치
- 오프닝 / 중반 / 엔딩 전후

## 6. 반드시 살아야 할 장면
- 5개 내외
""".strip()



def build_unit_plan_prompt(title: str, genre: str, reinforced_story: str) -> str:
    return f"""
[TASK] 12 Unit 설계

[작품 제목]
{title or '(제목 미입력)'}

[장르]
{genre}

[보강된 전체 줄거리]
{reinforced_story}

[해야 할 일]
이 이야기를 12 Unit 장편 구조로 설계하라.
Unit당 약 1만자 내외를 목표로 하고, 각 Unit은 명확한 기능과 엔딩 훅을 가져야 한다.

[OUTPUT FORMAT]
# 12 Unit 설계

각 Unit을 아래 형식으로 반복한다.

## Unit 01. 제목
- 기능:
- 핵심 사건:
- 감정 변화:
- 공개 정보:
- 숨길 정보:
- 다음 Unit 훅:

## Unit 02. 제목
- 기능:
- 핵심 사건:
- 감정 변화:
- 공개 정보:
- 숨길 정보:
- 다음 Unit 훅:

(이 형식으로 Unit 12까지)
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
    prev_block = f"\n[직전 Unit 요약]\n{previous_unit_summary}\n" if previous_unit_summary else ""
    return f"""
[TASK] Unit {unit_number:02d} 원고 작성

[작품 제목]
{title or '(제목 미입력)'}

[장르]
{genre}

[문체 지향]
{style_note}

[보강된 전체 줄거리]
{reinforced_story}

[12 Unit 설계]
{unit_plan}
{prev_block}
[해야 할 일]
1. Unit {unit_number:02d}에 해당하는 원고만 작성하라.
2. 대중 장편소설답게 빠르게 읽히되 얇지 않게 쓴다.
3. 영상화 가능한 장면성과 소설의 감정선을 동시에 유지하라.
4. 설명문이 길어지면 행동, 대사, 선택으로 분산하라.
5. 마지막은 다음 Unit으로 넘어가게 만드는 훅으로 끝낸다.
6. 분량은 한 번에 출력 가능한 범위 안에서 최대한 충실하게 쓴다.

[OUTPUT FORMAT]
# Unit {unit_number:02d}

## Unit 기능
- 짧게 정리

## 원고
(바로 읽을 수 있는 소설 원고. 불필요한 해설 금지)
""".strip()



def build_rewrite_prompt(mode: str, text: str) -> str:
    return f"""
[TASK] Unit 원고 다시 쓰기

[리라이트 방향]
{mode}

[기존 원고]
{text}

[해야 할 일]
1. 원고의 핵심 사건은 유지한다.
2. 리라이트 방향에 맞게 문체, 리듬, 감정 압력, 후킹을 조정한다.
3. 더 읽히게 만들되 과장된 수식은 줄인다.
4. 장면이 더 또렷하게 보이도록 다듬는다.

[OUTPUT FORMAT]
기존 구조를 살린 개선 원고만 출력한다.
""".strip()
