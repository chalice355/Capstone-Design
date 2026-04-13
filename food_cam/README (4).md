# 🍽️ AI 음식 스토리 안드로이드 앱

> EfficientNet 기반 한식 음식 인식 + Naver 검색 + Firebase 클라우드 + Flutter 안드로이드 앱

---

## 배경 및 필요성

음식은 단순한 끼니가 아니라 역사·문화·이야기가 담긴 콘텐츠다.
그러나 기존 음식 관련 앱은 칼로리·영양 정보에만 집중되어 있어,
음식이 가진 문화적 맥락과 이야기를 즐기는 경험을 제공하지 못하고 있다.

### 개발 목적

1. **음식을 이야기로** — 사진 한 장으로 음식의 유래·문화·어울리는 술·관련 이야기·노래·미디어 등장 장면까지 탐색할 수 있는 앱을 개발한다.
2. **사진 없이도 탐색** — 랜덤 음식 탐색 기능으로 사진 촬영 없이도 매일 새로운 음식 이야기를 발견할 수 있게 한다.
3. **나만의 기록** — 음식 일기 기능으로 탐색한 음식과 이야기를 저장하고 돌아볼 수 있게 한다.

---

## 개발 진척도

| 항목 | 상태 | 비고 |
|------|------|------|
| FastAPI 서버 구축 | ✅ 완료 | 4개 엔드포인트 동작 확인 |
| Naver 검색 API 연동 | ✅ 완료 | 탭별 검색어 분리 구현 |
| Wikipedia API 연동 | ✅ 완료 | 유래 탭 기본 데이터 |
| Render 서버 배포 | ✅ 완료 | 외부 접근 가능한 URL 발급 |
| EfficientNet-B0 학습 | 🔲 진행 전 | 학습 데이터 준비 중 |
| Flutter 앱 개발 | 🔲 진행 전 | Flutter SDK 설치 필요 |
| Firebase 연동 | 🔲 진행 전 | 음식 일기 저장용 |

---

## 시스템 구조

```mermaid
graph TB
    subgraph READY["사전 준비"]
        AIHUB[AI Hub 음식 이미지]
        FOODLIST[한식 목록 JSON]
    end

    subgraph APP["Flutter 안드로이드 앱"]
        CAM[카메라 촬영]
        RAND[랜덤 탐색]
        DIARY[음식 일기]
        TABS[결과 화면\n유래 · 술 · 이야기 · 노래 · 미디어]
        SAVE[일기 저장]
    end

    subgraph SERVER["FastAPI 백엔드 (Render 배포) ✅"]
        MODEL[EfficientNet-B0\n음식 인식]
        WIKI[Wikipedia API\n유래 검색 ✅]
        NAVER[Naver 검색 API\n탭별 콘텐츠 ✅]
    end

    subgraph FIREBASE["Firebase"]
        STORE[(Firestore\n일기 텍스트)]
        STORAGE[(Storage\n음식 사진)]
    end

    AIHUB -->|파인튜닝| MODEL
    FOODLIST -->|랜덤 pick| RAND

    CAM -->|사진 전송| MODEL
    RAND -->|음식명| TABS
    DIARY -->|저장된 음식명| TABS
    MODEL -->|음식명| TABS

    TABS -->|음식명| WIKI
    WIKI -->|검색 결과| NAVER
    NAVER -->|탭별 콘텐츠| TABS

    SAVE -->|저장| STORE
    SAVE -->|저장| STORAGE
    STORE & STORAGE -->|불러오기| DIARY
```

---

## 데이터 흐름

```mermaid
sequenceDiagram
    participant App as Flutter 앱
    participant API as FastAPI 서버 (Render)
    participant Model as EfficientNet-B0
    participant Naver as Naver 검색 API
    participant Wiki as Wikipedia API
    participant FB as Firebase

    alt 사진 촬영
        App->>API: 음식 사진 전송
        API->>Model: 이미지 전처리 후 추론
        Model->>API: 음식명 + 신뢰도
    else 랜덤 탐색
        App->>API: 랜덤 음식명 요청
        API->>App: 음식 목록 중 랜덤 반환
    end

    API->>Wiki: 음식명으로 유래 검색
    Wiki->>API: 검색 결과 반환
    API->>Naver: 탭별 검색어로 정보 수집
    Naver->>API: 탭별 콘텐츠 반환
    API->>App: 전체 결과 응답

    App->>App: 탭 화면 표시 (유래·술·이야기·노래·미디어)
    App->>FB: 일기 저장 (음식명·날짜·사진·메모)
    FB->>App: 저장된 일기 목록 조회
```

---

## 앱 화면 구성

| 화면 | 설명 | 상태 |
|------|------|------|
| 촬영 화면 | 카메라로 음식 사진 촬영 또는 갤러리에서 불러오기 | 🔲 |
| 인식 결과 | 음식명 + 신뢰도 표시, 탭 화면으로 이동 | 🔲 |
| 유래 탭 | 음식의 역사·기원·지역 정보 | 🔲 |
| 술 탭 | 어울리는 주류 및 페어링 이유 | 🔲 |
| 이야기 탭 | 관련 문화·속담·흥미로운 에피소드 | 🔲 |
| 노래 탭 | 음식 분위기에 어울리는 노래 추천 | 🔲 |
| 미디어 탭 | 영화·드라마·책에 등장하는 장면 소개 | 🔲 |
| 랜덤 탐색 | 오늘의 음식 랜덤 소개, 계속 탐색 가능 | 🔲 |
| 음식 일기 | 저장된 음식 기록 날짜순 / 카테고리별 열람 | 🔲 |

