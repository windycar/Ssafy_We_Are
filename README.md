# 🚨 LocalHub - 위치 기반 치안·안전 커뮤니티 플랫폼

> **공공데이터와 실시간 지도를 결합한 지역 사회 안전망 및 범죄 예방 AI 챗봇 커뮤니티 서비스**
>
> 본 프로젝트는 Vue.js 3 (Vite) 기반의 프론트엔드 단일 구조(SPA)로 개발되었으며, 별도의 백엔드 서버 없이 브라우저의 `localStorage`와 다양한 외부 API(Kakao Map, TMAP, OpenAI)를 연동하여 안전 정보를 제공하는 정적 웹 애플리케이션입니다.

---

## 📌 프로젝트 개요
- **개발 기간:** 2026년 7월 (납기: 2026.07.16)
- **개발 환경:** Vue.js 3 (Vite), VSCode Copilot
- **배포 환경:** Netlify (정적 웹 호스팅)
- **주요 목적:** 전국 5개 권역(서울, 대전/충청, 구미/경북, 광주/전라, 부산)의 공공데이터와 치안 시설 데이터를 기반으로 사용자의 안전한 보행을 지원하고, 실시간 지역 안전 정보를 익명으로 공유하는 플랫폼 구축.

---

## ✨ 핵심 기능 (Key Features)

### 1. 📍 내 위치 기반 안전 지도 (Safety Map)
- **카카오 지도 API** 연동을 통해 사용자의 현재 위치를 실시간으로 파악합니다.
- 주변의 **CCTV 위치** 및 가장 가까운 **경찰서/지구대/치안센터**의 위치를 지도 위에 즉각적으로 시각화(마커 렌더링)합니다.

### 2. 🌡️ 동네 안전도 히트맵 (Safety Heatmap)
- 지자체 공공데이터의 CCTV 밀집도 및 경찰관서 분포 데이터를 기반으로 화면에 가상의 **안전도 히트맵(온도 분포)**을 시각화합니다.
- 이를 통해 사용자는 직관적으로 어느 지역이 방범 시설이 잘 갖춰진 안전 구역인지 한눈에 파악할 수 있습니다.

### 3. 🗺️ '최단 시간' vs '최고 안전' 경로 듀얼 비교 (Safe Routing)
- **TMAP 보행자 경로 탐색 API**를 기반으로 출발지부터 목적지까지의 도보 경로를 안내합니다.
- 단순 빠른 길(**최단 시간**)과 CCTV가 조밀하고 경찰서 주변(절대 안전 구역)을 경유하여 가중치가 부여된 안심 길(**최고 안전**)을 듀얼 경로로 매핑하여 비교 제공합니다.

### 4. 🚨 CCTV 사각지대 진입 알림 (Blind-Spot Alert)
- 사용자가 이동하는 도중 CCTV 분포도가 극히 낮거나 치안 시설이 없는 **방범 사각지대 및 범죄 취약 구역**에 진입할 경우, 화면 상에 경고 모달 또는 토스트(Toast) 알림을 즉각적으로 발생시킵니다.

### 5. 💬 범죄 예방 특화 AI 챗봇 (Safety Assistant)
- **OpenAI API(호출 모델: gpt-5-mini)**를 프론트엔드에서 직접 호출하는 방식으로 동작합니다.
- **치안 특화 안내:** 사용자의 질문에 맞춰 근처 호신용품 판매점 위치, 긴급 대피가 가능한 24시간 안전 구역(편의점 등), 최신 지역 치안 관련 기사 및 행동 요령을 대화형으로 안내합니다.
- **반응형 UI:** 모바일 화면에서도 100% 최적화된 우측 하단 플로팅 대화창 UI를 지원하며, 세션 내 대화 히스토리를 유지합니다.

### 6. ✍️ 지역 안전 익명 커뮤니티 (CRUD)
- 별도의 회원가입 및 로그인 없이 자유롭게 동네의 안전 정보(예: 가로등 고장 제보, 우범지역 공유)를 나누는 **익명 게시판**입니다.
- **localStorage 활용:** 작성된 게시물은 브라우저 로컬 저장소에 저장되며, 작성 시 설정한 **수정용 비밀번호**를 통해 프론트엔드 자체 로직으로만 권한을 검증(수정/삭제)합니다.

---

## 🛠️ 기술 스택 (Tech Stack)

| 구분 | 기술 / 라이브러리 |
| :--- | :--- |
| **Framework** | Vue.js 3 (Composition API, Vite) |
| **State / Routing** | Pinia, Vue Router |
| **Style** | Tailwind CSS / Bootstrap |
| **Map API** | Kakao Maps SDK, Kakao Local REST API |
| **Route API** | TMAP Route API (Pedestrian) |
| **AI API** | OpenAI API (Model: `gpt-5-mini`) |
| **Storage** | Browser LocalStorage |
| **Deployment** | Netlify |

---

## 🔑 환경 변수 설정 (.env)
프로젝트 루트 경로에 `.env` 파일을 생성하고 아래와 같이 발급받은 API 키를 설정합니다.  
*(※ Vite 환경 상 빌드 결과물에 키가 포함되므로, 배포 시 반드시 API 플랫폼에서 도메인 제한 및 결제 한도 제한 설정을 적용하십시오.)*

```env
# 1. 카카오맵 자바스크립트 앱 키 (지도 렌더링용)
VITE_KAKAO_MAP_APP_KEY=your_kakao_javascript_app_key

# 2. 카카오 로컬 REST API 키 (장소 검색 및 주소/좌표 변환용)
VITE_KAKAO_REST_API_KEY=your_kakao_rest_api_key

# 3. TMAP API 키 (보행자 경로 탐색 및 지도 선 그리기용)
VITE_TMAP_APP_KEY=your_tmap_api_key

# 4. OpenAI API 키 (gpt-5-mini 기반 치안 챗봇 연동용)
VITE_OPENAI_API_KEY=your_openai_api_key