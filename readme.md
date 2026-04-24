# 👖 BLUE JEANS NOVEL ENGINE v3.0

장편 대중소설 집필 엔진 — Mr.MOON의 소설 문법 + Creator Engine 동기화

## 설치 및 실행

### Streamlit Cloud
1. GitHub repo: `cinepark-1974/Novel-Engine`
2. Streamlit Cloud에서 배포
3. Secrets에 `ANTHROPIC_API_KEY` 설정

### 로컬 실행
```
streamlit run main.py
```

## 필수 환경변수

| 변수 | 설명 | 예시 |
|------|------|------|
| ANTHROPIC_API_KEY | Anthropic API 키 | sk-ant-... |
| ANTHROPIC_MODEL | 분석/설계 모델 (선택) | claude-sonnet-4-20250514 |
| ANTHROPIC_MODEL_OPUS | 원고 생성 모델 (선택) | claude-opus-4-20250514 |

## 파일 구조

```
Novel-Engine/
├── main.py              # Streamlit 앱 (1,934줄)
├── prompt.py            # 프롬프트 라이브러리 (1,968줄)
├── profession_pack.py   # 19개 직업 팩 (2,586줄, Creator Engine 동기화)
├── period_pack.py       # 10개 시대 팩 (1,605줄, Creator Engine 동기화)
├── requirements.txt     # 의존성
├── .streamlit/
│   └── config.toml      # 테마 설정
├── README.md
└── NOVEL_ENGINE_BRIEFING.md  # 엔진 설명서
```

## requirements.txt

```
streamlit>=1.30.0
anthropic>=0.18.0
python-docx>=1.0.0
lxml>=4.9.0
```

---

## v3.0 업그레이드 (2026-04-24)

### v3.0 신규 모듈 10종

| 모듈 | 명칭 | 핵심 효과 |
|------|------|----------|
| **M1** | BJND Scene Enforcer | 임계치 초과 시 자동 재생성 1회 (있었다/것이었다/대사태그 하드 차단) |
| **M2** | OPENING MASTERY | 장르=오프닝 DNA, 오프닝 도파민≠발단 사건 구분 |
| **M3** | BJND 4축 자기검증 | NECESSITY/AUTHENTICITY/EMPATHY/POTENCY 자체 채점, 14점 미만 재설계 |
| **M4** | Sub-genre OVERRIDE 4종 | ROMCOM / MOBFILM / DRUGFILM / CONMAN |
| **M5** | Profession Pack | 19개 직업 카테고리 자동 주입 (법률/의료/금융기업/언론/공직/요식/교육/엔터/IT/예술/강력수사/건설/농림/마약수사/지능수사/대공/조폭/밀수/화이트칼라) |
| **M6** | Chapter Signature System | Unit별 Opening/Closing Signature 필드 |
| **M7** | Reader Retention Curve | Unit 3/7/10 독자 이탈 피크에 Twist·Betrayal·Information 강제 |
| **M8** | POV Discipline | 1인칭/3인칭 제한/듀얼·다중 각각 HARD CONSTRAINT |
| **M9** | Period Pack | 10개 시대 카테고리 (조선 전기~민주화기) 자동 감지/수동 선택 |
| **M10** | Profession × Period 교차검증 | 시대별 직업 왜곡 방지 (예: 일제강점기 "M&A" 금지) |

### v3.0 BJND 임계치 강화 (v2.5 대비)

| 지표 | v2.5 | v3.0 | 비고 |
|------|------|------|------|
| "있었다" | 15회 | **10회** | 시크릿 퀸 미개선 문제 근본 해결 |
| "것이었다" | 3회 | **2회** | 해설체 강화 차단 |
| 대사 태그 | 12회 | 12회 | 유지 |
| 현재형 종결 | 3회 | 3회 | 유지 (치명적) |

### v3.0 STEP 1 입력 필드 추가

- **주인공 직업** (선택) — Profession Pack 자동 매칭
- **주요 조연/적대자 직업** (선택) — 중복 방지 자동 처리
- **시대 모드** — 현대 / 자동 감지 / 수동 선택
- **시대 선택** (수동 모드) — 10개 시대 중 최대 2개 (교차 전개 지원)

### 자동 재생성 흐름 (M1)

```
Unit 생성 → analyze_unit_quality() 실행
  ↓
위반 지표 severity 판정
  ↓
"critical" 또는 "high" 위반 1건 이상
  ↓
build_retry_hint() → 구체 위반 수치 프롬프트 주입
  ↓
retry_hint 포함 2차 생성
  ↓
1차 vs 2차 비교 → 더 좋은 쪽 채택
```

---

## 파이프라인 (v3.0)

1. **STEP 1** 작품 자료 입력 (가제/장르/형식/시점 + v3.0 직업·시대)
2. **STEP 2** 문체/분석 (Style DNA + 통합 분석 + 부족한 점 진단)
3. **STEP 3** 기승전결 보강
4. **STEP 4** 12 Unit 설계 (BJND 4축 자기검증 + Retention Curve)
5. **STEP 5** Unit 원고 생성 (Chapter 1 3-stage + 자동 재생성 / 일반 Unit 생성)
6. **STEP 6** 가제 검토/제목 제안
7. **STEP 7** 저장/내보내기 (TXT/DOCX)

---

## 주요 기능

- 7단계 파이프라인
- Chapter 1 다단계 생성 (Stage A PEAK / B WORLD / C LOSS)
- 10장르 Rule Pack × 12필드
- 상업소설 5대 기계 (Twist Map, Pacing, Cliffhanger, Betrayal, Information Layer)
- Planting & Payoff + Villain 4 Questions + Goal/Need BJND
- Genre Override 기본 3종 (호러/코미디/로맨스)
- **v3.0 Sub-genre OVERRIDE 4종 (ROMCOM/MOBFILM/DRUGFILM/CONMAN)**
- AI Anti-Pattern A1~A16 + 기능적 조연 규칙
- 품질 자동 체크 + Unit 요약 + 캐릭터 추적
- **v3.0 자동 재생성 (BJND Scene Enforcer)**
- **v3.0 Profession Pack 19 카테고리 자동 주입**
- **v3.0 Period Pack 10 시대 자동 감지/수동 선택**
- **v3.0 POV Discipline (시점 위반 하드 차단)**
- **v3.0 Chapter Signature System (Opening/Closing 시그니처)**
- **v3.0 Reader Retention Curve (Unit 3/7/10 강제 장치)**
- DOCX 소설 원고 포맷 내보내기

---

## 연동 엔진

- Creator Engine v2.3.10 → Novel Engine v3.0 (Profession/Period Pack 동기화)
- Writer Engine v3.1.1 (시나리오 집필 전용)
- Series Engine v1.7 (시리즈)

---

## 라이선스

BLUE JEANS PICTURES 내부 도구. 비공개.

---

**Build 2026-04-24 · v3.0**
