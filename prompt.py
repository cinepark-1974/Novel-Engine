# ─────────────────────────────────────────────────────────────
# BLUE JEANS NOVEL ENGINE
# prompt.py
# ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
당신은 BLUE JEANS NOVEL ENGINE이다.

역할:
사용자가 입력한 기획 자료를 바탕으로 장편 대중소설을 위한
분석, 보강, Unit 설계, 실제 원고 생성, 리라이트, 제목 검토를 수행한다.

핵심 원칙:
1. 설명보다 체험을 우선한다.
2. 줄거리 요약처럼 쓰지 말고 실제 장면으로 전개한다.
3. 설정 설명은 백과사전처럼 길게 풀지 말고 사건, 행동, 대사, 반응 속에 녹인다.
4. 장면은 갈등, 감정 변화, 정보 공개/은폐, 선택 압력 중 하나 이상을 가진다.
5. 대사는 기능적이어야 하며 갈등, 관계 변화, 정보 전진에 기여해야 한다.
6. 문장은 난해하지 않되 화면이 보이게 쓴다.
7. 중요한 감정은 직접 진술만 하지 말고 시선, 침묵, 몸짓, 행동으로도 드러낸다.
8. 장르적 정보는 설명이 아니라 위기, 반전, 선택의 장치로 쓴다.
9. Unit 12는 반드시 본편을 마무리해야 한다.
10. Unit 13은 선택형 에필로그이며 후일담과 여운 중심으로 쓴다.
11. Unit 12 또는 Unit 13의 마지막 결과는 마지막 줄에 정확히 `끝.` 을 단독으로 둔다.
12. 사용자의 문체 샘플이 있으면 이를 복제하려 하지 말고 구조적 특징을 추출해 반영한다.
13. 불필요한 사족, 메타 설명, 자기 변명, 장황한 서문은 쓰지 않는다.
14. 결과는 실무적으로 바로 사용 가능한 형태로 명확하게 출력한다.
15. 원고 생성 시 반드시 목표 분량을 충족하도록 장면, 대사, 행동 묘사를 충분히 전개한다.
16. 토큰이 부족해 중간에 끊길 위험이 있으면, 마지막 장면을 서둘러 마감하더라도 완결된 문장으로 끝낸다.
""".strip()

AUTHOR_STYLE_DNA_BASE = """
Mr.MOON 스타일 기본 규칙:
- 영화친화적인 상업 장편소설 톤으로 쓴다.
- 장면은 공간, 빛, 냄새, 소리, 촉감 중 최소 1개 이상의 감각 요소로 진입할 수 있다.
- 세계관 설명은 사건, 행동, 인물 반응, 대사 속에 배치한다.
- 주요 인물은 첫 등장 장면에서 직업, 결핍, 비밀, 욕망 중 최소 2개가 드러나야 한다.
- 대사는 멋을 부리기보다 갈등, 관계 변화, 정보 전진에 기여해야 한다.
- 감정은 직접 말할 수 있으나 결정적 장면에서는 시선, 침묵, 몸짓, 행동으로 한 번 더 보여준다.
- 로맨스는 플롯과 분리하지 말고 정보 교환, 위험 노출, 계급/권력 충돌과 함께 전진시킨다.
- 장면 말미에는 반전, 위협, 감정 흔들림, 선택 압력 중 하나를 남겨 다음 장으로 이어지게 한다.
- 작품 전체에서 감각어와 물성어를 반복 모티프로 사용할 수 있다.
- 문장은 중간 길이 문장을 기본으로 하되 전환과 충격 지점에서는 짧게 끊는다.
- 설명문이 길어질 조짐이 보이면 장면과 대사로 환원한다.
""".strip()

STYLE_DNA_ANALYSIS_PROMPT = """
다음 문체 샘플을 분석해 `Style DNA`를 작성하라.

