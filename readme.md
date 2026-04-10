# 👖 BLUE JEANS NOVEL ENGINE v2.5

장편 대중소설 집필 AI 엔진 — Mr.MOON의 소설 문법

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
├── main.py          # Streamlit 앱 (1,579줄)
├── prompt.py        # 프롬프트 라이브러리 (1,291줄)
├── requirements.txt # 의존성
├── .streamlit/
│   └── config.toml  # 테마 설정
├── README.md
└── NOVEL_ENGINE.md  # 제품 설명서
```

## requirements.txt

```
streamlit>=1.30.0
anthropic>=0.18.0
python-docx>=1.0.0
lxml>=4.9.0
```

## 주요 기능

- 7단계 파이프라인 (입력 → 분석 → 보강 → 설계 → 생성 → 검토 → 내보내기)
- Chapter 1 다단계 생성 (Stage A/B/C)
- 10장르 Rule Pack × 12필드
- 상업소설 5대 기계 (Twist Map, Pacing, Cliffhanger, Betrayal, Information Layer)
- Planting & Payoff + Villain 4 Questions + Goal/Need BJND
- 품질 자동 체크 + Unit 요약 + 캐릭터 추적
- DOCX 소설 원고 포맷 내보내기

## 라이선스

BLUE JEANS PICTURES 내부 도구. 비공개.
