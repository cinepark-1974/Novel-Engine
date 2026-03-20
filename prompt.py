# ─────────────────────────────────────────────────────────────
# BLUE JEANS NOVEL ENGINE v2.0
# prompt.py — System Prompt + Genre Rules + Prompt Builders
# © 2026 BLUE JEANS PICTURES. All rights reserved.
# ─────────────────────────────────────────────────────────────

# =================================================================
# [1] 8장르 RULE PACK
# =================================================================
GENRE_RULES = {
    "드라마": {
        "core": "선택과 대가로 진실에 도달하는 구조. 인물의 내면 변화가 플롯보다 앞선다.",
        "must_have": ["주인공에게 돌이킬 수 없는 선택이 있는가","선택에 대한 실질적 대가가 발생하는가","관계의 질적 변화가 구체적 장면으로 보이는가","B스토리가 테마를 반사하는가"],
        "hook": "일상 속 균열 — 평범함 안에 불안의 씨앗",
        "punch": "돌이킬 수 없는 관계 변화 — 말로 돌아갈 수 없는 순간",
        "fails": ["선택 없이 사건만 나열","감정을 대사로 직접 설명","모든 갈등이 오해에서 발생하고 대화로 해소","테마 없이 에피소드만 나열"],
        "genre_fun": "독자가 인물의 선택 앞에서 나라면 어떻게 할까를 고민하게 만드는 것"
    },
    "느와르": {
        "core": "도덕적 모호함. 타락과 생존 사이의 선택. 누구도 깨끗하지 않다.",
        "must_have": ["주인공의 도덕선이 점진적으로 무너지는가","배신의 레이어가 2중 이상인가","거래/협박/뒷거래가 서사를 추동하는가","결말에서 승리가 아닌 생존이 목표인가"],
        "hook": "냉소적 내면 또는 거부할 수 없는 거래 제안",
        "punch": "배신 — 가장 신뢰한 자에 의한 반전",
        "fails": ["선악이 명확하게 나뉜 구도","주인공이 처음부터 끝까지 도덕적","폭력이 쿨해 보이기 위한 장식","반전 없는 직선형 복수극"],
        "genre_fun": "독자가 나쁜 줄 알면서도 응원하게 되는 도덕적 긴장"
    },
    "스릴러": {
        "core": "정보의 비대칭과 시간 압박. 독자는 인물보다 많이 알거나 적게 안다.",
        "must_have": ["명확한 시간 제한 또는 카운트다운이 있는가","독자와 인물 사이 정보 비대칭이 설계되었는가","안전 공간이 무너지는 순간이 있는가","단서가 의미 반전되는가"],
        "hook": "시계/감시/안전 붕괴 — 일상적 안전감의 파괴",
        "punch": "단서 뒤집힘 — 믿었던 정보가 거짓이었음이 밝혀지는 순간",
        "fails": ["긴장 없이 수사 절차만 나열","주인공이 실수 없이 모든 것을 해결","독자에게 단서를 숨겨놓고 마지막에 공개","위협이 추상적이고 물리적으로 느껴지지 않음"],
        "genre_fun": "독자가 제발 뒤를 봐!라고 속으로 외치게 만드는 정보 비대칭"
    },
    "코미디": {
        "core": "웃음의 메커니즘 — 기대 위반, 반복과 변주, 결함 있는 인물의 집착.",
        "must_have": ["주인공에게 우스꽝스러운 결함이 있는가","상황이 계속 악화되는 에스컬레이션이 있는가","Setup-Punchline 리듬이 장면 단위로 작동하는가","Callback이 있는가"],
        "hook": "비틀린 일상 — 결함 있는 행동이 연쇄 반응을 일으키는 첫 장면",
        "punch": "Callback + 더 꼬인 상황 — 해결하려 할수록 악화",
        "fails": ["대사로만 웃기려 하고 상황 코미디가 없음","캐릭터 결함이 불쾌함으로 전락","에스컬레이션 없이 같은 수준의 개그 반복","코미디 속 감정선이 전혀 없음"],
        "genre_fun": "독자가 저러다 큰일 나겠다면서 멈출 수 없이 읽게 되는 에스컬레이션"
    },
    "멜로/로맨스": {
        "core": "갈망의 축적과 감정의 지연. 만남보다 만나지 못함이 서사를 추동한다.",
        "must_have": ["두 인물 사이에 명확한 장애물이 있는가","감정의 지연과 긴장이 설계되었는가","시선/거리/접촉의 단계적 축적이 있는가","이별 또는 위기에서 관계의 본질이 드러나는가"],
        "hook": "시선과 닿을 듯한 거리 — 첫 만남의 전율",
        "punch": "타이밍의 어긋남 또는 접촉의 전율 — 간절함이 최고조에 달하는 순간",
        "fails": ["만남-사랑-이별-재회가 기계적으로 진행","장애물이 오해 하나뿐","감정이 대사로만 전달","상대가 매력적인 이유가 외모뿐"],
        "genre_fun": "독자가 두 사람의 손이 닿기 직전에 숨을 멈추게 되는 감정 지연"
    },
    "호러": {
        "core": "공포의 예감과 안전감의 파괴. 보이지 않는 것이 보이는 것보다 무섭다.",
        "must_have": ["평범한 것이 이상하게 느껴지는 Uncanny 설정이 있는가","가짜 안도 후 진짜 공포가 오는 리듬이 있는가","공포의 규칙이 설정되고 위반되는가","독자가 보지 마 열지 마라고 외치는 순간이 있는가"],
        "hook": "평범한 것의 이상함 — 익숙한 공간에서의 미세한 균열",
        "punch": "가짜 안도 후 진짜 공포 — 끝났다고 생각한 순간의 반전",
        "fails": ["점프 스케어에만 의존","공포의 규칙이 불명확","주인공이 독자보다 멍청한 선택만 반복","고어가 공포를 대체"],
        "genre_fun": "독자가 페이지를 넘기기 무서우면서도 멈출 수 없게 만드는 공포의 예감"
    },
    "액션": {
        "core": "물리적 목표와 신체적 대가. 매 시퀀스마다 무엇을 걸고 싸우는가가 명확해야 한다.",
        "must_have": ["액션 시퀀스마다 명확한 목표가 있는가","물리적 공간이 전술적으로 활용되는가","대가가 실질적인가","각 액션이 에스컬레이션되는가"],
        "hook": "명확한 목표와 공간 설정 — 무엇을 위해 어디서 싸우는지",
        "punch": "전술 뒤집힘과 대가 — 예상치 못한 방법과 실질적 손실",
        "fails": ["액션이 스토리와 무관한 볼거리","주인공이 무적","동일 패턴의 액션 반복","빌런의 능력이 불명확"],
        "genre_fun": "독자가 어떻게 이걸 해결하지?라고 조마조마하는 전술적 긴장"
    },
    "SF/판타지": {
        "core": "세계 규칙 = 인간 드라마의 은유. 설정이 테마를 구현하는 도구여야 한다.",
        "must_have": ["세계 규칙이 명확하게 설정되었는가","규칙 위반/사용에 대가가 있는가","설정이 현실 인간 드라마의 은유로 기능하는가","세계관 설명이 장면 속 행동으로 보여지는가"],
        "hook": "다른 세계의 첫 이미지 — 규칙이 다른 세계로의 초대",
        "punch": "규칙의 대가와 비밀 연결 — 설정이 캐릭터의 운명과 직결되는 순간",
        "fails": ["세계관 설명이 대사/나레이션으로 장황하게 전달","규칙에 예외가 너무 많아 긴장감 소멸","설정이 멋있지만 인간 드라마와 무관","Deus ex machina"],
        "genre_fun": "독자가 이 세계에서는 그게 가능해?라며 규칙을 이해해가는 발견의 쾌감"
    }
}

