const MAX_HISTORY = 12

export default async (request) => {
  if (request.method !== 'POST') return json({ error: 'POST 요청만 허용됩니다.' }, 405)

  let question = ''
  let context = {}
  try {
    const body = await request.json()
    question = body.question
    context = body.context || {}
    const history = body.history || []
    if (typeof question !== 'string' || !question.trim()) return json({ error: '질문을 입력하세요.' }, 400)
    if (!process.env.OPENAI_API_KEY) return json({ answer: fallbackAnswer(question, context) })
    const messages = [{ role: 'system', content: systemPrompt(context) }, ...history.slice(-MAX_HISTORY).filter(message => ['user', 'assistant'].includes(message?.role) && typeof message.content === 'string').map(({ role, content }) => ({ role, content }))]
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: { Authorization: `Bearer ${process.env.OPENAI_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: 'gpt-5-mini', messages, max_completion_tokens: 500 }),
    })
    const data = await response.json().catch(() => null)
    if (!response.ok) return json({ answer: fallbackAnswer(question, context) })
    const answer = data?.choices?.[0]?.message?.content?.trim()
    return json({ answer: answer || fallbackAnswer(question, context) })
  } catch (error) {
    console.error('chat function error', error)
    return json({ answer: fallbackAnswer(question || '입력한 질문', context) })
  }
}

function systemPrompt(context) {
  return `너는 LocalHub의 광주 지역 생활안전 AI다. 범죄·사고 예방, 안전귀가, 신고 절차, 제공된 광주 범죄 기사 설명을 돕는다.
규칙: 제공된 데이터에 없는 기사 사실·통계·장소는 만들지 않는다. 기사 설명 시 제목, 날짜, 지역·범죄 유형을 구분하고 단정적 위험 예측을 하지 않는다. 예방 조치는 실행 가능한 3~5개로 제시한다. 현재 위협·범죄·실종은 112, 화재·구조·응급환자는 119 신고를 가장 먼저 안내한다. CCTV는 안전 보장이 아니며 커뮤니티 글은 공식 확인 정보가 아니다. 답변은 공감은 짧게, 한국어로 간결하게 작성한다.

안전 지식: ${JSON.stringify(context.knowledge || {})}
안전 통계: ${JSON.stringify(context.summary || {})}
범죄 기사 집계: ${JSON.stringify(context.newsSummary || {})}
질문과 관련해 선별된 기사(최대 4건): ${JSON.stringify(context.articles || [])}
경찰 시설: ${JSON.stringify(context.police || [])}
최근 주민 게시글: ${JSON.stringify(context.posts || [])}`
}

function fallbackAnswer(question, context) {
  const articles = Array.isArray(context.articles) ? context.articles : []
  if (!articles.length) {
    return `“${question}”에 직접 일치하는 제공 기사 데이터는 현재 없습니다. 이는 해당 사건이 없다는 뜻은 아닙니다. 장소·구·동 또는 범죄 유형을 바꿔 다시 검색해 보세요.\n\n기본 예방 수칙\n1. 야간에는 조명이 밝고 사람이 있는 큰길을 이용하세요.\n2. 이어폰·휴대전화 사용을 줄이고 주변을 확인하세요.\n3. 불안하거나 위협을 느끼면 가까운 편의점·경찰시설로 이동하세요.\n4. 현재 위험하거나 범죄 피해가 의심되면 즉시 112에 신고하세요.`
  }
  const article = articles[0]
  const location = [article.district, article.neighborhood].filter(Boolean).join(' ') || '광주'
  return `관련 기사 데이터가 확인되었습니다.\n- ${article.title || '제목 정보 없음'}\n- 지역: ${location} / 유형: ${article.crimeType || '분류 없음'}\n- 내용: ${article.summary || '요약 정보 없음'}\n\n예방 수칙\n1. 귀가 시 밝고 사람 많은 길을 이용하세요.\n2. 위험을 느끼면 혼자 이동하지 말고 가까운 안전한 장소로 이동하세요.\n3. 긴급한 위협·범죄 상황은 즉시 112에 신고하세요.`
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json; charset=utf-8' } })
}