요구사항:
- 샘플 줄거리를 요약하지 말고 문체의 구조적 특징을 추출할 것
- 칭찬 위주가 아니라 제어 가능한 규칙으로 정리할 것
- 출력은 아래 형식을 유지할 것

출력 형식:
1. 한 줄 정의
2. 문장 리듬
3. 감정 처리 방식
4. 장면 진입 방식
5. 정보 삽입 방식
6. 대사 성향
7. 자주 강해지는 장면 유형
8. 약해질 수 있는 지점
9. 엔진 반영 규칙 8~10개

[문체 샘플]
{style_sample}
""".strip()


def _style_block(style_dna: str, style_strength: str = "중") -> str:
    strength_map = {
        "약": "문체 특징을 은은하게 반영하되 장르 요구와 가독성을 우선한다.",
        "중": "문체 특징을 분명히 반영하되 반복감이나 자기복제는 피한다.",
        "강": "문체 특징을 강하게 반영하되 작품 전체의 추진력과 가독성은 무너뜨리지 않는다.",
    }
    strength_text = strength_map.get(style_strength, strength_map["중"])
    return f"""
[기본 STYLE DNA]
{AUTHOR_STYLE_DNA_BASE}

[사용자 STYLE DNA]
{style_dna or "사용자 문체 샘플 분석 결과 없음. 기본 STYLE DNA만 사용한다."}

[문체 반영 강도]
{strength_text}
""".strip()


def build_merge_analysis_prompt(
    working_title: str,
    genre: str,
    format_mode: str,
    pov: str,
    target_length: str,
    overview: str,
    characters: str,
    synopsis: str,
    notes: str,
    style_dna: str,
    style_strength: str,
) -> str:
    return f"""
다음 자료를 통합 분석하여 장편소설 개발용 진단 리포트를 작성하라.

요구사항:
- 장황한 미사여구 금지
- 평가와 진단을 분리해서 쓸 것
- 실무 문서처럼 명확하게 쓸 것
- 결과는 아래 형식을 반드시 유지할 것

출력 형식:
1. 한 줄 콘셉트
2. 작품의 강점 5개
3. 장편화 위험요소 5개
4. 장르 톤 정의
5. 주인공 아크 요약
6. 적대 구조 요약
7. 관계 축 요약
8. 정보/시대/세계관 처리 포인트
9. 이 작품이 장편소설로 강해질 수 있는 이유
10. 즉시 보강이 필요한 핵심 3개

[가제]
{working_title}

[장르]
{genre}

[형식]
{format_mode}

[시점]
{pov}

[목표 분량]
{target_length}

[작품 개요]
{overview}

[캐릭터]
{characters}

[줄거리 / 트리트먼트]
{synopsis}

[추가 메모]
{notes}

{_style_block(style_dna, style_strength)}
""".strip()


def build_gap_diagnosis_prompt(
    working_title: str,
    merged_analysis: str,
    overview: str,
    characters: str,
    synopsis: str,
    notes: str,
    style_dna: str,
) -> str:
    return f"""
다음 작품의 부족한 점을 장편소설 기준으로 진단하라.

요구사항:
- 단순 비판이 아니라 보강 가능 포인트로 쓸 것
- 구조, 인물, 감정, 장르, 정보 레이어를 나눠서 볼 것
- 결과는 아래 형식을 유지할 것

출력 형식:
1. 구조적 부족점
2. 인물의 부족점
3. 감정선의 부족점
4. 장르적 부족점
5. 정보/시대/세계관의 과다 또는 부족
6. 중반부 붕괴 위험
7. 엔딩 약화 위험
8. 가장 먼저 보강해야 할 5개 항목
9. 각 항목별 구체적 대안

[가제]
{working_title}

[통합 분석]
{merged_analysis}

[작품 개요]
{overview}

[캐릭터]
{characters}

[줄거리 / 트리트먼트]
{synopsis}

[추가 메모]
{notes}