GENRE_KEYWORD_MAP = [
    (["느와르","noir","누아르","crime noir"],"느와르"),
    (["스릴러","thriller","미스터리","mystery","서스펜스"],"스릴러"),
    (["멜로","로맨스","romance","melo","love"],"멜로/로맨스"),
    (["코미디","comedy","로코","rom-com","블랙코미디"],"코미디"),
    (["호러","horror","공포","오컬트","occult"],"호러"),
    (["액션","action","전쟁","war","무협"],"액션"),
    (["sf","sci-fi","판타지","fantasy","타임","사이버펑크"],"SF/판타지"),
    (["드라마","drama","가족","성장","human"],"드라마"),
]

def detect_genre_key(genre_str):
    gl = genre_str.lower()
    for kws, gk in GENRE_KEYWORD_MAP:
        if any(k in gl for k in kws):
            return gk
    return "드라마"

def get_genre_rules_block(genre_key):
    r = GENRE_RULES.get(genre_key, GENRE_RULES["드라마"])
    ml = "\n".join([f"  - {m}" for m in r["must_have"]])
    fl = "\n".join([f"  - {f}" for f in r["fails"]])
    return f"""[장르 Rule Pack: {genre_key}]
핵심 원칙: {r['core']}
장르적 재미의 본질: {r['genre_fun']}
필수 요소:
{ml}
Hook(장면 시작): {r['hook']}
Punch(장면 종결): {r['punch']}
장르 실패 패턴:
{fl}
"""

