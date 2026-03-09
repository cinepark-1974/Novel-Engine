from __future__ import annotations

from textwrap import dedent


def clean(text: str | None) -> str:
    return (text or "").strip()


AUTHOR_STYLE_DNA = dedent(
    """
    [Mr.MOON STYLE DNA]
    - 이 작품은 영화친화적인 상업 장편소설 톤으로 쓴다.
    - 문장은 과하게 난해하지 않되, 장면이 또렷이 보이게 쓴다.
    - 각 장면은 공간, 빛, 냄새, 소리, 촉감 중 최소 1개 이상의 감각 요소로 시작한다.
    - 세계관 설명은 요약문처럼 길게 설명하지 말고 사건, 대화, 인물 반응 속에 녹여낸다.
    - 주요 인물은 첫 등장 장면에서 직업, 결핍, 비밀, 욕망 중 최소 2개가 드러나야 한다.
    - 대사는 멋을 부리기보다 갈등, 관계 변화, 정보 전진에 기여해야 한다.
    - 감정은 직접 말할 수 있으나, 중요한 장면에서는 시선, 침묵, 몸짓, 행동으로 한 번 더 보여준다.
    - 로맨스는 플롯과 분리하지 말고, 정보 교환과 위험 노출, 계급 충돌과 함께 전진시킨다.
    - 장면 말미에는 반전, 위협, 감정 흔들림, 선택 압력 중 하나를 남겨 다음 장을 열게 만든다.
    - 작품 전체에서 감각어와 물성어를 반복 모티프로 사용해 세계관과 정서를 연결한다.
    - 설명은 친절하되 평범한 해설문처럼 들리지 않게 하고, 장면화 가능한 순간으로 전환한다.
    - 문장은 중간 길이를 기본으로 하되, 전환과 충격의 순간에는 짧게 끊어 리듬을 만든다.
    - 인물의 외형은 단순 미사여구보다 상대의 반응, 행동의 변화, 장면의 공기 속에서 드러낸다.
    - 독자가 길을 잃지 않도록 구조는 명확하게 유지하되, 감정과 비밀의 압력은 점층적으로 높인다.
    """
).strip()


SYSTEM_PROMPT = dedent(
    f"""
    You are BLUE JEANS NOVEL ENGINE.

    You are a professional commercial novel development engine for long-form fiction.
    Your task is to transform planning documents into compelling Korean popular fiction with cinematic propulsion.

    Core mission:
    - Analyze planning materials clearly.
    - Diagnose what is missing for long-form fiction.
    - Reinforce the full story into a sustainable 12-unit novel structure.
    - Draft each unit as actual prose, not summary.
    - Maintain readability, suspense, visual immediacy, and emotional pull.

    Non-negotiable rules:
    - Never sound like a manual, screenplay outline, or development memo unless the user explicitly asks for one.
    - Never write generic AI-sounding prose.
    - Do not flatten scenes into summary when dramatic enactment is needed.
    - Treat each unit as real novel pages, not a synopsis.
    - Keep the writing commercial, readable, visual, and emotionally active.
    - Preserve character voice and hidden tension.
    - Information must function as conflict, risk, leverage, or revelation.
    - If exposition gets long, convert it into scene, dialogue, reaction, or action.

    Length and density policy:
    - Long-form novel scale is the goal.
    - Each generated unit should feel materially substantial, scene-based, and expandable.
    - Avoid premature closure.
    - When a passage feels compressed, expand through conflict, sensory detail, character reaction, and tactical dialogue.

    Authorial style policy:
    {AUTHOR_STYLE_DNA}

    Output language:
    - Korean by default.
    - Be clean, elegant, commercial, and vivid.
    """
).strip()


INTAKE_TEMPLATE = dedent(
    """
    [작품 기본 정보]
    제목: {title}
    장르: {genre}
    문체 지향: {style_note}

    [입력 자료]
    작품 개요:
    {overview}

    캐릭터:
    {characters}

    줄거리 / 트리트먼트:
    {synopsis}

    추가 메모:
    {extra_notes}
    """
).strip()


STYLE_APPLICATION_NOTE = dedent(
    f"""
    [문체 적용 지침]
    {AUTHOR_STYLE_DNA}

    [추가 작품별 문체 지시]
    {{style_note}}
    """
).strip()



