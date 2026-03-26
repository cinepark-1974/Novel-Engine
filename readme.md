#👖BLUE JEANS NOVEL ENGINE

**기획 자료를 입력하면 아마존/교보문고 출판 가능 수준의 장편소설을 단계적으로 설계·집필하는 개인용 소설 엔진**

BLUE JEANS PICTURES 내부 개발 도구 시리즈:
`CREATOR ENGINE` → `WRITER ENGINE` → `SERIES ENGINE` → `REWRITE ENGINE` → **`NOVEL ENGINE`**

---

## 한 줄 정의

기획 자료를 입력받아 10장르 Rule Pack과 Sorkin/Curtis 원칙, 독자 심리 6원칙을 적용하여 분석·보강하고, LOCKED/OPEN 시스템으로 확정 설정을 보호하면서 12 Unit 장편소설 원고를 생성·재작성·저장하는 출판 지향형 소설 집필 엔진이다.

---

## v2.5 핵심 시스템

### 🔒 LOCKED/OPEN 시스템
확정된 설정(캐릭터 소속, 핵심 관계, 세계관 규칙, 기획의도)을 AI가 임의로 변경하지 못하도록 보호한다. 12 Unit 순차 생성 시 후반부에서 초반 설정이 뒤틀리는 문제를 방지.

### 🎬 10장르 Rule Pack
범죄/스릴러, 드라마, 액션, 로맨스, 코미디, 호러/공포, SF, 판타지, 역사, 미지정 — 각 장르별 필수 요소, Hook/Punch 규칙, 오프닝 패턴, 금지 사항, 실패 패턴을 자동 감지하여 전 단계에 주입.

### ✍️ Sorkin/Curtis 9원칙
BUT/EXCEPT 테스트, Intention & Obstacle 압박, Tactics = Character, Too Wet 금지, Curtis 3% 법칙, 감정 연쇄 등 헐리우드 마스터클래스 수준의 서사 원칙을 소설에 적용.

### 🧠 독자 심리 6원칙
Dramatic Irony, Information Gap, Zeigarnik Effect, Pattern & Violation, Delayed Gratification, Mystery Box — 페이지 터너를 만드는 심리 설계를 Unit 설계와 원고 생성에 적용.

### 🤖 듀얼 모델
분석/설계에는 Sonnet, 원고 생성에는 Opus — 비용 효율과 창작 품질을 동시에 확보.

---

## 파이프라인

| STEP | 기능 | 설명 |
|------|------|------|
| **1** | 작품 자료 입력 | 가제, 장르, 형식, 시점, 분량, 개요, 캐릭터, 줄거리, 메모, 문체 샘플, LOCKED/OPEN 설정 |
| **2** | 문체 / 분석 | Style DNA 추출 → 기획서 통합 분석 (장르 Rule Pack + Sorkin 기준) → 부족한 점 진단 |
| **3** | 전체 줄거리 보강 | 기·승·전·결 구간별 분할 보강 (Hook/Punch + 독자 심리 + 감정 연쇄) |
| **4** | 12 Unit 설계 | 2 Unit씩 6개 버튼으로 구조 설계 (독자 심리 원칙 태그 포함) |
| **5** | Unit 원고 생성 / 다시 쓰기 | Opus 모델로 원고 생성 + 챕터 제목 자동 생성 + 6종 리라이트 모드 |
| **6** | 가제 검토 / 제목 제안 | 원고 기반 제목 검토 및 대안 제안 |
| **7** | 저장 / 내보내기 | 현재 Unit / 최종 원고 TXT·DOCX 다운로드 (목차 자동 포함) |

---

## AI 문체 교정 규칙 (Anti-Pattern)

| 코드 | 규칙 |
|------|------|
| A1 | 해설체 종결 금지 (~것이었다, ~터였다) |
| A2 | 격언조 심리 묘사 금지 |
| A3 | 과잉 의미 부여 금지 |
| A4 | 설명적 장면 전환 금지 |
| A5 | 분위기 사족 금지 |
| A6 | 인물 호칭 자연 전환 |
| A7 | 기계적 리듬 반복 금지 |
| A8 | 실존 명칭 금지 |
| A9 | 문단 묶음 규칙 |

---

## 분량 규칙

| Unit | 목표 분량 | 최소 분량 |
|------|----------|----------|
| UNIT 01~02 | 약 7,000자 | 6,000자 |
| UNIT 03~06 | 약 8,000~9,000자 | 6,500~7,000자 |
| UNIT 07~12 | 약 8,000~9,000자 | 6,500~7,000자 |
| UNIT 13 에필로그 | 약 2,500자 | 1,800자 |

---

## 기술 스택

| 구분 | 사용 기술 |
|------|----------|
| Frontend | Streamlit |
| LLM (분석/설계) | Claude Sonnet 4 (Anthropic) |
| LLM (원고 생성) | Claude Opus 4 (Anthropic) |
| Export | python-docx |
| Deploy | Streamlit Cloud + GitHub (cinepark-1974) |

---

## 환경 변수

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `ANTHROPIC_API_KEY` | Claude API 키 (필수) | — |
| `ANTHROPIC_MODEL` | 분석/설계용 모델 | `claude-sonnet-4-20250514` |
| `ANTHROPIC_MODEL_OPUS` | 원고 생성용 모델 | `claude-opus-4-20250514` |

---

## 설치 및 실행

```bash
pip install -r requirements.txt
streamlit run main.py
```

---

## 파일 구조

```
Novel-Engine/
├── .streamlit/
│   └── config.toml
├── storage/
│   └── exports/
├── main.py                   # Streamlit 앱 본체 (1,041줄)
├── prompt.py                 # 프롬프트 모듈 v2.5 (601줄)
├── readme.md
├── NOVEL_ENGINE.md           # 제품설명서
└── requirements.txt
```

---

## 운영 원칙

- 아이디어만 있는 단계는 **CREATOR ENGINE** 사용 권장
- 기존 시나리오 리라이트는 **REWRITE ENGINE** 사용 권장
- NOVEL ENGINE은 **기획안 이후 소설화 단계**에 집중
- 구조는 엔진이 돕고, 최종 취사선택은 작가가 수행

---

## 라이선스

BLUE JEANS PICTURES 내부 사용 도구.

---

*BLUE JEANS NOVEL ENGINE v2.5 — 기획 자료에서 출판 가능한 장편소설까지.*
