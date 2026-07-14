<script setup>
import { ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import SafetyChatbot from './components/SafetyChatbot.vue'

const menuOpen = ref(false)
</script>

<template>
  <div class="app-shell">
    <header class="site-header">
      <RouterLink class="brand" to="/" @click="menuOpen = false">
        <span class="brand-mark">L</span>
        <span><strong>LocalHub</strong><small>광주 안전 정보 커뮤니티</small></span>
      </RouterLink>
      <button class="menu-button" aria-label="메뉴 열기" @click="menuOpen = !menuOpen">☰</button>
      <nav :class="{ open: menuOpen }">
        <RouterLink to="/" @click="menuOpen = false">홈</RouterLink>
        <RouterLink to="/map" @click="menuOpen = false">안전지도</RouterLink>
        <RouterLink to="/community" @click="menuOpen = false">커뮤니티</RouterLink>
      </nav>
    </header>
    <RouterView />
    <SafetyChatbot />
  </div>
</template>

<style scoped>
.app-shell{min-height:100vh}.site-header{height:72px;padding:0 max(24px,calc((100vw - 1200px)/2));display:flex;align-items:center;justify-content:space-between;background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:100}.brand{display:flex;align-items:center;gap:11px;text-decoration:none;color:var(--ink)}.brand-mark{display:grid;place-items:center;width:39px;height:39px;border-radius:12px;background:var(--green);color:#fff;font-weight:900}.brand strong,.brand small{display:block}.brand strong{font-size:1.15rem}.brand small{font-size:.72rem;color:var(--muted);margin-top:2px}nav{display:flex;gap:5px}nav a{padding:10px 15px;border-radius:10px;color:#52635e;text-decoration:none;font-weight:700;font-size:.93rem}nav a.router-link-active{background:#e8f5ef;color:var(--green)}.menu-button{display:none;background:none;color:var(--ink);font-size:1.3rem;padding:8px}@media(max-width:640px){.site-header{height:64px;padding:0 16px}.menu-button{display:block}nav{display:none;position:absolute;top:63px;left:0;right:0;padding:10px 16px 16px;background:#fff;border-bottom:1px solid var(--line);box-shadow:0 12px 22px #18312c14}nav.open{display:grid}}
</style>