def build_intake_merge_prompt(title: str, genre: str, style_note: str, chunks: list[str]) -> str:
    overview = clean(chunks[0] if len(chunks) > 0 else "")
    characters = clean(chunks[1] if len(chunks) > 1 else "")
    synopsis = clean(chunks[2] if len(chunks) > 2 else "")
    extra_notes = clean(chunks[3] if len(chunks) > 3 else "")

    intake = INTAKE_TEMPLATE.format(
        title=clean(title),
        genre=clean(genre),
        style_note=clean(style_note),
        overview=overview or "(없음)",
        characters=characters or "(없음)",
        synopsis=synopsis or "(없음)",
        extra_notes=extra_notes or "(없음)",
    )

    return dedent(
        f"""
        다음 자료를 하나의 장편소설 기획으로 통합 분석하라.

        {intake}

        목표:
        - 흩어진 입력 자료를 하나의 일관된 소설 기획으로 정리한다.
        - 작품의 중심축을 선명하게 드러낸다.
        - 아이디어 메모가 아니라 실제 장편소설 개발용 통합 문서처럼 정리한다.

        반드시 포함할 항목:
        1. 작품 한 줄 정의
        2. 작품의 핵심 매력 5가지
        3. 주인공 / 적대자 / 관계 구조 분석
        4. 세계관과 장르의 매력
        5. 장편화의 강점
        6. 현재 이미 있는 재료
        7. 우선순위 높은 보강 포인트
        8. 영상화 시 유리한 포인트

        작성 규칙:
        - 명확하고 실전적인 한국어로 쓴다.
        - 추상어보다 구체어를 쓴다.
        - 이미 있는 장점을 잃지 않도록 보호하는 방향으로 쓴다.
        - 문장 내내 {clean(style_note) or '상업 장편소설'} 지향을 유지한다.
        """
    ).strip()



def build_gap_diagnosis_prompt(title: str, genre: str, merged_summary: str) -> str:
    return dedent(
        f"""
        아래의 통합 분석을 바탕으로, 이 작품이 12만 자 내외 장편소설이 되기 위해 무엇이 부족한지 진단하라.

        [작품명] {clean(title)}
        [장르] {clean(genre)}

        [통합 분석]
        {clean(merged_summary)}

        출력 목표:
        - 문제를 모호하게 말하지 말고, 실제 집필 전에 보강해야 할 항목을 정확히 짚는다.

        반드시 아래 구조를 따른다.
        1. 현재 장편화에 가장 유리한 요소
        2. 부족한 점 진단
           - 주인공 욕망/결핍
           - 적대 구조
           - 관계 갈등
           - 중반부 연료
           - 장르 정보 활용
           - 엔딩 회수 가능성
        3. 왜 이 문제가 장편 분량에서 치명적인지
        4. 반드시 보강해야 할 우선순위 TOP 5
        5. 각 항목별 보강 제안

        작성 규칙:
        - 막연한 조언 금지.
        - 실제로 플롯, 감정선, 정보선, 인물선이 어떻게 보강되어야 하는지 써라.
        - Mr.MOON 스타일의 장점(장면성, 감각어, 상업성, 플롯-로맨스 결합)을 약화시키지 않는 방향으로 제안하라.
        """
    ).strip()



def build_story_reinforcement_prompt(title: str, genre: str, merged_summary: str, gap_report: str) -> str:
    return dedent(
        f"""
        아래 자료를 바탕으로 장편소설용 전체 줄거리를 보강하라.

        [작품명] {clean(title)}
        [장르] {clean(genre)}

        [통합 분석]
        {clean(merged_summary)}

        [부족한 점 진단]
        {clean(gap_report)}

        목표:
        - 이 작품이 12개 Unit로 확장 가능한 장편소설이 되도록 전체 줄거리를 보강한다.
        - 단순 시놉시스가 아니라, 장편 전체를 끌고 갈 수 있는 압력과 관계 변화를 설계한다.

        반드시 포함할 항목:
        1. 장편소설용 강화 로그라인
        2. 시작 / 중반 / 위기 / 결전 / 결말의 흐름
        3. 주인공 아크
        4. 적대자 아크
        5. 관계 아크
        6. 중반 이후 확장되는 갈등 연료
        7. 장르 정보가 사건으로 작동하는 방식
        8. 결말의 정서적 회수

        작성 규칙:
        - 요약문처럼 말고, 실제 소설화가 가능한 형태로 쓴다.
        - 사건만 나열하지 말고 감정 변화와 선택의 대가를 함께 넣는다.
        - 설명 과다 구간은 장면으로 환산 가능한 방식으로 설계한다.
        - 정보, 시대, 세계관 요소가 감정과 분리되지 않게 한다.
        - 상업 장편소설의 흡입력을 유지한다.
        """
    ).strip()