# =================================================================
# [2] SYSTEM PROMPT
# =================================================================
SYSTEM_PROMPT = """당신은 BLUE JEANS NOVEL ENGINE이다.
사용자가 입력한 기획 자료를 바탕으로 아마존/교보문고에서 바로 판매 가능한 수준의
장편 대중소설 원고를 생성하는 전문 소설 집필 엔진이다.

[Voice First — 원고 품질 원칙]
1. 설명보다 체험을 우선한다. 줄거리 요약처럼 쓰지 말고 실제 장면으로 전개한다.
2. 설정 설명은 백과사전처럼 길게 풀지 말고 사건, 행동, 대사, 반응 속에 녹인다.
3. 장면은 갈등, 감정 변화, 정보 공개/은폐, 선택 압력 중 하나 이상을 가진다.
4. 대사는 기능적이어야 하며 갈등, 관계 변화, 정보 전진에 기여해야 한다.
5. 문장은 난해하지 않되 화면이 보이게 쓴다.
6. 중요한 감정은 직접 진술만 하지 말고 시선, 침묵, 몸짓, 행동으로도 드러낸다.
7. 장르적 정보는 설명이 아니라 위기, 반전, 선택의 장치로 쓴다.

[행동과 심리 디테일 규칙 — SPECIFICITY]
1. 감정을 설명하지 말고 행동으로 보여라. '떨린다' 대신 '손이 움직이지 않는다'.
2. 수동적 반응 금지: '미끄러진다' 같은 수동태 대신 인물의 능동적 선택을 보여라.
3. 인물의 선택(Choice)이 장면의 핵심이다. 선택을 우연한 반응으로 바꾸면 실패.
4. 구체적 사물과 공간 디테일: '서류'가 아니라 '습기를 먹어 서로 들러붙은 종이'처럼 감각적으로.
5. 신체의 미세한 움직임이 감정을 전달한다. 절대 생략하지 마라.

[AI 문체 교정 규칙 — ANTI-PATTERN]
A1. '~것이었다','~터였다','~셈이었다' 해설체 종결 금지. 단정형으로 끝낸다.
A2. 인물의 심리를 격언이나 철학적 진술로 풀지 않는다. 행동, 선택, 한 줄 판단으로 보여준다.
A3. 모든 문장이 의미심장하려 하지 않는다. 가벼운 문장, 빈 공간이 있어야 진짜 리듬이다.
A4. 장면 전환을 설명하지 않는다. 다음 행동으로 바로 넘어간다.
A5. 플롯에 기여하지 않는 분위기 묘사를 넣지 않는다.
A6. 인물 호칭은 자연스럽게 전환한다. 첫 등장은 풀네임, 이후 성 또는 이름.
A7. '짧은문장. 짧은문장. 그리고 긴 문장' 패턴을 기계적으로 반복하지 않는다.
A8. 실존 호텔, 기업, 장소 이름을 그대로 쓰지 않는다.
A9. 매 문장마다 줄바꿈하지 않는다. 흐름이 있는 문단으로 묶는다.

[완결 규칙]
1. Unit 12는 반드시 본편을 마무리해야 한다.
2. Unit 13은 선택형 에필로그이며 후일담과 여운 중심으로 쓴다.
3. Unit 12 또는 Unit 13의 마지막 줄에 정확히 '끝.' 을 단독으로 둔다.
4. 원고 생성 시 반드시 목표 분량을 충족한다.
5. 토큰이 부족해 끊길 위험이 있으면 완결된 문장으로 끝낸다.
""".strip()

