<!-- Top Premium Navigation Bar -->
<header class="bg-white border-b border-slate-200/80 px-6 py-4 flex items-center justify-between z-30 shadow-sm shrink-0">
  <div class="flex items-center space-x-3">
    <!-- Brand Safe Logo -->
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

  <!-- Current Location HUD -->
  <div class="hidden md:flex items-center space-x-3 bg-slate-100 rounded-full py-1.5 px-4 border border-slate-200">
    <span class="relative flex h-2 w-2">
      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
      <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
    </span>
    <span class="text-xs font-medium text-slate-600">{{ currentAddress }}</span>
  </div>
</header>

<!-- Navigation Tabs -->
<nav class="bg-white border-b border-slate-200 px-6 py-1 flex space-x-1 overflow-x-auto shrink-0 z-20 shadow-sm">
  <button @click="currentTab = 'map'" 
          :class="currentTab === 'map' ? 'border-emerald-600 text-emerald-600 font-bold bg-emerald-50/50' : 'border-transparent text-slate-500 hover:text-slate-800'"
          class="flex items-center gap-2 px-4 py-3 border-b-2 text-sm transition-all rounded-t-lg">
    🗺️ 안심 지도 & 길안내
  </button>
  <button @click="currentTab = 'chatbot'" 
          :class="currentTab === 'chatbot' ? 'border-emerald-600 text-emerald-600 font-bold bg-emerald-50/50' : 'border-transparent text-slate-500 hover:text-slate-800'"
          class="flex items-center gap-2 px-4 py-3 border-b-2 text-sm transition-all rounded-t-lg">
    💬 AI 안심 비서 (챗봇)
  </button>
  <button @click="currentTab = 'community'" 
          :class="currentTab === 'community' ? 'border-emerald-600 text-emerald-600 font-bold bg-emerald-50/50' : 'border-transparent text-slate-500 hover:text-slate-800'"
          class="flex items-center gap-2 px-4 py-3 border-b-2 text-sm transition-all rounded-t-lg">
    🏡 동네 커뮤니티
  </button>
  <button @click="currentTab = 'stats'" 
          :class="currentTab === 'stats' ? 'border-emerald-600 text-emerald-600 font-bold bg-emerald-50/50' : 'border-transparent text-slate-500 hover:text-slate-800'"
          class="flex items-center gap-2 px-4 py-3 border-b-2 text-sm transition-all rounded-t-lg">
    📊 지역 안전 통계
  </button>
</nav>

<!-- Main Content Panel -->
<main class="flex-1 overflow-hidden relative bg-slate-50">

  <!-- ================= Tab 1: Map ================= -->
  <div v-show="currentTab === 'map'" class="h-full flex flex-col md:flex-row overflow-hidden">
    <aside class="w-full md:w-96 bg-white border-r border-slate-200 flex flex-col shrink-0 overflow-y-auto">
      <div class="p-5 space-y-6">
        <div class="bg-slate-50 p-4 rounded-2xl border border-slate-150 space-y-3">
          <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider">출발지 / 목적지 설정</h3>
          <input type="text" v-model="startLocation" class="w-full bg-white border border-slate-200 rounded-lg px-3 py-1.5 text-sm" placeholder="출발지" />
          <input type="text" v-model="endLocation" class="w-full bg-white border border-slate-200 rounded-lg px-3 py-1.5 text-sm" placeholder="목적지" />
          <button @click="searchRoute" class="w-full bg-emerald-600 text-white font-bold py-2 rounded-xl text-xs">경로 분석하기</button>
        </div>
      </div>
    </aside>
    <div class="flex-1 relative overflow-hidden bg-[#f8fafc]">
       <svg class="absolute inset-0 w-full h-full" id="svgMap">
         <path v-if="routeCalculated" :d="safeRoutePathD" fill="none" stroke="#059669" stroke-width="8" stroke-linecap="round" />
       </svg>
    </div>
  </div>
  
</main>
