# 👖 BLUE JEANS NOVEL ENGINE v3.1

장편 대중소설 집필 AI 엔진 — 시나리오 소설화 모드 추가

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
├── main.py                  # Streamlit 앱 (2,133줄)
├── prompt.py                # 프롬프트 라이브러리 (1,976줄)
├── scenario_extractor.py    # v3.1 시나리오 추출기 (370줄, 신규)
├── profession_pack.py       # 19개 직업 팩 (2,586줄)
├── period_pack.py           # 10개 시대 팩 (1,605줄)
├── requirements.txt
├── .streamlit/config.toml
└── README.md
```

## requirements.txt

```
streamlit>=1.30.0
anthropic>=0.18.0
python-docx>=1.0.0
lxml>=4.9.0
```

---

## v3.1 업그레이드 — 시나리오 소설화 모드 (2026-04-24)

### 핵심 기능

**STEP 0 · 시나리오 업로드**
기존에 써둔 시나리오(.docx / .txt)를 업로드하면 Sonnet이 자동으로:
- 로그라인, 장르, 작품 개요, 캐릭터 시트, 기승전결 트리트먼트 추출
- 주인공/적대자 직업 추출 (Profession Pack 자동 매칭)
- 시대 키 추출 (Period Pack 자동 매칭)
- LOCKED / OPEN 블록 구성
- **12 Unit 매핑 가이드** 생성 (시나리오 씬 → 소설 Unit 대응)

### 동작 흐름

```
[STEP 0] 시나리오 업로드 (.docx / .txt / 붙여넣기)
    ↓
구조 통계 표시 (글자수 / 씬 수 / V.O / CUT / 회상)
    ↓
"🧬 Sonnet 자동 추출 실행" 버튼
    ↓ (30~60초)
추출 결과를 STEP 1 모든 필드에 자동 입력
+ 12 Unit 매핑 가이드를 세션 상태에 저장
    ↓
[STEP 1] 자동 입력된 필드 검토·수정
    ↓
[STEP 2~3] 평소대로 (문체 분석 + 기승전결 보강)
    ↓
[STEP 4] Unit 설계 시 매핑 가이드가 자동 주입됨
    ↓
[STEP 5] Chapter 1 Stage A/B/C + Unit 02~12 생성
    ↓ (BJND Scene Enforcer 자동 재생성 포함)
[STEP 6~7] 제목 검토 + DOCX 내보내기
```

### v3.1 신규 모듈

| 모듈 | 설명 |
|------|------|
| **STEP 0 UI** | .docx/.txt 파일 업로드 + 텍스트 붙여넣기 듀얼 입력 |
| **구조 통계** | 글자수/씬수/V.O/CUT/회상 자동 카운트 |
| **Sonnet 추출기** | 시나리오 1회 호출로 12개 필드 + 매핑 가이드 생성 |
| **자동 입력** | 모든 STEP 1 필드에 추출 결과 기본값 주입 (수정 가능) |
| **12 Unit 매핑 주입** | STEP 4 blueprint 프롬프트에 매핑 가이드 자동 주입 |

---

## v3.0 기존 모듈 10종 (v3.1에서도 모두 유지)

| 모듈 | 명칭 | 핵심 효과 |
|------|------|----------|
| **M1** | BJND Scene Enforcer | 임계치 초과 시 자동 재생성 1회 |
| **M2** | OPENING MASTERY | 장르=오프닝 DNA, 오프닝 도파민≠발단 사건 |
| **M3** | BJND 4축 자기검증 | NECESSITY/AUTHENTICITY/EMPATHY/POTENCY |
| **M4** | Sub-genre OVERRIDE 4종 | ROMCOM/MOBFILM/DRUGFILM/CONMAN |
| **M5** | Profession Pack | 19개 직업 카테고리 자동 주입 |
| **M6** | Chapter Signature System | Opening/Closing Signature 필드 |
| **M7** | Reader Retention Curve | Unit 3/7/10 강제 장치 |
| **M8** | POV Discipline | 시점 위반 HARD CONSTRAINT |
| **M9** | Period Pack | 10개 시대 자동 감지/수동 선택 |
| **M10** | Profession × Period 교차검증 | 시대별 직업 왜곡 방지 |

### BJND 임계치

| 지표 | v2.5 | v3.0/3.1 | 비고 |
|------|------|----------|------|
| "있었다" | 15회 | **10회** | 시크릿 퀸 미개선 문제 해결 |
| "것이었다" | 3회 | **2회** | 해설체 차단 |
| 대사 태그 | 12회 | 12회 | 유지 |
| 현재형 종결 | 3회 | 3회 | 치명적 |

---

## 사용 시나리오

### 시나리오 A — 시나리오 → 소설 (v3.1 주용도)
기존 시나리오가 있는 경우:
1. STEP 0에서 업로드
2. "Sonnet 자동 추출" 클릭
3. STEP 1 필드 검토·미세조정
4. STEP 2~7 평소대로 진행

### 시나리오 B — 백지 기획 → 소설 (v3.0 기본 모드)
시나리오 없이 처음부터 쓰는 경우:
1. STEP 0을 건너뛰기
2. STEP 1부터 수동 입력
3. STEP 2~7 평소대로 진행

---

## 연동 엔진

- Creator Engine v2.3.10 → Novel Engine v3.1 (Profession/Period Pack 동기화)
- Writer Engine v3.1.1 (시나리오 집필 전용)
- Series Engine v1.7 (시리즈)

---

## 라이선스

BLUE JEANS PICTURES 내부 도구. 비공개.

---

**Build 2026-04-24 · v3.1 / Scenario-to-Novel Mode**
