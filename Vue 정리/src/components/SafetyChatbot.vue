<script setup>
import { nextTick, ref } from 'vue'
import { getPosts } from '../utils/communityStorage'

const open = ref(false)
const input = ref('')
const sending = ref(false)
const error = ref('')
const listEl = ref(null)
let dataPromise

const messages = ref([])
async function fetchJson(path) { try { const response = await fetch(path); return response.ok ? response.json() : null } catch { return null } }
function words(text) { return [...new Set((text.toLowerCase().match(/[가-힣a-z0-9]{2,}/g) || []).filter(word => !['광주', '안전', '관련', '어떻게', '무엇', '기사', '뉴스'].includes(word)))] }
function pickNews(news, question) {
  const terms = words(question)
  return [...(news || [])].map(item => {
    const text = `${item.title || ''} ${item.summary || ''} ${item.crimeType || ''} ${item.district || ''} ${item.neighborhood || ''}`.toLowerCase()
    const score = terms.reduce((sum, term) => sum + (text.includes(term) ? 3 : 0), 0) + (text.includes('광주') ? 1 : 0)
    return { item, score, date: Date.parse(item.publishedAt) || 0 }
  }).sort((a, b) => b.score - a.score || b.date - a.date).slice(0, 4).map(({ item }) => ({ title: item.title, summary: item.summary, crimeType: item.crimeType, district: item.district, neighborhood: item.neighborhood, publishedAt: item.publishedAt, originalUrl: item.originalUrl }))
}
async function loadData() {
  if (!dataPromise) dataPromise = Promise.all([
    fetchJson('/data/gwangju-data-summary.json'), fetchJson('/data/police_gwangju.clean.json'), fetchJson('/data/safety-knowledge.json'), fetchJson('/data/gwangju-crime-news.json'), fetchJson('/data/gwangju-crime-news-summary.json'),
  ]).then(([summary, police, knowledge, news, newsSummary]) => ({ summary, police, knowledge, news, newsSummary }))
  return dataPromise
}
async function context(question) {
  const { summary, police, knowledge, news, newsSummary } = await loadData()
  const posts = getPosts().sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt)).slice(0, 3).map(({ title, category }) => `${title} (${category})`)
  return { knowledge, summary, newsSummary, articles: pickNews(news, question), police: (police || []).slice(0, 5).map(({ name, type, address }) => ({ name, type, address })), posts }
}
async function send() {
  const question = input.value.trim()
  if (!question || sending.value) return
  messages.value.push({ role: 'user', content: question })
  input.value = ''; error.value = ''
  await nextTick(); listEl.value?.scrollTo(0, listEl.value.scrollHeight)
  sending.value = true
  try {
    const response = await fetch('/.netlify/functions/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question, history: messages.value.slice(-12), context: await context(question) }) })
    const data = await response.json().catch(() => null)
    if (!response.ok) throw new Error(data?.error || `AI 요청에 실패했습니다. (${response.status})`)
    if (!data?.answer) throw new Error('AI 응답을 받지 못했습니다.')
    messages.value.push({ role: 'assistant', content: data.answer })
  } catch (exception) {
    console.error(exception)
    error.value = exception instanceof TypeError ? '네트워크 연결을 확인해주세요. Netlify 개발 서버 또는 배포 사이트에서 실행해야 합니다.' : exception.message
  } finally { sending.value = false; await nextTick(); listEl.value?.scrollTo(0, listEl.value.scrollHeight) }
}
function keydown(event) { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); send() } }
function close() { open.value = false; messages.value = []; error.value = '' }
function toggle() { if (open.value) close(); else open.value = true }
</script>

<template>
  <button class="floating" aria-label="안전 챗봇 열기" @click="toggle">{{ open ? '×' : '💬' }}<span v-if="!open">안전 도우미</span></button>
  <section v-if="open" class="chat card" aria-label="안전 챗봇">
    <header><div><strong>LocalHub 안전 도우미</strong><small>광주 뉴스·안전 데이터 기반 AI 안내</small></div><button @click="close">×</button></header>
    <div ref="listEl" class="messages"><div v-if="!messages.length" class="welcome"><b>무엇을 도와드릴까요?</b><p>광주 범죄·사고 기사, 예방 행동, 안전귀가 방법을 물어보세요.</p></div><div v-for="(message, index) in messages" :key="index" :class="['message', message.role]">{{ message.content }}</div><div v-if="sending" class="message assistant">관련 기사와 안전 정보를 확인하고 있습니다…</div><p v-if="error" class="chat-error">{{ error }}</p></div>
    <footer><textarea v-model="input" rows="2" placeholder="예: 북구 절도 기사와 예방법 알려줘" @keydown="keydown"></textarea><button :disabled="sending || !input.trim()" @click="send">전송</button></footer>
  </section>
</template>

<style scoped>
.floating{position:fixed;right:25px;bottom:25px;z-index:210;background:var(--green);color:#fff;border-radius:999px;min-width:56px;height:56px;padding:0 18px;font-weight:850;box-shadow:0 12px 30px #0f765755;font-size:1rem}.floating span{margin-left:7px}.chat{position:fixed;right:25px;bottom:92px;width:min(390px,calc(100vw - 30px));height:570px;z-index:200;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 20px 60px #0b2e2360}.chat header{display:flex;justify-content:space-between;align-items:center;background:#104f3d;color:#fff;padding:16px 18px}.chat header strong,.chat header small{display:block}.chat header small{font-size:.7rem;opacity:.72;margin-top:2px}.chat header button{background:transparent;color:#fff;font-size:1.4rem}.messages{flex:1;overflow:auto;padding:17px;background:#f4f8f6;display:flex;flex-direction:column;gap:10px}.welcome{text-align:center;margin:auto;color:var(--muted);padding:25px}.message{max-width:86%;padding:10px 12px;border-radius:13px;white-space:pre-wrap;font-size:.9rem;line-height:1.55}.message.user{align-self:flex-end;background:var(--green);color:#fff;border-bottom-right-radius:3px}.message.assistant{align-self:flex-start;background:#fff;border:1px solid var(--line);border-bottom-left-radius:3px}.chat-error{color:#a52f2f;font-size:.82rem;margin:0}.chat footer{display:flex;gap:8px;padding:12px;border-top:1px solid var(--line);background:#fff}.chat textarea{resize:none;flex:1;border:1px solid #bfd0c8;border-radius:10px;padding:9px}.chat footer button{background:var(--green);color:#fff;border-radius:9px;padding:0 13px;font-weight:800}.chat footer button:disabled{opacity:.4}@media(max-width:550px){.floating{right:15px;bottom:15px}.chat{inset:74px 10px 82px;width:auto;height:auto}.floating span{display:none}}
</style>
