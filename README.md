# 🚨 LocalHub - 위치 기반 치안·안전 커뮤니티 플랫폼

> 공공데이터와 지도를 결합해, 안전한 보행 경로와 지역 안전 정보를 한 번에 확인할 수 있는 정적 웹 앱입니다.

이 저장소는 Vue 3 + Vite로 만든 프론트엔드 프로젝트이며, 별도의 백엔드 없이 브라우저의 localStorage와 외부 API를 이용해 동작합니다.

---

## 📁 프로젝트 폴더 구조

```text
AI_온보딩_[팀_프로젝트]/
├─ README.md
├─ DEPLOYMENT.md
├─ netlify.toml
├─ 프롬포트.md
├─ SafeWalk_기능명세서_최종.md
├─ 데이터들/
│  ├─ CCTV정보.csv
│  ├─ 경찰청_전국 지구대 파출소 주소 현황_20251231.csv
│  └─ 광주_정제데이터/
│     ├─ cctv_gwangju.json
│     ├─ police_gwangju.json
│     ├─ csv_to_gwangju_json.py
│  └─ ...
└─ Vue 정리/
   ├─ index.html
   ├─ package.json
   ├─ vite.config.js
   ├─ start.bat
   ├─ public/
   │  └─ data/
   │     ├─ cctv_gwangju.clean.json
   │     ├─ police_gwangju.clean.json
   │     ├─ police_gwangju.coordinates.json
   │     ├─ safety-knowledge.json
   │     └─ gwangju-data-summary.json
   ├─ scripts/
   │  ├─ geocode-police.mjs
   │  └─ prepare-data.mjs
   └─ src/
      ├─ App.vue
      ├─ main.js
      ├─ assets/
      ├─ components/
      │  └─ SafetyChatbot.vue
      ├─ router/
      │  └─ index.js
      ├─ utils/
      │  ├─ communityStorage.js
      │  ├─ kakaoMap.js
      │  └─ safetyRouting.js
      └─ views/
         ├─ CommunityList.vue
         ├─ Home.vue
         ├─ Map.vue
         ├─ PostDetail.vue
         └─ PostEditor.vue
```

---

## ✨ 주요 기능

- CCTV, 경찰시설, 안전 지도 시각화
- 출발지/도착지 기준 도보 경로 탐색
- CCTV 우선 안전경로 추천
- 사각지대 경고 표시
- 지역 안전 커뮤니티 게시판
- AI 기반 안전 챗봇

---

## 🛠 실행 방법

### 1) 의존성 설치
```bash
cd "Vue 정리"
npm install
```

### 2) 환경 변수 설정
프로젝트 루트에 `.env` 파일을 생성하세요.

```env
VITE_KAKAO_MAP_APP_KEY=your_kakao_javascript_app_key
VITE_KAKAO_REST_API_KEY=your_kakao_rest_api_key
VITE_TMAP_APP_KEY=your_tmap_api_key
VITE_OPENAI_API_KEY=your_openai_api_key
```

### 3) 로컬 실행
```bash
cd "Vue 정리"
npm run dev
```

### 4) 빌드 확인
```bash
cd "Vue 정리"
npm run build
```

---

## 🌐 Netlify 배포 방법

이 프로젝트는 정적 웹 앱이므로 Netlify에 바로 배포할 수 있습니다.

### 권장 배포 설정
- Base directory: `Vue 정리`
- Build command: `npm install && npm run build`
- Publish directory: `dist`

### 환경 변수
Netlify 대시보드의 Site settings → Environment variables에 아래 값을 등록하세요.

```text
VITE_KAKAO_MAP_APP_KEY
VITE_KAKAO_REST_API_KEY
VITE_TMAP_APP_KEY
VITE_OPENAI_API_KEY
```

### 배포 파일
- [netlify.toml](netlify.toml) 에 배포 설정이 포함되어 있습니다.
- 자세한 내용은 [DEPLOYMENT.md](DEPLOYMENT.md) 를 참고하세요.

---

## ⚠️ 참고 사항

- 이 프로젝트는 백엔드 서버 없이 동작합니다.
- 커뮤니티 글과 챗봇 대화는 브라우저의 localStorage에 저장됩니다.
- 지도/경로/AI 기능은 외부 API 키가 있어야 정상 동작합니다.
- API 키는 배포 시 도메인 제한과 사용량 제한을 권장합니다.
