<!-- Top Premium Navigation Bar -->
<header class="bg-white border-b border-slate-200/80 px-6 py-4 flex items-center justify-between z-30 shadow-sm shrink-0">
  <div class="flex items-center space-x-3">
    <div class="bg-emerald-600 text-white p-2 rounded-xl flex items-center justify-center shadow-md shadow-emerald-600/10">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="w-6 h-6">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.57-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z" />
      </svg>
    </div>
    <div>
      <h1 class="font-bold text-xl leading-tight text-slate-900 tracking-tight flex items-center gap-2">
        SafeWalk Nav
        <span class="bg-emerald-50 text-emerald-700 text-xs font-semibold px-2.5 py-0.5 rounded-full border border-emerald-200">안심 귀가</span>
      </h1>
      <p class="text-xs text-slate-500">CCTV 및 경찰 시설 밀집 분석 기반 길안내 서비스</p>
    </div>
  </div>
</header>

<!-- Navigation Tabs -->
<nav class="bg-white border-b border-slate-200 px-6 py-1 flex space-x-1 shrink-0 z-20 shadow-sm">
  <button @click="currentTab = 'map'" :class="currentTab === 'map' ? 'border-emerald-600 text-emerald-600 font-bold bg-emerald-50/50' : 'border-transparent text-slate-500'" class="px-4 py-3 border-b-2 text-sm transition-all rounded-t-lg">🗺️ 안심 지도</button>
  <button @click="currentTab = 'chatbot'" :class="currentTab === 'chatbot' ? 'border-emerald-600 text-emerald-600 font-bold bg-emerald-50/50' : 'border-transparent text-slate-500'" class="px-4 py-3 border-b-2 text-sm transition-all rounded-t-lg">💬 AI 안심 비서</button>
  <button @click="currentTab = 'community'" :class="currentTab === 'community' ? 'border-emerald-600 text-emerald-600 font-bold bg-emerald-50/50' : 'border-transparent text-slate-500'" class="px-4 py-3 border-b-2 text-sm transition-all rounded-t-lg">🏡 동네 커뮤니티</button>
  <button @click="currentTab = 'stats'" :class="currentTab === 'stats' ? 'border-emerald-600 text-emerald-600 font-bold bg-emerald-50/50' : 'border-transparent text-slate-500'" class="px-4 py-3 border-b-2 text-sm transition-all rounded-t-lg">📊 안전 통계</button>
</nav>

<!-- Main Content Panel -->
<main class="flex-1 overflow-y-auto bg-slate-50 p-6">
  <div v-show="currentTab === 'map'" class="text-center py-20">
    <h2 class="text-2xl font-bold text-slate-800">지도 서비스 준비 완료</h2>
    <p class="text-slate-500 mt-2">이곳에 지도 컴포넌트와 경로 분석 UI가 렌더링됩니다.</p>
  </div>
  <div v-show="currentTab !== 'map'" class="text-center py-20 text-slate-400">
    준비 중인 페이지입니다.
  </div>
</main>