[STYLE DNA]
{style_dna}
""".strip()


def build_story_reinforcement_prompt(
    segment_name: str,
    working_title: str,
    genre: str,
    overview: str,
    characters: str,
    synopsis: str,
    notes: str,
    merged_analysis: str,
    gap_diagnosis: str,
    style_dna: str,
) -> str:
    segment_roles = {
        "기": "세계 진입, 주인공 소개, 결핍/욕망 제시, 발화 사건, 되돌릴 수 없는 선택",
        "승": "상황 확장, 관계 심화, 첫 성공과 첫 대가, 판 확대, 적대 구조 선명화",
        "전": "중반 반전, 배신/상실/균열, 추락과 재정렬, 진실 접근, 결전 압축",
        "결": "결전 준비, 클라이맥스, 감정 회수, 본편 마무리",
    }

    return f"""
다음 작품의 `{segment_name}` 구간만 보강하라.

구간 기능:
{segment_roles.get(segment_name, "")}

요구사항:
- 전체 줄거리 요약이 아니라 이 구간이 실제로 더 강해지도록 보강할 것
- 설명보다 사건 흐름과 감정 전환이 보이게 쓸 것
- 장편소설 분량을 버틸 수 있는 갈등과 장면을 제안할 것
- 결과는 아래 형식으로 작성할 것

출력 형식:
1. 구간 역할
2. 핵심 사건 흐름
3. 인물/관계 변화
4. 감정 흐름
5. 반드시 살아야 할 장면 3~5개
6. 약한 부분 보강 포인트
7. 다음 구간으로 넘기는 연결점

[가제]
{working_title}

[장르]
{genre}

[작품 개요]
{overview}

[캐릭터]
{characters}

[줄거리 / 트리트먼트]
{synopsis}

[추가 메모]
{notes}

[통합 분석]
{merged_analysis}

[부족한 점 진단]
{gap_diagnosis}

[STYLE DNA]
{style_dna}
""".strip()


def build_unit_blueprint_prompt(
    group_key: str,
    working_title: str,
    genre: str,
    format_mode: str,
    pov: str,
    overview: str,
    characters: str,
    story_reinforcement_merged: str,
    synopsis: str,
    notes: str,
    style_dna: str,
) -> str:
    group_meaning = {
        "01-02": "기 구간 초반. 오프닝, 세계 진입, 발화 사건",
        "03-04": "기에서 승으로 넘어가는 구간. 되돌릴 수 없는 선택, 상황 확장",
        "05-06": "승 구간 심화. 관계 확장, 첫 대가, 판 확대",
        "07-08": "전 구간 진입. 중반 반전, 균열, 배신, 상실",
        "09-10": "전에서 결로 넘어가는 구간. 추락, 재정렬, 결전 준비",
        "11-12": "결 구간. 클라이맥스, 정서 회수, 본편 마무리",
    }

    return f"""
다음 작품의 UNIT {group_key} 설계를 작성하라.

현재 설계 대상 구간 의미:
{group_meaning.get(group_key, "")}

요구사항:
- 반드시 UNIT {group_key}만 작성할 것
- 각 Unit당 아래 5개 항목만 작성할 것
- 군더더기 설명 없이 핵심 기능과 후킹을 분명하게 제시할 것
- Unit 12가 포함된 경우, Unit 12는 반드시 본편을 마무리하도록 설계할 것

출력 형식:
[UNIT XX]
- 제목:
- 서사 기능:
- 핵심 사건:
- 감정 변화:
- 엔딩 훅:

[가제]
{working_title}

[장르]
{genre}

[형식]
{format_mode}

[시점]
{pov}

[작품 개요]
{overview}

[캐릭터]
{characters}

[줄거리 / 트리트먼트]
{synopsis}

[기승전결 보강본]
{story_reinforcement_merged}

[추가 메모]
{notes}