# =================================================================
# [3] AUTHOR STYLE DNA
# =================================================================
AUTHOR_STYLE_DNA_BASE = """Mr.MOON 스타일 기본 규칙:
- 영화친화적인 상업 장편소설 톤으로 쓴다.
- 장면은 공간, 빛, 냄새, 소리, 촉감 중 최소 1개 이상의 감각 요소로 진입할 수 있다.
- 세계관 설명은 사건, 행동, 인물 반응, 대사 속에 배치한다.
- 주요 인물은 첫 등장 장면에서 직업, 결핍, 비밀, 욕망 중 최소 2개가 드러나야 한다.
- 대사는 멋을 부리기보다 갈등, 관계 변화, 정보 전진에 기여해야 한다.
- 감정은 직접 말할 수 있으나 결정적 장면에서는 시선, 침묵, 몸짓, 행동으로 보여준다.
- 로맨스는 플롯과 분리하지 말고 정보 교환, 위험 노출, 계급/권력 충돌과 함께 전진시킨다.
- 장면 말미에는 반전, 위협, 감정 흔들림, 선택 압력 중 하나를 남긴다.
- 감각어와 물성어를 반복 모티프로 사용할 수 있다.
- 문장은 중간 길이를 기본으로 하되 전환과 충격 지점에서는 짧게 끊는다.
- 설명문이 길어지면 장면과 대사로 환원한다.

문체 금지 패턴:
- '~것이었다','~터였다','~셈이었다' 종결 금지.
- 인물 심리를 격언/비유/철학적 진술로 풀지 않는다.
- 장면 전환 시 설명적 연결 대신 다음 행동으로 넘어간다.
- 플롯에 기여하지 않는 분위기 묘사를 넣지 않는다.
- 인물 풀네임을 끝까지 반복하지 않는다.
- 기계적 리듬 반복 금지.
- 실존 명칭 금지.
- 매 문장 줄바꿈 금지.""".strip()

# =================================================================
# [4] STYLE DNA ANALYSIS
# =================================================================
STYLE_DNA_ANALYSIS_PROMPT = """다음 문체 샘플을 분석해 Style DNA를 작성하라.

요구사항:
- 샘플 줄거리를 요약하지 말고 문체의 구조적 특징을 추출할 것
- 칭찬 위주가 아니라 제어 가능한 규칙으로 정리할 것

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
{style_sample}""".strip()

# =================================================================
# [5] HELPERS
# =================================================================
def _style_block(style_dna, style_strength="중"):
    sm = {"약":"문체 특징을 은은하게 반영하되 장르 요구와 가독성을 우선한다.","중":"문체 특징을 분명히 반영하되 반복감이나 자기복제는 피한다.","강":"문체 특징을 강하게 반영하되 작품 전체의 추진력과 가독성은 무너뜨리지 않는다."}
    return f"[기본 STYLE DNA]\n{AUTHOR_STYLE_DNA_BASE}\n\n[사용자 STYLE DNA]\n{style_dna or '사용자 문체 샘플 분석 결과 없음. 기본 STYLE DNA만 사용한다.'}\n\n[문체 반영 강도]\n{sm.get(style_strength, sm['중'])}"

