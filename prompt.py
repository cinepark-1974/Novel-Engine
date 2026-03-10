from __future__ import annotations

from textwrap import dedent


def clean(text: str | None) -> str:
    return (text or "").strip()


AUTHOR_STYLE_DNA = dedent(
    """
    [Mr.MOON STYLE DNA]
    - 영화친화적인 상업 장편소설 톤으로 쓴다.
    - 문장은 과하게 난해하지 않되 장면이 또렷이 보이게 쓴다.
    - 각 장면은 공간, 빛, 냄새, 소리, 촉감 중 최소 1개 이상의 감각 요소로 시작한다.
    - 세계관 설명은 요약문처럼 길게 설명하지 말고 사건, 대화, 인물 반응 속에 녹여낸다.
    - 주요 인물은 첫 등장 장면에서 직업, 결핍, 비밀, 욕망 중 최소 2개가 드러나야 한다.
    - 대사는 멋을 부리기보다 갈등, 관계 변화, 정보 전진에 기여해야 한다.
    - 감정은 직접 말할 수 있으나 중요한 장면에서는 시선, 침묵, 몸짓, 행동으로 한 번 더 보여준다.
    - 로맨스는 플롯과 분리하지 말고 정보 교환, 위험 노출, 계급 충돌과 함께 전진시킨다.
    - 장면 말미에는 반전, 위협, 감정 흔들림, 선택 압력 중 하나를 남겨 다음 장을 열게 만든다.
    - 작품 전체에서 감각어와 물성어를 반복 모티프로 사용해 세계관과 정서를 연결한다.
    - 문장은 중간 길이를 기본으로 하되 전환과 충격의 순간에는 짧게 끊어 리듬을 만든다.
    - 인물의 외형은 단순 미사여구보다 상대의 반응, 행동의 변화, 장면의 공기 속에서 드러낸다.
    """
).strip()


SYSTEM_PROMPT = dedent(
    f"""
    You are BLUE JEANS NOVEL ENGINE.

    You are a professional long-form fiction development engine for Korean commercial novels.
    Your role is to transform planning materials into compelling, cinematic, emotionally active prose.

    Core rules:
    - Never sound generic.
    - Never write like a manual unless explicitly asked.
    - Convert exposition into scene, conflict, reaction, leverage, danger, or revelation whenever possible.
    - Keep the prose readable, visual, and commercially strong.
    - Preserve hidden tension and character contradiction.
    - Avoid premature closure except in the final unit or epilogue.

    Finale rules:
    - Unit 12 must close the main story arc decisively.
    - If Unit 13 (Epilogue) is requested, Unit 12 should still finish the core conflict, and Unit 13 should provide emotional afterglow and final image.
    - The final generated output of the novel must end with a standalone final line exactly: 끝.

    Authorial style policy:
    {AUTHOR_STYLE_DNA}

    Output language:
    - Korean by default.
    """
).strip()


STYLE_NOTE_BLOCK = dedent(
    """
    [문체 적용 지침]
    {style_note}

    [고정 작가 문체 기준]
    {author_style}
    """
).strip()


INTAKE_BLOCK = dedent(
    """
    [작품 정보]
    제목: {title}
    장르: {genre}
    가제: {working_title}

    [작품 개요]
    {overview}

    [캐릭터]
    {characters}

    [줄거리 / 트리트먼트]
    {synopsis}

    [추가 메모]
    {extra_notes}
    """
).strip()


def _base_intake(title: str, genre: str, working_title: str, overview: str, characters: str, synopsis: str, extra_notes: str) -> str:
    return INTAKE_BLOCK.format(
        title=clean(title) or "(미입력)",
        genre=clean(genre) or "(미입력)",
        working_title=clean(working_title) or "(미입력)",
        overview=clean(overview) or "(없음)",
        characters=clean(characters) or "(없음)",
        synopsis=clean(synopsis) or "(없음)",
        extra_notes=clean(extra_notes) or "(없음)",
    )


