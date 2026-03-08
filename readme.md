# BLUE JEANS NOVEL ENGINE

기획서를 입력하면 프로그램이 통합 분석, 부족한 점 진단, 전체 줄거리 보강, 12 Unit 설계, Unit별 초안 생성을 순차적으로 수행하는 개인용 소설 집필 엔진입니다.

## 파일 구성

```text
blue_jeans_novel_engine/
├── main.py
├── prompt.py
├── requirements.txt
├── README.md
├── NOVEL_ENGINE_MANUAL.md
└── .streamlit/
    └── config.toml
```

## 핵심 특징

- 기획서 조각 입력만 받는 심플 UI
- 사용자는 버튼 클릭 중심으로 진행
- 장편소설 기준 12 Unit 구조 설계
- 부족한 요소 자동 진단
- 전체 줄거리 보강
- Unit별 초안 생성 및 리라이트
- TXT / DOCX 저장

## 설치

```bash
pip install -r requirements.txt
```

## 실행

```bash
streamlit run main.py
```

## 환경변수 또는 Secrets

Anthropic API 키 필요:

```bash
ANTHROPIC_API_KEY=your_key
```

Streamlit Cloud에서는 Secrets에 아래처럼 넣으면 됩니다.

```toml
ANTHROPIC_API_KEY = "your_key"
```

## 권장 사용 순서

1. 작품 제목 / 장르 / 문체 입력
2. 기획서 조각 1~4 입력
3. `기획서 분석`
4. `부족한 점 진단`
5. `전체 줄거리 보강`
6. `12 Unit 생성`
7. Unit 번호를 선택하고 `선택 Unit 쓰기`
8. 필요하면 `선택 Unit 다시 쓰기`
9. TXT / DOCX 저장

## 메모

- 이 버전은 UI를 단순하게 유지한 MVP입니다.
- 세부 옵션을 최소화하고, 프로그램이 분석과 대안 제시를 맡도록 설계했습니다.
- 이후 버전에서 Continuity Bible, 인물 상태 추적, 복선/회수 관리 기능을 확장할 수 있습니다.