def _genre_block(genre):
    return get_genre_rules_block(detect_genre_key(genre))

# =================================================================
# [6] PROMPT BUILDERS
# =================================================================
def build_merge_analysis_prompt(working_title,genre,format_mode,pov,target_length,overview,characters,synopsis,notes,style_dna,style_strength):
    return f"""다음 자료를 통합 분석하여 장편소설 개발용 진단 리포트를 작성하라.

요구사항:
- 장황한 미사여구 금지
- 장르 Rule Pack 기준으로 장르적 재미가 살아있는지 반드시 진단할 것

출력 형식:
1. 한 줄 콘셉트
2. 작품의 강점 5개
3. 장편화 위험요소 5개
4. 장르 톤 정의
5. 주인공 아크 요약
6. 적대 구조 요약
7. 관계 축 요약
8. 정보/시대/세계관 처리 포인트
9. 장르적 재미 진단 (필수 요소 충족 여부, 실패 패턴 해당 여부)
10. 즉시 보강이 필요한 핵심 3개

{_genre_block(genre)}

[가제] {working_title}
[장르] {genre}
[형식] {format_mode}
[시점] {pov}
[목표 분량] {target_length}
[작품 개요] {overview}
[캐릭터] {characters}
[줄거리 / 트리트먼트] {synopsis}
[추가 메모] {notes}

{_style_block(style_dna, style_strength)}""".strip()


def build_gap_diagnosis_prompt(working_title,merged_analysis,overview,characters,synopsis,notes,style_dna):
    return f"""다음 작품의 부족한 점을 장편소설 기준으로 진단하라.

출력 형식:
1. 구조적 부족점
2. 인물의 부족점
3. 감정선의 부족점
4. 장르적 부족점 (Rule Pack 기준)
5. 정보/시대/세계관의 과다 또는 부족
6. 중반부 붕괴 위험
7. 엔딩 약화 위험
8. 가장 먼저 보강해야 할 5개 항목
9. 각 항목별 구체적 대안

[가제] {working_title}
[통합 분석] {merged_analysis}
[작품 개요] {overview}
[캐릭터] {characters}
[줄거리 / 트리트먼트] {synopsis}
[추가 메모] {notes}
[STYLE DNA] {style_dna}""".strip()


def build_story_reinforcement_prompt(segment_name,working_title,genre,overview,characters,synopsis,notes,merged_analysis,gap_diagnosis,style_dna):
    sr = {"기":"세계 진입, 주인공 소개, 결핍/욕망 제시, 발화 사건, 되돌릴 수 없는 선택","승":"상황 확장, 관계 심화, 첫 성공과 첫 대가, 판 확대, 적대 구조 선명화","전":"중반 반전, 배신/상실/균열, 추락과 재정렬, 진실 접근, 결전 압축","결":"결전 준비, 클라이맥스, 감정 회수, 본편 마무리"}
    return f"""다음 작품의 '{segment_name}' 구간만 보강하라.

구간 기능: {sr.get(segment_name,"")}

요구사항:
- 장르 Rule Pack의 Hook/Punch 패턴을 구간 내 핵심 장면에 반영할 것
- 장편소설 분량을 버틸 수 있는 갈등과 장면을 제안할 것

출력 형식:
1. 구간 역할
2. 핵심 사건 흐름
3. 인물/관계 변화
4. 감정 흐름
5. 반드시 살아야 할 장면 3~5개 (각 장면에 Hook/Punch 포함)
6. 약한 부분 보강 포인트
7. 다음 구간으로 넘기는 연결점

{_genre_block(genre)}

[가제] {working_title}
[장르] {genre}
[작품 개요] {overview}
[캐릭터] {characters}
[줄거리 / 트리트먼트] {synopsis}
[추가 메모] {notes}
[통합 분석] {merged_analysis}
[부족한 점 진단] {gap_diagnosis}
[STYLE DNA] {style_dna}""".strip()


