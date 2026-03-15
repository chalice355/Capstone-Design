# 🍱 AI 음식 사진 인식 칼로리 계산 웹앱

> EfficientNet 기반 한식 음식 인식 + 식약처 공식 영양 DB + Streamlit 웹 대시보드

## 프로젝트 개요

음식 사진을 업로드하면 AI가 한식 종류를 자동으로 인식하고,
식약처 공식 데이터 기반으로 **칼로리·탄수화물·단백질·지방** 정보를 즉시 제공하며,
식단 기록과 영양 균형 통계를 Streamlit 웹 대시보드로 확인할 수 있는 시스템입니다.

## 시스템 구조

```mermaid
graph LR
    USER[사용자] -->|음식 사진 업로드| WEB[Streamlit 웹앱]
    WEB --> AI[EfficientNet-B0\n음식 인식 모델]
    AI -->|음식명| DB[(SQLite\n영양 DB)]
    DB -->|칼로리 / 탄·단·지| WEB
    WEB -->|영양 정보 + 식단 기록| USER
    OPEN[식약처 오픈API] -->|최초 1회 수집| DB
    AIHUB[AI Hub\n한국 음식 데이터셋] -->|파인튜닝| AI
```

## 주요 기능

| 기능 | 설명 |
|------|------|
| 한식 음식 인식 | EfficientNet-B0로 한식 100종 분류 |
| 칼로리 조회 | 식약처 공식 DB 기반 칼로리·탄수화물·단백질·지방 제공 |
| 영양소 시각화 | Plotly 파이·바 차트로 영양 비율 즉시 표시 |
| 식단 기록 | 하루 섭취 음식 누적 저장 및 총 칼로리 합산 |
| 영양 균형 분석 | 일별 탄·단·지 비율 그래프 및 권장량 대비 현황 |
| 무료 배포 | Streamlit Cloud로 서버 비용 없이 웹 서비스 운영 |

## 기술 스택

| 파트 | 기술 |
|------|------|
| AI / 모델 | Python, PyTorch, EfficientNet-B0, torchvision, Pillow |
| 웹앱 / UI | Streamlit, Plotly |
| 데이터 / DB | SQLite, pandas, 식약처 식품영양성분 오픈API |
| 학습 데이터 | AI Hub 한국 음식 이미지 데이터셋 (한식 150종+) |
| 배포 | Streamlit Cloud, GitHub |

## 팀원 및 역할

| 이름 | 역할 | 담당 |
|------|------|------|
| 팀원 A | AI / 모델 | AI Hub 데이터 전처리 + EfficientNet-B0 파인튜닝 + 정확도 개선 |
| 팀원 B | 데이터 / 백엔드 | 식약처 오픈API 연동 + SQLite DB 설계 + 칼로리 계산 로직 |
| 팀원 C | 웹앱 / 배포 | Streamlit UI 개발 + Plotly 시각화 + Streamlit Cloud 배포 |

## 폴더 구조

```
food-calorie-ai/
├── app.py                  # Streamlit 메인 앱
├── model/
│   ├── train.py            # EfficientNet-B0 파인튜닝 스크립트
│   ├── predict.py          # 추론 함수
│   └── class_names.json    # 학습된 음식 클래스 목록 (학습 후 생성)
├── data/
│   ├── nutrition_db.py     # 식약처 API 연동 및 SQLite 저장
│   └── food_nutrition.db   # 영양 정보 DB (자동 생성)
├── requirements.txt
├── project.md              # 상세 프로젝트 기획서
└── README.md
```

## 실행 방법

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 영양 DB 초기화 (식약처 API 키 필요)
python data/nutrition_db.py

# 3. 모델 학습 (AI Hub 데이터셋 준비 후)
python model/train.py

# 4. 앱 실행
streamlit run app.py
```

## 개발 단계

1. **Phase 1**: AI Hub 데이터셋 수집 및 전처리
2. **Phase 2**: EfficientNet-B0 파인튜닝 및 성능 평가
3. **Phase 3**: 식약처 오픈API 연동 및 SQLite DB 구축
4. **Phase 4**: Streamlit 웹 UI 개발 및 시각화
5. **Phase 5**: 통합 테스트 및 Streamlit Cloud 배포

## 데이터셋

- **[AI Hub 한국 음식 이미지](https://aihub.or.kr)** — 한식 150여 종, 수십만 장 (무료 신청)
- **[식약처 식품영양성분 DB 오픈API](https://www.foodsafetykorea.go.kr/api/main.do)** — 칼로리·탄·단·지 공식 데이터 (무료)

## 문서

- [상세 프로젝트 기획서 (project.md)](project.md)

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