[STYLE DNA]
{style_dna}
""".strip()


def build_unit_draft_prompt(
    unit_no: int,
    working_title: str,
    genre: str,
    format_mode: str,
    pov: str,
    overview: str,
    characters: str,
    synopsis: str,
    notes: str,
    story_reinforcement_merged: str,
    all_blueprints_text: str,
    previous_drafts: str,
    style_dna: str,
    style_strength: str,
    target_length: int,
    min_length: int,
) -> str:
    if unit_no == 12:
        final_rule = """
추가 규칙:
- 이 Unit은 본편의 마지막 Unit이다.
- 반드시 중심 갈등을 종결하고, 감정적/플롯적 회수를 수행하라.
- 열린 질문이 있더라도 본편은 완결된 상태여야 한다.
- 마지막 줄에는 정확히 `끝.` 을 단독으로 출력하라.
"""
    else:
        final_rule = """
추가 규칙:
- 아직 본편의 마지막이 아니므로 `끝.` 을 출력하지 않는다.
- 다음 Unit으로 넘어가게 하는 압력을 남긴다.
"""

    return f"""
다음 작품의 UNIT {unit_no:02d} 실제 원고를 작성하라.

중요 원칙:
- 줄거리 요약처럼 쓰지 말고 실제 소설 원고로 쓸 것
- 장면으로 전개할 것
- 최소 4개의 장면 블록을 포함할 것
  1) 도입 장면
  2) 전개 장면
  3) 전환 장면
  4) 마감 장면
- 감각적 진입, 행동, 대사, 갈등, 감정 변화가 살아 있어야 한다
- 설명이 길어지면 장면과 대사로 전환할 것
- 장르 정보, 시대 정보, 전문 정보는 플롯 장치처럼 쓸 것
- 중요한 대면 장면은 축약하지 말 것
- 이 Unit의 목표 분량은 약 {target_length}자이며 최소 {min_length}자 이상을 확보할 것
- 분량이 부족하면 요약하지 말고 장면, 대화, 감정 반응, 행동 묘사를 확장해 채울 것
- 문장이 미완성인 상태로 끝나면 안 된다
- 마지막 문단은 반드시 장면적으로 닫히거나 다음 Unit로 이어지는 압력을 남겨야 한다
- 출력 시작 시 불필요한 서문이나 메타 설명 없이 바로 원고 본문부터 시작할 것

{final_rule}

[가제]
{working_title}

[장르]
{genre}

[형식]
{format_mode}

[시점]
{pov}

[작품 개요]
{overview}

[캐릭터]
{characters}

[줄거리 / 트리트먼트]
{synopsis}

[추가 메모]
{notes}

[기승전결 보강본]
{story_reinforcement_merged}

[전체 Unit 설계]
{all_blueprints_text}

[이전까지 작성된 Unit 원고]
{previous_drafts or "이전 원고 없음"}

{_style_block(style_dna, style_strength)}
""".strip()


def build_expand_incomplete_unit_prompt(
    unit_no: int,
    current_text: str,
    target_length: int,
    min_length: int,
) -> str:
    final_rule = "마지막 줄에는 정확히 `끝.` 을 단독으로 출력하라." if unit_no in (12, 13) else "`끝.` 을 붙이지 않는다."
    return f"""
다음 UNIT 원고는 분량이 부족하거나 끝맺음이 미완성이다.
기존 텍스트를 반복하지 말고, 바로 이어서 장면을 확장하고 마무리를 완성하라.

요구사항:
- 현재 원고의 톤, 시점, 흐름을 유지할 것
- 최소 2개의 추가 장면 또는 장면 블록을 더해도 좋다
- 요약문으로 건너뛰지 말 것
- 대사, 행동, 감정 반응, 공간 디테일을 사용해 자연스럽게 확장할 것
- 전체 결과가 최소 {min_length}자 이상, 가능하면 {target_length}자 내외가 되도록 보강할 것
- 문장이 중간에 끊기지 않게 완결된 문장으로 마무리할 것
- 서문이나 메타 설명 없이 바로 이어서 쓸 것
- {final_rule}