---

## 주요 기능

| 기능 | 설명 | 상태 |
|------|------|------|
| 한식 음식 인식 | EfficientNet-B0로 한식 100종 분류 | 🔲 학습 데이터 준비 중 |
| 탭별 이야기 제공 | 유래·술·이야기·노래·미디어 5가지 탭 | ✅ 서버 완료 |
| Naver 검색 연동 | 탭별 검색어로 실시간 정보 수집 | ✅ 완료 |
| 랜덤 탐색 | 사진 없이 매일 새 음식 이야기 발견 | ✅ 서버 완료 |
| 음식 일기 | Firebase에 탐색 기록 저장 및 열람 | 🔲 Firebase 연동 필요 |
| 딥링크 연결 | 유튜브·검색으로 바로 이동 | 🔲 앱 개발 시 추가 |

---

## 기술 스택

| 파트 | 라이브러리 / 도구 | 역할 | 상태 |
|------|----------------|------|------|
| 모바일 앱 | Flutter (Dart) | 안드로이드 앱 UI | 🔲 |
| AI 모델 | PyTorch, EfficientNet-B0 | 한식 음식 분류 | 🔲 학습 전 |
| 백엔드 | FastAPI (Python) | 추론·검색 통합 처리 | ✅ |
| 정보 검색 | Naver 검색 API | 탭별 콘텐츠 수집 | ✅ |
| 유래 검색 | Wikipedia API | 음식 유래·역사 검색 | ✅ |
| 클라우드 DB | Firebase Firestore + Storage | 음식 일기 저장 | 🔲 |
| 학습 데이터 | 오픈셀렉트 + AI Hub 음식 이미지 | EfficientNet-B0 파인튜닝 | 🔲 준비 중 |
| 배포 | Render | FastAPI 서버 무료 배포 | ✅ |

---

## 폴더 구조

```
food-story-app/
├── flutter_app/                # Flutter 안드로이드 앱 (예정)
│   ├── lib/
│   │   ├── main.dart
│   │   ├── screens/
│   │   │   ├── camera_screen.dart
│   │   │   ├── result_screen.dart
│   │   │   ├── explore_screen.dart
│   │   │   └── diary_screen.dart
│   │   └── services/
│   │       ├── api_service.dart
│   │       └── firebase_service.dart
│   └── pubspec.yaml
├── server/                     # FastAPI 백엔드 ✅
│   ├── main.py
│   ├── model/
│   │   ├── train.py
│   │   └── predict.py
│   └── services/
│       ├── llm_service.py      # Naver 검색 API ✅
│       └── wiki_service.py     # Wikipedia API ✅
├── Procfile                    # Render 배포 설정 ✅
├── runtime.txt
├── requirements.txt
└── README.md
```

---

## 실행 방법

```bash
# 1. 서버 의존성 설치
pip install -r requirements.txt

# 2. .env 파일 생성
cp .env.example .env
# NAVER_CLIENT_ID, NAVER_CLIENT_SECRET 입력

# 3. FastAPI 서버 로컬 실행
uvicorn server.main:app --reload

# 4. Flutter 앱 실행 (개발 예정)
cd flutter_app && flutter run
```

---

## 개발 단계

1. **Phase 1**: FastAPI 서버 구축 + Naver·Wikipedia API 연동 ✅
2. **Phase 2**: Render 서버 배포 ✅
3. **Phase 3**: EfficientNet-B0 파인튜닝 (학습 데이터 준비 중) 🔲
4. **Phase 4**: Flutter 앱 개발 (촬영 → 결과 → 탭 화면) 🔲
5. **Phase 5**: 랜덤 탐색 + 음식 일기 + Firebase 연동 🔲
6. **Phase 6**: 미디어 탭 + 딥링크 연결 🔲
7. **Phase 7**: 통합 테스트 및 최종 배포 🔲

---

## 데이터셋

- **[AI Hub 한국 음식 이미지](https://aihub.or.kr)** — 한식 150여 종, 수십만 장 (신청 완료)
- **오픈셀렉트** — 100종 × 1,000장, 1024×1024 고해상도, JSON 라벨링 (다운로드 중)

---

## 기대 효과 및 차별점

| 항목 | 내용 |
|------|------|
| 콘텐츠 차별화 | 칼로리 앱과 달리 음식을 이야기·문화로 즐기는 경험 제공 |
| 사진 없이도 사용 | 랜덤 탐색으로 매일 앱을 열 이유 확보 |
| 기록 기능 | 음식 일기로 나만의 음식 스토리북 형성 |
| 미디어 연결 | 영화·드라마·책과 음식을 연결하는 독창적 콘텐츠 |
| 확장 가능성 | 나라별 음식 비교, 계절·지역 연결, SNS 카드 공유로 확장 가능 |

---

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
