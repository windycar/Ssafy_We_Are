<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { ensureSeedPosts } from '../utils/communityStorage'
const stats = ref(null), recent = ref([]), error = ref('')
onMounted(async () => {
  recent.value = (await ensureSeedPosts()).sort((a,b) => new Date(b.createdAt)-new Date(a.createdAt)).slice(0,3)
  try { const r = await fetch('/data/gwangju-data-summary.json'); if(!r.ok) throw new Error(); stats.value = await r.json() } catch { error.value = '안전 통계를 불러오지 못했습니다.' }
})
const date = value => new Intl.DateTimeFormat('ko-KR',{dateStyle:'medium'}).format(new Date(value))
</script>
<template>
  <main>
    <section class="hero">
      <div class="hero-inner"><p class="eyebrow">광주 시민을 위한 생활 안전 플랫폼</p><h1>우리 동네 안전을<br><em>함께 확인하고 나눠요.</em></h1><p>CCTV 공공데이터와 지역 주민의 제보를 한곳에서 확인하세요.</p><div class="actions"><RouterLink class="btn" to="/map">안전지도 보기 →</RouterLink><RouterLink class="btn secondary" to="/community">커뮤니티 참여</RouterLink></div></div>
    </section>
    <section class="page home-content">
      <div class="stats card" v-if="stats"><article><strong>{{ stats.cctvTotal.toLocaleString() }}</strong><span>광주 CCTV 총 대수</span></article><article><strong>{{ stats.cctvMarkers.toLocaleString() }}</strong><span>CCTV 지도 지점</span></article><article><strong>{{ stats.policeTotal.toLocaleString() }}</strong><span>경찰 시설</span></article></div>
      <div v-else-if="error" class="error-box">{{ error }}</div><div v-else class="empty">통계를 불러오는 중입니다…</div>
      <div class="section-head"><div><p class="eyebrow">LOCAL NEWS</p><h2>최신 동네 소식</h2></div><RouterLink to="/community">전체 보기 →</RouterLink></div>
      <div v-if="recent.length" class="post-grid"><RouterLink v-for="post in recent" :key="post.id" class="post-card card" :to="`/community/${post.id}`"><span class="tag">{{ post.category }}</span><h3>{{ post.title }}</h3><p>{{ post.content }}</p><small>{{ date(post.createdAt) }} · 조회 {{ post.viewCount || 0 }}</small></RouterLink></div>
      <div v-else class="empty">아직 게시글이 없습니다. 첫 동네 소식을 남겨보세요.</div>
    </section>
  </main>
</template>
<style scoped>
.hero{background:radial-gradient(circle at 78% 30%,#42b88b44,transparent 25%),linear-gradient(135deg,#eff8f4,#dbeee5);border-bottom:1px solid #cfe3d9}.hero-inner{width:min(1200px,calc(100% - 32px));margin:auto;padding:88px 0 95px}.eyebrow{color:var(--green);font-size:.76rem;font-weight:900;letter-spacing:.14em;text-transform:uppercase}.hero h1{font-size:clamp(2.4rem,6vw,4.5rem);line-height:1.09;letter-spacing:-.05em;margin:12px 0 20px}.hero h1 em{font-style:normal;color:var(--green)}.hero p:not(.eyebrow){color:#4c6960;font-size:1.05rem}.actions{display:flex;gap:10px;margin-top:30px}.home-content{padding-top:0}.stats{display:grid;grid-template-columns:repeat(3,1fr);transform:translateY(-36px);overflow:hidden}.stats article{padding:25px 30px;border-right:1px solid var(--line)}.stats article:last-child{border:0}.stats strong,.stats span{display:block}.stats strong{font-size:2rem;color:var(--green)}.stats span{font-size:.85rem;color:var(--muted)}.section-head{display:flex;align-items:end;justify-content:space-between;margin:18px 0}.section-head h2{margin:3px 0;font-size:1.7rem}.section-head a{color:var(--green);font-weight:800;text-decoration:none}.post-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.post-card{display:block;padding:22px;text-decoration:none;color:inherit}.post-card h3{margin:14px 0 6px}.post-card p{height:48px;overflow:hidden;color:var(--muted);font-size:.9rem}.post-card small{color:#84938e}@media(max-width:700px){.hero-inner{padding:58px 0 78px}.stats{grid-template-columns:1fr;transform:translateY(-24px)}.stats article{border-right:0;border-bottom:1px solid var(--line);padding:16px 20px}.post-grid{grid-template-columns:1fr}.actions{flex-wrap:wrap}}
</style>