def build_unit_plan_prompt(title: str, genre: str, reinforced_story: str) -> str:
    return dedent(
        f"""
        아래 전체 줄거리 보강안을 바탕으로 12 Unit 장편소설 구조를 설계하라.

        [작품명] {clean(title)}
        [장르] {clean(genre)}

        [전체 줄거리 보강]
        {clean(reinforced_story)}

        목표:
        - 총 12개 Unit으로 구성된 장편소설 구조를 만든다.
        - 각 Unit은 약 1만 자 안팎으로 확장 가능한 밀도를 가져야 한다.
        - 각 Unit이 독립적인 사건 기능과 감정 전환을 가지게 한다.

        출력 형식:
        Unit 01 ~ Unit 12까지 각각 아래 항목을 반드시 포함한다.
        - Unit 제목
        - 서사 기능
        - 핵심 사건
        - 감정 변화
        - 공개 정보
        - 숨길 정보
        - 주요 관계 변화
        - 감각/정보 포인트
        - 엔딩 훅

        추가 규칙:
        - Unit 01은 강한 오프닝이어야 한다.
        - Unit 06 전후에는 판을 흔드는 변화가 있어야 한다.
        - Unit 08~10 구간에는 추락, 재정렬, 결전 준비가 살아 있어야 한다.
        - Unit 12는 플롯 정리뿐 아니라 정서 회수까지 포함한다.
        - 각 Unit은 다음 Unit을 읽게 만드는 상업적 압력을 남겨야 한다.
        """
    ).strip()



def build_unit_draft_prompt(
    title: str,
    genre: str,
    style_note: str,
    reinforced_story: str,
    unit_plan: str,
    unit_number: int,
    previous_unit_summary: str,
) -> str:
    prev_block = clean(previous_unit_summary) or "(직전 Unit 없음)"
    style_block = STYLE_APPLICATION_NOTE.format(style_note=clean(style_note) or "(없음)")

    return dedent(
        f"""
        아래 자료를 바탕으로 Unit {unit_number:02d}의 실제 소설 원고를 작성하라.

        [작품명] {clean(title)}
        [장르] {clean(genre)}

        {style_block}

        [전체 줄거리 보강]
        {clean(reinforced_story)}

        [12 Unit 설계]
        {clean(unit_plan)}

        [직전 Unit 요약]
        {prev_block}

        [현재 작업]
        Unit {unit_number:02d}

        집필 목표:
        - 이 출력은 시놉시스가 아니라 실제 소설 원고여야 한다.
        - 장면이 보이고, 인물이 움직이고, 감정이 흔들려야 한다.
        - 상업 장편소설답게 빠르게 읽히되, 평평한 설명문으로 흘러가지 말아야 한다.
        - 필요하면 2~4개의 소챕터 흐름을 자연스럽게 포함해도 좋다.

        반드시 지킬 규칙:
        1. 첫 문단부터 공간, 행동, 감각으로 시작한다.
        2. 정보를 길게 설명하지 말고 갈등과 반응 속에 녹인다.
        3. 인물은 기능적 도구가 아니라 모순과 욕망을 지닌 사람처럼 보이게 쓴다.
        4. 대사는 갈등, 유혹, 위협, 정보 전진 중 하나를 수행해야 한다.
        5. 중요한 감정 장면은 한 번 더 행동과 침묵으로 보여준다.
        6. 로맨스가 있다면 플롯과 함께 전진시킨다.
        7. 장면 끝에는 다음 장을 열게 하는 압력을 남긴다.
        8. 결론을 서둘러 닫지 않는다.

        분량 규칙:
        - 충분히 실질적인 Unit 초안이 되도록 풍부하게 쓴다.
        - 장면을 요약하지 말고 전개하라.
        - 압축이 심해지면 감각, 반응, 대화, 갈등, 선택을 통해 확장하라.

        출력 형식:
        - 바로 소설 본문으로 시작한다.
        - 불필요한 머리말, 해설, 분석, 번호 목록 금지.
        """
    ).strip()



def build_rewrite_prompt(mode: str, text: str) -> str:
    mode_map = {
        "더 상업적으로": "흡입력, 가독성, 장면 추진력을 강화하라.",
        "더 빠르게": "문장과 장면 전환 속도를 높이고 군더더기를 줄여라.",
        "더 감정적으로": "감정의 여운과 관계의 떨림을 강화하라.",
        "더 차갑게": "문장을 절제하고 긴장과 냉기를 강화하라.",
        "더 스릴러답게": "위험, 추적, 의심, 반전의 압력을 높여라.",
        "더 여성서사 중심으로": "주체성, 선택, 시선의 중심을 여성 인물에게 더 강하게 실어라.",
        "더 영상적으로": "장면의 시각성, 동선, 현장감, 컷감 같은 리듬을 강화하라.",
    }
    mode_instruction = mode_map.get(clean(mode), "문체와 장면 밀도를 개선하라.")

    return dedent(
        f"""
        아래 소설 원고를 다시 써라.

        [리라이트 방향]
        {clean(mode)}
        {mode_instruction}

        [유지해야 할 기본 작가 스타일]
        {AUTHOR_STYLE_DNA}

        [원고]
        {clean(text)}

        규칙:
        - 줄거리의 핵심 사건은 유지한다.
        - 원문의 장면성과 감각 모티프를 잃지 않는다.
        - 더 강한 상업 장편소설 초안처럼 읽히게 만든다.
        - 기계적으로 꾸미지 말고 자연스럽게 개선한다.
        - 해설 없이 바로 수정된 소설 본문만 출력한다.
        """
    ).strip()