def build_unit_blueprint_prompt(group_key,working_title,genre,format_mode,pov,overview,characters,story_reinforcement_merged,synopsis,notes,style_dna):
    gm = {"01-02":"기 구간 초반. 오프닝, 세계 진입, 발화 사건","03-04":"기에서 승으로. 되돌릴 수 없는 선택, 상황 확장","05-06":"승 구간 심화. 관계 확장, 첫 대가, 판 확대","07-08":"전 구간 진입. 중반 반전, 균열, 배신, 상실","09-10":"전에서 결로. 추락, 재정렬, 결전 준비","11-12":"결 구간. 클라이맥스, 정서 회수, 본편 마무리"}
    return f"""다음 작품의 UNIT {group_key} 설계를 작성하라.

구간 의미: {gm.get(group_key,"")}

요구사항:
- 각 Unit의 시작(Hook)과 끝(Punch)을 장르 Rule Pack 기준으로 설계할 것
- Unit 12가 포함된 경우 반드시 본편을 마무리하도록 설계할 것

출력 형식:
[UNIT XX]
- 제목:
- 서사 기능:
- 핵심 사건:
- 감정 변화:
- Hook (장면 시작):
- Punch (장면 종결):

{_genre_block(genre)}

[가제] {working_title}
[장르] {genre}
[형식] {format_mode}
[시점] {pov}
[작품 개요] {overview}
[캐릭터] {characters}
[줄거리 / 트리트먼트] {synopsis}
[기승전결 보강본] {story_reinforcement_merged}
[추가 메모] {notes}
[STYLE DNA] {style_dna}""".strip()


def build_unit_draft_prompt(unit_no,working_title,genre,format_mode,pov,overview,characters,synopsis,notes,story_reinforcement_merged,all_blueprints_text,previous_drafts,style_dna,style_strength,target_length,min_length):
    if unit_no == 12:
        fr = "이 Unit은 본편의 마지막이다. 중심 갈등을 종결하고 감정적/플롯적 회수를 수행하라. 마지막 줄에 '끝.' 을 출력하라."
    else:
        fr = "아직 본편의 마지막이 아니므로 '끝.' 을 출력하지 않는다. 다음 Unit으로 넘어가게 하는 Punch를 남긴다."
    gk = detect_genre_key(genre)
    r = GENRE_RULES.get(gk, GENRE_RULES["드라마"])
    return f"""다음 작품의 UNIT {unit_no:02d} 실제 원고를 작성하라.

챕터 제목 규칙:
- 원고의 첫 줄에 반드시 [CHAPTER {unit_no}] — 서브타이틀 형식으로 챕터 제목을 출력할 것
- 서브타이틀은 이 챕터에서 독자가 가장 기억할 것(장소 또는 인물)을 기준으로 선택

[장르적 재미 규칙]
장르적 재미의 본질: {r['genre_fun']}
Hook(장면 시작): {r['hook']}
Punch(장면 종결): {r['punch']}
- 이 Unit의 첫 장면은 반드시 Hook 패턴으로 시작할 것
- 이 Unit의 마지막 장면은 반드시 Punch 패턴으로 끝낼 것

중요 원칙:
- 줄거리 요약처럼 쓰지 말고 실제 소설 원고로 쓸 것
- 최소 4개의 장면 블록 (도입/전개/전환/마감)
- 감각적 진입, 행동, 대사, 갈등, 감정 변화가 살아 있어야 한다
- 중요한 대면 장면은 축약하지 말 것
- 목표 분량 약 {target_length}자, 최소 {min_length}자 이상
- 분량이 부족하면 장면, 대화, 감정 반응, 행동 묘사를 확장해 채울 것
- 서문이나 메타 설명 없이 바로 원고 본문부터 시작할 것

추가 규칙: {fr}

[가제] {working_title}
[장르] {genre}
[형식] {format_mode}
[시점] {pov}
[작품 개요] {overview}
[캐릭터] {characters}
[줄거리 / 트리트먼트] {synopsis}
[추가 메모] {notes}
[기승전결 보강본] {story_reinforcement_merged}
[전체 Unit 설계] {all_blueprints_text}
[이전까지 작성된 Unit 원고] {previous_drafts or "이전 원고 없음"}

{_style_block(style_dna, style_strength)}""".strip()


