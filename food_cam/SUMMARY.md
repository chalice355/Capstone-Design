# Food Story App — Flutter 파트 정리

## 프로젝트 개요

음식 이름을 검색하면 Django 백엔드가 AI(Anthropic)와 Wikipedia를 활용해
**유래 / 술 / 이야기 / 노래 / 미디어** 5가지 탭으로 정보를 제공하고,
그 내용을 **음식 일기**로 저장·관리할 수 있는 앱입니다.

---

## 화면 구조 및 흐름

```mermaid
stateDiagram-v2
    [*] --> HomeScreen : 앱 시작

    HomeScreen --> StoryScreen : 검색하기
    HomeScreen --> DiaryListScreen : 일기 보기

    StoryScreen --> DiarySaveScreen : 일기 저장 (FAB)

    DiarySaveScreen --> HomeScreen : 저장 완료 → Yes
    DiarySaveScreen --> StoryScreen : 저장 완료 → No

    DiaryListScreen --> DiaryListScreen : 삭제
```

---

## 파일별 역할

```mermaid
classDiagram
    class main.dart {
        MaterialApp 진입점
        테마: 오렌지 계열 Color(0xFFE65100)
    }
    class HomeScreen {
        음식 이름 입력 TextField
        검색 → StoryScreen 이동
        일기 목록 → DiaryListScreen 이동
    }
    class StoryScreen {
        TabController (5탭)
        ApiService.getStory() 호출
        미디어 탭: ListView
        나머지 탭: ScrollView 텍스트
        FAB → DiarySaveScreen 이동
    }
    class DiarySaveScreen {
        날짜 자동 입력 (오늘)
        음식명 읽기 전용
        장소 직접 입력
        ApiService.saveDiary() 호출
    }
    class DiaryListScreen {
        ApiService.getDiaries() 호출
        ExpansionTile 카드 목록
        삭제: ApiService.deleteDiary()
    }
    class Diary {
        id: int
        foodName: String
        place: String
        date: String
        tabsJson: Map
        fromJson() factory
    }
    class ApiService {
        getStory(foodName) GET
        getDiaries() GET
        saveDiary(...) POST
        deleteDiary(id) DELETE
    }
    class config.dart {
        kBaseUrl = localhost:8000
    }

    HomeScreen --> StoryScreen
    HomeScreen --> DiaryListScreen
    StoryScreen --> DiarySaveScreen
    StoryScreen --> ApiService
    DiarySaveScreen --> ApiService
    DiaryListScreen --> ApiService
    DiaryListScreen --> Diary
    ApiService --> config.dart
```

---

## API 통신 구조

```mermaid
sequenceDiagram
    participant U as 사용자
    participant Flutter as Flutter App
    participant Django as Django Server :8000

    U->>Flutter: 음식 이름 입력 후 검색
    Flutter->>Django: GET /story/{food_name}/
    Django-->>Flutter: { food_name, tabs: {유래, 술, 이야기, 노래, 미디어} }
    Flutter-->>U: 5탭으로 내용 표시

    U->>Flutter: 일기 저장 (장소 입력)
    Flutter->>Django: POST /diary/
    Django-->>Flutter: { id: 201 }
    Flutter-->>U: 저장 완료 다이얼로그

    U->>Flutter: 일기 목록 열기
    Flutter->>Django: GET /diary/
    Django-->>Flutter: [ Diary 배열 ]
    Flutter-->>U: 카드 목록 표시

    U->>Flutter: 일기 삭제
    Flutter->>Django: DELETE /diary/{id}/
    Django-->>Flutter: { ok: true }
    Flutter-->>U: 목록 새로고침
```

---

## 주요 기술 스택

| 항목 | 내용 |
|---|---|
| Framework | Flutter 3.41.9 / Dart 3.11.5 |
| 상태 관리 | StatefulWidget (별도 패키지 없음) |
| HTTP 통신 | `http: ^1.1.0` |
| UI 스타일 | Material 3, 오렌지 컬러 테마 |
| 백엔드 연결 | `config.dart`의 `kBaseUrl`로 중앙 관리 |
| 데이터 모델 | `Diary` (id, foodName, place, date, tabsJson) |