def build_intake_merge_prompt(title: str, genre: str, working_title: str, style_note: str, overview: str, characters: str, synopsis: str, extra_notes: str) -> str:
    intake = _base_intake(title, genre, working_title, overview, characters, synopsis, extra_notes)
    style = STYLE_NOTE_BLOCK.format(style_note=clean(style_note) or "(없음)", author_style=AUTHOR_STYLE_DNA)
    return dedent(
        f"""
        다음 자료를 바탕으로 장편소설 개발용 통합 분석문을 작성하라.

        {intake}

        {style}

        출력 항목:
        1. 작품 한 줄 정의
        2. 작품의 핵심 매력 5가지
        3. 주인공 / 적대자 / 관계 구조 분석
        4. 세계관과 장르의 매력
        5. 장편화의 강점
        6. 현재 이미 있는 재료
        7. 우선순위 높은 보강 포인트
        8. 영상화 시 유리한 포인트

        작성 규칙:
        - 추상어보다 구체어.
        - 실제 집필과 개발에 바로 쓸 수 있는 언어로 쓸 것.
        - Mr.MOON 스타일의 장점(장면성, 감각어, 상업성, 플롯-로맨스 결합)을 보호할 것.
        """
    ).strip()


def build_gap_diagnosis_prompt(title: str, genre: str, merged_summary: str) -> str:
    return dedent(
        f"""
        아래 통합 분석을 바탕으로 이 작품이 장편소설이 되기 위해 부족한 점을 진단하라.

        [작품명] {clean(title)}
        [장르] {clean(genre)}

        [통합 분석]
        {clean(merged_summary)}

        반드시 포함할 것:
        1. 현재 장편화에 유리한 요소
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
        - 실제 플롯, 감정선, 정보선, 인물선이 어떻게 보강되어야 하는지 쓸 것.
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

        반드시 포함할 것:
        1. 강화 로그라인
        2. 시작 / 중반 / 위기 / 결전 / 결말
        3. 주인공 아크
        4. 적대자 아크
        5. 관계 아크
        6. 중반 이후 갈등 연료
        7. 정보가 사건으로 작동하는 방식
        8. 결말의 정서적 회수

        작성 규칙:
        - 장편소설의 뼈대가 되도록 설계할 것.
        - 사건 나열이 아니라 선택의 대가와 감정 변화를 함께 쓸 것.
        - 설명 과다 구간은 장면으로 환산 가능한 방식으로 바꿀 것.
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

        출력 형식:
        Unit 01 ~ Unit 12까지 각각 아래 항목을 포함한다.
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
        - Unit 01은 강한 오프닝.
        - Unit 06 전후에는 판을 흔드는 변화.
        - Unit 08~10은 추락, 재정렬, 결전 준비.
        - Unit 12는 본편의 메인 갈등을 완결하고 정서 회수까지 끝낼 것.
        - 별도의 Unit 13 에필로그를 붙일 수 있으므로, Unit 12는 본편 완결 중심으로 설계할 것.
        """
    ).strip()


def build_unit_draft_prompt(
    title: str,
    genre: str,
    working_title: str,
    style_note: str,
    reinforced_story: str,
    unit_plan: str,
    unit_number: int,
    previous_unit_summary: str,
) -> str:
    is_final = unit_number == 12
    style = STYLE_NOTE_BLOCK.format(style_note=clean(style_note) or "(없음)", author_style=AUTHOR_STYLE_DNA)
    unit_specific = dedent(
        """
        [최종 Unit 규칙]
        - 이번 Unit은 Unit 12다.
        - 메인 갈등, 핵심 비밀, 감정의 결산을 반드시 마무리한다.
        - 끝을 흐리지 말고 서사를 명확히 닫는다.
        - 별도 에필로그가 없더라도 독자가 완결을 느껴야 한다.
        - 마지막 줄은 아직 `끝.` 을 쓰지 않는다. 그것은 최종 후처리 또는 에필로그에서 붙는다.
        """
    ).strip() if is_final else "[중간 Unit 규칙]\n- 이번 Unit은 다음 Unit으로 이어지는 압력을 남겨야 한다."

    return dedent(
        f"""
        아래 자료를 바탕으로 Unit {unit_number:02d}의 실제 소설 원고를 작성하라.

        [작품명] {clean(title)}
        [가제] {clean(working_title)}
        [장르] {clean(genre)}

        {style}

        [전체 줄거리 보강]
        {clean(reinforced_story)}

        [12 Unit 설계]
        {clean(unit_plan)}

        [직전 Unit 요약]
        {clean(previous_unit_summary) or '(없음)'}

        {unit_specific}

        집필 목표:
        - 시놉시스가 아니라 실제 소설 원고여야 한다.
        - 장면이 보이고, 인물이 움직이고, 감정이 흔들려야 한다.
        - 상업 장편소설답게 빠르게 읽히되 평평한 설명문으로 흐르지 말아야 한다.

        반드시 지킬 규칙:
        1. 첫 문단부터 공간, 행동, 감각으로 시작한다.
        2. 정보를 길게 설명하지 말고 갈등과 반응 속에 녹인다.
        3. 인물은 모순과 욕망을 가진 사람처럼 보이게 쓴다.
        4. 대사는 갈등, 유혹, 위협, 정보 전진 중 하나를 수행해야 한다.
        5. 중요한 감정 장면은 한 번 더 행동과 침묵으로 보여준다.
        6. 로맨스가 있다면 플롯과 함께 전진시킨다.
        7. 장면 끝에는 다음 장 또는 결말의 압력을 남긴다.
        8. 요약보다 장면을 우선한다.
        """
    ).strip()