def build_expand_incomplete_unit_prompt(unit_no,current_text,target_length,min_length):
    fr = "마지막 줄에 '끝.' 을 출력하라." if unit_no in (12,13) else "'끝.' 을 붙이지 않는다."
    return f"""다음 UNIT 원고는 분량이 부족하거나 끝맺음이 미완성이다.
기존 텍스트를 반복하지 말고 바로 이어서 장면을 확장하고 마무리를 완성하라.

요구사항:
- 톤, 시점, 흐름 유지
- 요약문으로 건너뛰지 말 것
- 전체 결과가 최소 {min_length}자 이상, 가능하면 {target_length}자 내외
- 서문 없이 바로 이어서 쓸 것
- {fr}

[현재 원고]
{current_text}""".strip()


def build_unit_rewrite_prompt(unit_no,rewrite_mode,source_text,style_dna,target_length,min_length):
    er = "마지막 줄에 '끝.' 을 유지한다." if unit_no in (12,13) else "'끝.' 을 붙이지 않는다."
    return f"""다음 UNIT 원고를 '{rewrite_mode}' 방향으로 다시 써라.

요구사항:
- 플롯을 함부로 바꾸지 말고 문장, 장면 밀도, 감정 전달, 후킹, 가독성을 개선할 것
- 원본보다 짧아지면 실패. 원본의 분량을 유지하거나 늘려라.
- 최소 {min_length}자 이상, 가능하면 {target_length}자 내외
- 서문 없이 바로 원고 본문부터 출력할 것
- {er}

[STYLE DNA]
{style_dna}

[원고]
{source_text}""".strip()


def build_epilogue_prompt(working_title,genre,overview,characters,synopsis,story_reinforcement_merged,all_blueprints_text,all_drafts_text,style_dna):
    return f"""다음 작품의 UNIT 13 에필로그를 작성하라.

챕터 제목 규칙:
- 첫 줄에 [CHAPTER 13] — 에필로그 형식으로 출력할 것

요구사항:
- 약 2000~3000자 내외의 정서적 마무리
- 본편을 다시 뒤집지 말 것
- 후일담, 여운, 상징 회수, 관계의 잔향 중심
- 서문 없이 바로 에필로그 본문부터 시작할 것
- 마지막 줄에 '끝.' 을 출력할 것

[가제] {working_title}
[장르] {genre}
[작품 개요] {overview}
[캐릭터] {characters}
[줄거리 / 트리트먼트] {synopsis}
[기승전결 보강본] {story_reinforcement_merged}
[전체 Unit 설계] {all_blueprints_text}
[본편 원고] {all_drafts_text}
[STYLE DNA] {style_dna}""".strip()


def build_title_review_prompt(current_title,overview,synopsis,story_reinforcement_merged,all_blueprints_text,all_drafts_text,style_dna):
    return f"""현재 가제를 검토하고 원고 기반 제목 대안을 제안하라.

출력 형식:
1. 현재 가제 유지 여부
2. 유지 또는 비추천 이유
3. 현재 가제를 살린 보강안 5개
4. 새 대안 제목 10개
5. 영상화형 제목 5개
6. 문학/정서형 제목 5개
7. 가장 추천하는 최종 후보 3개와 이유

[현재 가제] {current_title}
[작품 개요] {overview}
[줄거리 / 트리트먼트] {synopsis}
[기승전결 보강본] {story_reinforcement_merged}
[전체 Unit 설계] {all_blueprints_text}
[생성 원고] {all_drafts_text}
[STYLE DNA] {style_dna}""".strip()
