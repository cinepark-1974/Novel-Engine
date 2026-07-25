# 👖 BLUE JEANS NOVEL ENGINE v3.11.0

**A CINEMATIC NOVEL ENGINE**
영화를 연상시키는 속도감 · 3막 15비트 구조 · 소설만의 묘사와 심리

---

## CINEMATIC NOVEL이란

만화를 **그래픽 노블**이라 부르는 것과 같은 층위의 용어다.

- **속도감** — 글이 영화를 연상시킬 만큼 빠르게 전개된다. 장면은 사건이 시작되는 지점부터 시작하고, 인물이 도착하고 앉고 인사하는 과정은 쓰지 않는다.
- **구조** — 3막 15비트의 탄탄한 서사 골격 위에 놓인다. 12 Unit은 이 3막 구조를 쪼갠 것이다.
- **소설의 무기** — 영상 문법은 배제하되, 묘사·심리 설명이라는 소설의 장점을 끌어온다.

시나리오와의 결정적 차이는 여기다. **시나리오는 카메라가 볼 수 있는 것만 쓴다. 시네마틱 노블은 카메라가 볼 수 없는 것 — 내면, 기억, 주관적 감각 — 까지 쓴다.** 그것이 이 형식의 존재 이유이며, 그 무기를 버리면 시나리오의 열화판이 될 뿐이다.

동시에 영상 제작 문법은 들어오지 않는다. 카메라·앵글·컷·클로즈업 같은 촬영 용어, 지문처럼 동작만 나열하는 서술, 씬 넘버링은 금지된다.

---

## 설치 및 실행

### Streamlit Cloud
1. GitHub repo: `cinepark-1974/Novel-Engine`
2. Streamlit Cloud에서 배포
3. Secrets에 `ANTHROPIC_API_KEY` 설정

### 로컬 실행
```
streamlit run main.py
```

## 환경변수

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `ANTHROPIC_API_KEY` | Anthropic API 키 (필수) | — |
| `ANTHROPIC_MODEL` | 분석·설계·추출 모델 | `claude-sonnet-5` |
| `ANTHROPIC_MODEL_OPUS` | 원고 집필 모델 | `claude-opus-4-8` |

## 파일 구조

```
Novel-Engine/
├── main.py                  # Streamlit 앱 (약 2,880줄)
├── prompt.py                # 프롬프트 라이브러리 · 룰셋 M1~M14 (약 2,880줄)
├── scenario_extractor.py    # 시나리오 → 12키 추출기 (약 550줄)
├── creator_extractor.py     # Creator Engine JSON 소설화 (약 820줄)
├── idea_extractor.py        # Idea Engine JSON 소설화 (약 830줄)
├── profession_pack.py       # 19개 직업 팩 (2,586줄)
├── period_pack.py           # 10개 시대 팩 (1,605줄)
├── requirements.txt
├── .streamlit/config.toml
└── readme.md
```

## requirements.txt

```
streamlit>=1.30
anthropic>=0.40
python-docx>=1.1.0
```

---

## 동작 흐름

```
[프로젝트 저장 / 불러오기]  작업 상태 전체를 JSON 한 파일로 백업·복원
    ↓
[STEP 0] 원작 불러오기 (3탭 — 선택)
    · 기존 원고 (시나리오 .docx/.txt/붙여넣기)
    · Idea Engine JSON (기획 씨앗)
    · Creator Engine JSON (확정 기획, 영화/시리즈)
    ↓ Sonnet 1회 호출로 12개 필드 + 12 Unit 매핑 가이드 생성
[STEP 1] 작품 자료 검토·수정 (자동 입력된 값은 초안)
    ↓
[STEP 2] 문체 분석 · 기획서 통합 분석 · 부족한 점 진단
    ↓
[STEP 3] 기승전결 4구간 보강
    ↓
[STEP 4] 12 Unit 설계 (2 Unit씩 6그룹)
    ↓ 3막 15비트 좌표 + 장르 배합 비중 자동 주입
[STEP 5] Chapter 1 Stage A/B/C + Unit 02~12 집필
    ↓ BJND Scene Enforcer 자동 재생성 · 잘림 감지
[STEP 6] 원고 기반 제목 검토
    ↓
[STEP 7] TXT / DOCX 내보내기
```

STEP 0을 건너뛰고 STEP 1부터 수동 입력해도 된다.

---

## 룰셋 모듈

### v3.0 기반 모듈 (M1~M10)

| 모듈 | 명칭 | 핵심 효과 |
|------|------|----------|
| **M1** | BJND Scene Enforcer | 임계치 초과 시 자동 재생성 1회 |
| **M2** | OPENING MASTERY | 캐릭터 앵커 오프닝 (v3.8 재개정) |
| **M3** | BJND 4축 자기검증 | NECESSITY / AUTHENTICITY / EMPATHY / POTENCY |
| **M4** | Sub-genre OVERRIDE | ROMCOM / MOBFILM / DRUGFILM / CONMAN |
| **M5** | Profession Pack | 19개 직업 카테고리 자동 주입 |
| **M6** | Chapter Signature System | Opening / Closing Signature |
| **M7** | Reader Retention Curve | Unit 3/7/10 강제 장치 |
| **M8** | POV Discipline | 시점 위반 HARD CONSTRAINT |
| **M9** | Period Pack | 10개 시대 자동 감지 / 수동 선택 |
| **M10** | Profession × Period 교차검증 | 시대별 직업 왜곡 방지 |

### v3.5~v3.11 신규 모듈 (M11~M14)