[현재 원고]
{current_text}
""".strip()


def build_unit_rewrite_prompt(
    unit_no: int,
    rewrite_mode: str,
    source_text: str,
    style_dna: str,
    target_length: int,
    min_length: int,
) -> str:
    ending_rule = "마지막 줄에 `끝.` 을 유지한다." if unit_no in (12, 13) else "`끝.` 을 붙이지 않는다."
    return f"""
다음 UNIT 원고를 `{rewrite_mode}` 방향으로 다시 써라.

요구사항:
- 플롯을 함부로 바꾸지 말고 문장, 장면 밀도, 감정 전달, 후킹, 가독성을 개선할 것
- 요약문처럼 압축하지 말고 소설 문장으로 유지할 것
- 최소 {min_length}자 이상, 가능하면 {target_length}자 내외의 밀도를 확보할 것
- 장면 블록이 지나치게 줄어들지 않게 할 것
- Style DNA를 유지할 것
- 서문이나 메타 설명 없이 바로 원고 본문부터 출력할 것
- {ending_rule}

[STYLE DNA]
{style_dna}

[원고]
{source_text}
""".strip()


def build_epilogue_prompt(
    working_title: str,
    genre: str,
    overview: str,
    characters: str,
    synopsis: str,
    story_reinforcement_merged: str,
    all_blueprints_text: str,
    all_drafts_text: str,
    style_dna: str,
) -> str:
    return f"""
다음 작품의 UNIT 13 · 에필로그를 작성하라.

요구사항:
- 약 2000~3000자 내외의 정서적 마무리
- 본편을 다시 뒤집지 말 것
- 후일담, 여운, 상징 회수, 관계의 잔향을 중심으로 쓸 것
- 군더더기 설명을 피하고 마지막 정서가 또렷하게 남게 할 것
- 서문이나 메타 설명 없이 바로 에필로그 본문부터 시작할 것
- 마지막 줄에는 정확히 `끝.` 을 단독으로 출력할 것

[가제]
{working_title}

[장르]
{genre}

[작품 개요]
{overview}

[캐릭터]
{characters}

[줄거리 / 트리트먼트]
{synopsis}

[기승전결 보강본]
{story_reinforcement_merged}

[전체 Unit 설계]
{all_blueprints_text}

[본편 원고]
{all_drafts_text}

[STYLE DNA]
{style_dna}
""".strip()


def build_title_review_prompt(
    current_title: str,
    overview: str,
    synopsis: str,
    story_reinforcement_merged: str,
    all_blueprints_text: str,
    all_drafts_text: str,
    style_dna: str,
) -> str:
    return f"""
현재 가제를 검토하고 원고 기반 제목 대안을 제안하라.

요구사항:
- 현재 가제를 먼저 유지/비추천 여부로 판단할 것
- 원고 안의 반복 대사, 상징어, 감정 핵심, 마지막 장면 정서를 읽고 제목감을 찾을 것
- 흔한 제목, 지나치게 설명적인 제목은 피할 것
- 결과는 아래 형식을 지킬 것

출력 형식:
1. 현재 가제 유지 여부
2. 유지 또는 비추천 이유
3. 현재 가제를 살린 보강안 5개
4. 새 대안 제목 10개
5. 영상화형 제목 5개
6. 문학/정서형 제목 5개
7. 가장 추천하는 최종 후보 3개와 이유

[현재 가제]
{current_title}

[작품 개요]
{overview}

[줄거리 / 트리트먼트]
{synopsis}

[기승전결 보강본]
{story_reinforcement_merged}

[전체 Unit 설계]
{all_blueprints_text}

[생성 원고]
{all_drafts_text}

[STYLE DNA]
{style_dna}
""".strip()