def build_epilogue_prompt(
    title: str,
    genre: str,
    working_title: str,
    style_note: str,
    reinforced_story: str,
    unit_plan: str,
    final_unit_text: str,
) -> str:
    style = STYLE_NOTE_BLOCK.format(style_note=clean(style_note) or "(없음)", author_style=AUTHOR_STYLE_DNA)
    return dedent(
        f"""
        아래 자료를 바탕으로 Unit 13 에필로그를 작성하라.

        [작품명] {clean(title)}
        [가제] {clean(working_title)}
        [장르] {clean(genre)}

        {style}

        [전체 줄거리 보강]
        {clean(reinforced_story)}

        [12 Unit 설계]
        {clean(unit_plan)}

        [Unit 12 원고]
        {clean(final_unit_text)}

        에필로그 규칙:
        - 분량은 약 2페이지 분량의 짧고 밀도 있는 에필로그로 쓴다.
        - 메인 갈등은 이미 끝났다고 전제하고, 정서적 여운과 최종 이미지를 제공한다.
        - 설명으로 정리하지 말고, 마지막 장면처럼 써라.
        - 상징어, 반복 대사, 감각 모티프가 있다면 은은하게 회수한다.
        - 엔딩은 닫혀 있어야 한다.
        - 마지막 줄은 반드시 단독으로 정확히 `끝.` 이라고 출력한다.
        """
    ).strip()


def build_rewrite_prompt(mode: str, text: str, title: str, genre: str, style_note: str) -> str:
    style = STYLE_NOTE_BLOCK.format(style_note=clean(style_note) or "(없음)", author_style=AUTHOR_STYLE_DNA)
    return dedent(
        f"""
        아래 소설 원고를 `{clean(mode)}` 방향으로 다시 써라.

        [작품명] {clean(title)}
        [장르] {clean(genre)}

        {style}

        [원고]
        {clean(text)}

        규칙:
        - 줄거리 자체를 바꾸기보다 문장, 장면 밀도, 감정 압력, 후킹을 조정한다.
        - Mr.MOON 스타일 DNA를 유지한다.
        - 평범한 AI 설명문처럼 만들지 않는다.
        - 원고가 Unit 12 또는 에필로그라면, 완결감은 훼손하지 않는다.
        """
    ).strip()


def build_title_review_prompt(title: str, working_title: str, genre: str, reinforced_story: str, unit_plan: str, all_drafts_text: str) -> str:
    return dedent(
        f"""
        아래 자료를 바탕으로 현재 가제를 검토하고 대안을 제안하라.

        [작품명] {clean(title)}
        [현재 가제] {clean(working_title)}
        [장르] {clean(genre)}

        [전체 줄거리 보강]
        {clean(reinforced_story)}

        [12 Unit 설계]
        {clean(unit_plan)}

        [생성 원고]
        {clean(all_drafts_text)}

        목표:
        - 현재 가제를 유지할지, 보강할지, 더 강한 대안을 붙일지 판단한다.
        - 반복 대사, 상징어, 마지막 정서, 장르 톤을 함께 고려한다.

        출력 형식:
        1. 현재 가제 유지 여부 (유지 / 보강 / 교체 추천)
        2. 판단 이유
        3. 대안 제목 7개
        4. 가장 상업적인 제목 3개
        5. 가장 영상화에 강한 제목 3개
        6. 필요하면 부제 조합 3개
        """
    ).strip()
