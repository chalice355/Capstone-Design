# 🍱 AI 음식 사진 인식 칼로리 계산 웹앱

> EfficientNet 기반 한식 음식 인식 + 공공데이터 영양 DB + Streamlit 웹 대시보드

---

## 배경 및 필요성

기존 다이어트 카메라를 통한 음식 사진 인식률의 부족과 더불어 더욱 다양한 식품의 인식률 향상을 모색할 필요성을 느낌.
더해서, 신뢰할 수 있을만한 기관의 데이터를 활용하는 것으로 안정성과 신뢰성 향상을 목적으로 함.

### 개발 목표

1. **보완할 수 있는 기능 탑재** — AI Hub 음식 데이터셋으로 직접 파인튜닝하는 것 뿐만 아니라, 식품 인식에 도움을 줄 보완기능들을 통해 정확성을 기존보다 더욱 확보한다. (바코드 인식 및 검색 등)
2. **공신력 있는 영양 데이터** — 식약처 공공데이터(약 5만 건)를 기반으로 칼로리·탄수화물·당류·단백질·지방·포화지방·식이섬유·나트륨 8가지 영양소를 제공한다.
3. **앱과 웹을 동시에 사용** — 앱과 웹에서 모두 확인할 수 있게 하여 접근성과 편의성을 증진한다.

---

## 시스템 구조

```mermaid
graph LR
    USER[사용자] -->|음식 사진 업로드| WEB[Streamlit 웹앱]
    WEB --> AI[EfficientNet-B0\n음식 인식 모델]
    AI -->|음식명 + 신뢰도| DB[(SQLite\n영양 DB)]
    DB -->|8가지 영양소| WEB
    WEB -->|영양 정보 + 식단 기록| USER
    CSV[전국통합식품영양성분\n공공데이터 CSV] -->|최초 1회 import| DB
    AIHUB[AI Hub\n음식 데이터셋] -->|파인튜닝| AI
```

---

## 데이터 흐름

```mermaid
sequenceDiagram
    participant User as 사용자
    participant Web as Streamlit 웹앱
    participant Model as EfficientNet 모델
    participant DB as SQLite DB

    User->>Web: 음식 사진 업로드
    Web->>Model: 이미지 전처리 (224×224 리사이즈 + 정규화)
    Model->>Web: 음식명 + 신뢰도 반환

    Web->>DB: 음식명으로 영양 정보 조회
    alt 완전 일치
        DB->>Web: 영양 데이터 반환
    else 부분 일치
        DB->>Web: 유사 음식명으로 반환
    end

    Web->>User: 영양 정보 카드 + 차트 출력
    User->>Web: 식단에 추가 버튼 클릭
    Web->>Web: session_state에 기록 누적
    Web->>User: 오늘 총 칼로리 + 식단 리스트 표시
```

---

## DB 저장 과정

```mermaid
flowchart TD
    A[전국통합식품영양성분\n공공데이터 CSV 다운로드] --> B[nutrition_db.py 실행\npython data/nutrition_db.py --csv 파일명.csv]
    B --> C[pandas로 CSV 로드\ncp949 인코딩]
    C --> D[필요 컬럼 추출\n식품명 · 8가지 영양소]
    D --> E[숫자형 변환\n오류값 NaN 처리]
    E --> F[calories · food_name\nNaN 행 제거]
    F --> G[(SQLite\nfood_nutrition.db 저장\n약 5만 건)]
    G --> H[food_name 인덱스 생성\n조회 속도 최적화]
    H --> I[앱 실행 시\n로컬 DB 조회]
    I --> J{완전 일치?}
    J -->|Yes| K[해당 행 반환]
    J -->|No| L[LIKE 부분 일치 검색]
    L --> K
```

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| 한식 음식 인식 | EfficientNet-B0로 한식 100종 분류 |
| 영양 정보 조회 | 공공데이터 기반 8가지 영양소 제공 |
| 영양소 시각화 | Plotly 파이·바 차트로 영양 비율 즉시 표시 |
| 식단 기록 | 하루 섭취 음식 누적 저장 및 총 칼로리 합산 |
| 영양 균형 분석 | 일별 영양소 비율 그래프 및 권장량 대비 현황 |
| 무료 배포 | Streamlit Cloud로 서버 비용 없이 웹 서비스 운영 |

