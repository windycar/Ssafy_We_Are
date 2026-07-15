# safe_nav Netlify 배포 가이드

## 핵심 원칙

OpenAI 키는 절대 `VITE_OPENAI_API_KEY`로 등록하지 않습니다. `VITE_`로 시작하는 변수는 Vite가 브라우저 JavaScript에 포함하므로 사용자가 확인할 수 있습니다.

챗봇은 `Vue 정리/netlify/functions/chat.mjs` 서버 함수에서 OpenAI를 호출합니다. OpenAI 키는 Netlify 서버 환경 변수 `OPENAI_API_KEY`에만 등록합니다.

## 1. 배포 전 확인

다음 파일은 Git에 올리지 않습니다.

- `.env`
- `node_modules/`
- `dist/`

현재 `.gitignore`에 모두 등록되어 있습니다. `.env`에 실제 키를 적었다면 `git status`에 나타나지 않는지 확인합니다.

```bash
git status --short
```

OpenAI 키가 커밋, GitHub, 화면 공유, 채팅 등에 한 번이라도 노출됐다면 해당 키를 폐기하고 새 키를 발급합니다.

## 2. 로컬 실행

프로젝트 루트의 `.env`에 서버용 키를 설정합니다. 실제 키는 공유하거나 커밋하지 않습니다.

```env
OPENAI_API_KEY=여기에_실제_OpenAI_키
VITE_KAKAO_MAP_APP_KEY=카카오_JavaScript_키
VITE_KAKAO_REST_API_KEY=카카오_REST_키
VITE_TMAP_APP_KEY=TMAP_키
```

```bash
cd "Vue 정리"
npm install
npm run dev
```

`npm run dev`는 Vite 개발 서버에서 챗봇 함수를 연결합니다. 키가 없거나 OpenAI 호출에 실패해도 챗봇은 기사 데이터 기반의 기본 안전 안내를 답변합니다.

## 3. 빌드 확인

```bash
cd "Vue 정리"
npm run build
```

빌드 과정에서 공공안전 데이터와 광주 범죄 기사 300건이 `public/data`에 반영됩니다.

## 4. Netlify 사이트 연결

1. Netlify에서 **Add new site → Import an existing project**를 선택합니다.
2. GitHub 저장소를 연결합니다.
3. 저장소 루트를 선택한 상태에서 배포합니다. `netlify.toml`이 아래 설정을 자동 적용합니다.
   - Base directory: `Vue 정리`
   - Build command: `npm run build`
   - Publish directory: `dist`
   - Functions directory: `netlify/functions`

## 5. Netlify 환경 변수 등록

Netlify 사이트의 **Project configuration → Environment variables**에서 다음 변수를 등록합니다.

| 변수 | 등록 위치 | 브라우저 노출 |
| --- | --- | --- |
| `OPENAI_API_KEY` | Netlify 환경 변수만 | 노출되지 않음 |
| `VITE_KAKAO_MAP_APP_KEY` | Netlify 환경 변수 | 브라우저에 포함됨 |
| `VITE_KAKAO_REST_API_KEY` | Netlify 환경 변수 | 브라우저에 포함됨 |
| `VITE_TMAP_APP_KEY` | Netlify 환경 변수 | 브라우저에 포함됨 |

`OPENAI_API_KEY`는 Production, Deploy Preview에 필요한 범위로 등록합니다. `VITE_OPENAI_API_KEY`는 등록하거나 사용하지 마세요.

카카오·TMAP 키는 지도 기능상 브라우저에 전달될 수 있으므로 각 서비스 콘솔에서 반드시 Netlify 배포 도메인으로 허용 도메인 제한을 설정합니다. OpenAI 키에는 도메인 제한이 아니라 서버 보관, 사용량 한도·알림, 필요 시 프로젝트별 키 분리가 필요합니다.

## 6. 배포 후 확인

1. 새 배포를 실행합니다.
2. 사이트의 챗봇에 안전 질문을 입력합니다.
3. 브라우저 개발자 도구의 Network에서 `/.netlify/functions/chat` 요청이 200인지 확인합니다.
4. 응답에 OpenAI 키, `Authorization` 헤더, 환경 변수 값이 포함되지 않는지 확인합니다.

챗봇 대화는 브라우저 저장소에 저장하지 않으며, 챗봇을 닫으면 현재 대화도 삭제됩니다.