| 모듈 | 명칭 | 핵심 효과 |
|------|------|----------|
| **M11** | Behavioral Repetition Guard | 습관을 목록이 아닌 기질로. 동일 동작 작품 전체 2회 제한 |
| **M12** | Event Mandate | 매 Unit 현재 시점 사건 필수. 회상 30% 제한 |
| **M13** | Paragraph Rhythm | 문단·대사 리듬 (작가 완성 원고 12만자 실측 기반) |
| **M14** | Cinematic Novel | 속도감 + 3막 15비트 + 소설의 무기 |

### 그 외 주요 룰

- **복합 장르 운용 원리** (v3.10) — 주 장르 전 구간 우위, 보조 장르 집중 배치, 클라이맥스 구간 보조 차단
- **GENRE_RULES 12종** (v3.9) — 미스터리·무협 추가. 환생·회귀·학원 등은 소재로 분리

---

## 12 Unit ↔ 3막 15비트 매핑

12 Unit은 3막 구조를 쪼갠 것이다. 각 Unit은 자기 구조 좌표를 알고 집필된다.

| Unit | 막 | 담당 비트 |
|------|-----|----------|
| 01 | 1막 | 오프닝 이미지 + 설정 + 촉발 사건 |
| 02 | 1막 | 망설임 |
| 03 | 1막→2막 | 1막 전환점 |
| 04 | 2막 전반 | 서브플롯 진입 + 놀이와 약속 |
| 05 | 2막 전반 | 놀이와 약속 심화 |
| 06 | 2막 전반→후반 | **미드포인트** (깨달음이 아니라 외적 사건) |
| 07 | 2막 후반 | 적대의 압박 |
| 08 | 2막 후반 | 모든 것을 잃음 |
| 09 | 2막 후반→3막 | 영혼의 어두운 밤 (심리 서술의 정점) |
| 10 | 3막 | 3막 전환점 |
| 11 | 3막 | 피날레 — 클라이맥스 |
| 12 | 3막 | 최종 이미지 + 회수 |

---

## 문체 임계치

### BJND 임계치 (Unit당)

| 지표 | 임계치 | 비고 |
|------|--------|------|
| "있었다" | 10회 | 초과 시 자동 재생성 |
| "것이었다" | 2회 | 해설체 차단 |
| 대사 태그 | 12회 | — |
| 현재형 종결 | 3회 | 치명적 |

### M13 문단·대사 지표 (작가 완성 원고 실측 기반)

| 지표 | 목표 | 근거 (작가 원고) |
|------|------|-----------------|
| 평균 문단 길이 | 40~65자 | 감각구역 40자 / 시크릿퀸 62자 |
| 짧은 문단(50자 이하) 비율 | 55% 이상 | 60~78% |
| 대사 독립 문단 비율 | 45% 이상 | 47~55% |
| 대사 밀도 | 만자당 78개 이상 | 78~141개 |
| 감각 묘사 | 만자당 25회 이하 | 17~21회 |

한 문단이 200자를 넘으면 쪼갠다. 200자 이상 문단이 연속 2개를 넘지 않는다.

---

## 프로젝트 저장 / 불러오기

STEP 0 위 접이식 패널에서 작업 상태 전체를 JSON 한 파일로 저장·복원한다.

- 저장 대상 42개 항목 — STEP 1 자료, 문체 분석, 기승전결 보강, Unit 설계, Unit 원고, Chapter 1 Stage A/B/C, 12 Unit 매핑
- 파일명 자동 생성 — `작품명_novelengine_YYYYMMDD_HHMM.json`
- Creator/Idea JSON을 잘못 올리면 거부하고 STEP 0 해당 탭으로 안내
- 구버전 저장 파일은 있는 키만 부분 복원

**Unit 원고를 생성한 뒤에는 저장을 권한다.** 재생성 비용이 크다.

---

## 사용 시나리오

### A — Creator Engine 기획 → 소설
1. STEP 0 · Creator Engine JSON 탭에 백업 JSON 업로드
2. 소설화 변환 실행 (영상 언어를 소설 언어로 번역)
3. STEP 1 필드 검토·수정
4. STEP 2~7 진행

### B — Idea Engine 씨앗 → 소설
1. STEP 0 · Idea Engine JSON 탭에 업로드
2. 변환 실행. 미결정 항목은 `[엔진 제안 — 작가 확정 필요]` 표식으로 충전됨
3. STEP 1에서 미결정 항목 확정
4. STEP 2~7 진행

### C — 기존 시나리오 → 소설
1. STEP 0 · 기존 원고 탭에 .docx/.txt 업로드 또는 붙여넣기
2. 자동 추출 실행
3. STEP 1 검토 후 STEP 2~7 진행

### D — 백지 기획 → 소설
1. STEP 0 건너뛰기
2. STEP 1부터 수동 입력
3. STEP 2~7 진행

> STEP 0 자동 추출 결과는 항상 **초안**이다. STEP 1에서 작가가 검토·수정하는 것을 전제로 한다.

---

## 연동 엔진

| 엔진 | 역할 | 관계 |
|------|------|------|
| Idea Engine | 기획 씨앗 | → Novel Engine STEP 0 |
| Creator Engine v2.6.6 | 확정 기획 | → Novel Engine STEP 0 (Profession/Period Pack 동기화) |
| Writer Engine | 영화 시나리오 | 룰 사상 공유 (BJND 문체 · POV Discipline) |
| WebNovel Engine | 웹소설 시즌 집필 | 룰 사상 공유 |
| Wuxia Engine | 무협 전용 | 별도 |

---

## 라이선스

BLUE JEANS PICTURES 내부 도구. 비공개.

---

**Build 2026-07-24 · v3.11.0 / M14 Cinematic Novel (3-act 15-beat) + dialogue tuning**