---

## 제공 영양 정보

| 항목 | CSV 컬럼명 | 단위 |
|------|-----------|------|
| 칼로리 | 에너지(kcal) | kcal |
| 탄수화물 | 탄수화물(g) | g |
| 당류 | 당류(g) | g |
| 식이섬유 | 식이섬유(g) | g |
| 단백질 | 단백질(g) | g |
| 지방 | 지방(g) | g |
| 포화지방 | 포화지방산(g) | g |
| 나트륨 | 나트륨(mg) | mg |

---

## 음식 분류 클래스 (예시 100종)

| 카테고리 | 음식 예시 |
|---------|---------|
| 밥류 | 비빔밥, 볶음밥, 김밥, 주먹밥, 쌈밥 |
| 국·찌개 | 된장찌개, 김치찌개, 순두부찌개, 미역국, 설렁탕 |
| 구이 | 삼겹살, 갈비, 불고기, 생선구이, 닭갈비 |
| 면류 | 라면, 냉면, 칼국수, 잡채, 짜장면 |
| 반찬 | 김치, 잡채, 시금치나물, 콩나물, 두부조림 |
| 분식 | 떡볶이, 순대, 튀김, 어묵, 김말이 |

---

## 기술 스택

| 파트 | 라이브러리 / 도구 | 버전 |
|------|----------------|------|
| AI 모델 | PyTorch, torchvision (EfficientNet-B0) | 2.0+ / 0.15+ |
| 이미지 처리 | Pillow, OpenCV | 최신 |
| 웹앱 | Streamlit | 1.32+ |
| 시각화 | Plotly | 5.18+ |
| 데이터 처리 | pandas | 최신 |
| DB | SQLite3 (Python 내장) | - |
| 배포 | Streamlit Cloud, GitHub | - |

---

## 폴더 구조

```
food-calorie-ai/
├── app.py                  # Streamlit 메인 앱
├── test_cli.py             # Streamlit 없이 전체 흐름 CLI 확인용
├── model/
│   ├── predict.py          # 추론 함수
│   └── class_names.json    # 학습된 음식 클래스 목록 (학습 후 생성)
├── data/
│   ├── nutrition_db.py     # CSV → SQLite import 및 조회
│   └── food_nutrition.db   # 영양 정보 DB (자동 생성)
├── requirements.txt
└── README.md
```

---

## 실행 방법

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 영양 DB 초기화 (CSV 최초 1회)
python data/nutrition_db.py --csv 전국통합식품영양성분정보표준데이터.csv

# 3. 전체 흐름 CLI 빠른 확인 (Streamlit 없이)
python test_cli.py

# 4. 웹앱 실행
streamlit run app.py
```

---

## 개발 단계

1. **Phase 1**: AI Hub 데이터셋 신청 및 다운로드, 클래스 선정, 전처리 스크립트 작성
2. **Phase 2**: EfficientNet-B0 파인튜닝, 검증 정확도 85% 이상 달성
3. **Phase 3**: 공공데이터 CSV → SQLite DB 구축 및 조회 최적화
4. **Phase 4**: Streamlit UI 개발 (업로드 → 결과 → 식단 기록 → 통계 화면)
5. **Phase 5**: 통합 테스트, 오인식 케이스 개선, Streamlit Cloud 배포

---

## 데이터셋

- **[AI Hub 음식 이미지](https://aihub.or.kr)** — 한식 150여 종, 수십만 장 (무료 신청)
- **[전국통합식품영양성분정보 공공데이터](https://www.data.go.kr/data/15100064/standard.do)** — 약 5만 건, 8가지 영양소 (무료)

---

## 기대 효과 및 차별점

| 항목 | 내용 |
|------|------|
| 한식 특화 | 기존 앱(MyFitnessPal 등)의 한식 인식 한계 극복 |
| 비용 0원 | 서버·API 비용 없이 무료 운영 가능 |
| 공식 데이터 | 공공데이터포털 공식 DB 사용으로 영양 정보 신뢰도 확보 |
| 확장 가능성 | 추후 식단 추천, 알레르기 필터, 다이어트 목표 설정으로 확장 가능 |

---

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
