import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '..', '')
  return {
    envDir: '..',
    plugins: [vue(), localChatApi(env.OPENAI_API_KEY)],
  }
})

function localChatApi(apiKey) {
  return {
    name: 'local-chat-api',
    configureServer(server) {
      server.middlewares.use('/.netlify/functions/chat', async (request, response) => {
        if (request.method !== 'POST') return send(response, 405, { error: 'POST 요청만 허용됩니다.' })
        try {
          process.env.OPENAI_API_KEY = apiKey || ''
          const body = await readBody(request)
          const handler = (await import('./netlify/functions/chat.mjs')).default
          const result = await handler(new Request('http://localhost/.netlify/functions/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body }))
          send(response, result.status, await result.json())
        } catch {
          send(response, 500, { error: '로컬 챗봇 서버를 시작하지 못했습니다.' })
        }
      })
    },
  }
}

function readBody(request) {
  return new Promise((resolve, reject) => {
    let body = ''
    request.setEncoding('utf8')
    request.on('data', chunk => { body += chunk })
    request.on('end', () => resolve(body))
    request.on('error', reject)
  })
}

function send(response, status, body) {
  response.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' })
  response.end(JSON.stringify(body))
}
