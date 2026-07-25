# safe_nav - 광주 안심 귀가 서비스

> CCTV·경찰시설 공공데이터와 보행 경로를 결합해 더 안전한 귀가 경로와 지역 안전 정보를 제공하는 Vue 3 웹 애플리케이션입니다.
> 🌐 **배포 사이트:** [https://jovial-phoenix-52d898.netlify.app/](https://jovial-phoenix-52d898.netlify.app/)

## 주요 기능

- 현재 위치와 주소 검색 기반 출발지·목적지 지정
- 광주 CCTV·경찰시설 지도 표시 및 레이어 전환
- CCTV 밀도 기반 치안 히트맵
- TMAP 후보 경로를 비교한 최단 경로·안전 우선 경로 제공
- CCTV·경찰시설 사각 구간 경고와 단계별 길안내
- 광주 치안 기사·안전 데이터를 활용한 OpenAI 안전 챗봇
- 닉네임과 수정·삭제 비밀번호를 사용하는 익명 커뮤니티 CRUD
- 최근 목적지, 게시글 검색, 지역 안전 통계

## 기술 구성

- Vue 3, Vue Router, Vite
- Kakao Maps JavaScript API
- TMAP 보행자 경로 API
- Netlify Functions 기반 OpenAI API 호출
- 브라우저 LocalStorage 기반 커뮤니티·최근 검색 저장

OpenAI 키는 브라우저에 포함하지 않습니다. `Vue 정리/netlify/functions/chat.mjs`에서만 `OPENAI_API_KEY`를 사용합니다.

## 프로젝트 구조

```text
AI_온보딩_[팀_프로젝트]/
├─ README.md
├─ DEPLOYMENT.md
├─ netlify.toml
├─ safe_nav_기능명세서_최종.md
├─ 04_3일차_팀프로젝트_실습기획서_템플렛.xlsx
├─ 데이터들/
└─ Vue 정리/
   ├─ index.html
   ├─ package.json
   ├─ vite.config.js
   ├─ netlify/functions/chat.mjs
   ├─ public/data/
   └─ src/
      ├─ components/SafetyChatbot.vue
      ├─ router/index.js
      ├─ utils/
      └─ views/
```

## 로컬 실행

프로젝트 루트에 `.env`를 만들고 필요한 키를 설정합니다.

```env
OPENAI_API_KEY=server_only_openai_key
VITE_KAKAO_MAP_APP_KEY=kakao_javascript_key
VITE_KAKAO_REST_API_KEY=kakao_rest_key
VITE_TMAP_APP_KEY=tmap_key
```

`OPENAI_API_KEY`에 `VITE_` 접두사를 붙이면 안 됩니다. `VITE_` 변수는 브라우저 번들에 포함됩니다.

```bash
cd "Vue 정리"
npm install
npm run dev
```

## 빌드

```bash
cd "Vue 정리"
npm run build
```

빌드 전에 `scripts/prepare-data.mjs`가 실행되어 광주 공공데이터와 치안 기사 데이터를 `public/data`에 반영합니다.

## Netlify 배포

저장소 루트를 Netlify에 연결하면 [netlify.toml](netlify.toml)이 다음 설정을 적용합니다.

- Base directory: `Vue 정리`
- Build command: `npm run build`
- Publish directory: `dist`
- Functions directory: `netlify/functions`

Netlify 환경 변수에는 `OPENAI_API_KEY`, `VITE_KAKAO_MAP_APP_KEY`, `VITE_KAKAO_REST_API_KEY`, `VITE_TMAP_APP_KEY`를 등록합니다. 상세 절차는 [DEPLOYMENT.md](DEPLOYMENT.md)를 참고하세요.

## 데이터·보안 참고

- 커뮤니티 글과 최근 목적지는 현재 브라우저의 LocalStorage에 저장됩니다.
- 수정·삭제 비밀번호도 LocalStorage에 저장되므로 데모·교육용 구조입니다.
- 지도와 경로 결과는 참고 정보이며 실제 안전을 보장하지 않습니다.
- Kakao·TMAP 키는 각 서비스 콘솔에서 허용 도메인과 사용량 제한을 설정해야 합니다.
