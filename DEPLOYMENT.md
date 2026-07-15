# Netlify 배포 가이드

## 1. 사전 준비
- Node.js 18 이상 설치
- Netlify 계정 생성
- 카카오맵 API 키, TMAP API 키, OpenAI API 키 준비

## 2. 로컬 실행
```bash
cd "Vue 정리"
npm install
npm run dev
```

## 3. 빌드 확인
```bash
cd "Vue 정리"
npm run build
```

## 4. Netlify 배포
1. Netlify 대시보드에서 New site from Git 클릭
2. 이 저장소를 연결
3. 빌드 설정
   - Base directory: `Vue 정리`
   - Build command: `npm install && npm run build`
   - Publish directory: `dist`
4. 환경 변수 추가
   - `VITE_KAKAO_MAP_APP_KEY`
   - `VITE_KAKAO_REST_API_KEY`
   - `VITE_TMAP_APP_KEY`
   - `VITE_OPENAI_API_KEY`
5. Deploy site 클릭

## 5. 주의사항
- Vite 환경 변수는 빌드 시점에 반영됩니다.
- API 키는 반드시 도메인 제한과 사용량 제한을 설정하세요.
- 정적 웹 호스팅이므로 백엔드 서버는 없습니다.
- 커뮤니티 글과 챗봇 기록은 브라우저 localStorage에 저장됩니다.
