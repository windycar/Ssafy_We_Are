<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { loadKakaoMap } from '../utils/kakaoMap'
import { chooseRoutes, nearestFacilities } from '../utils/safetyRouting'

const center = { lat: 35.1595, lng: 126.8526 }
const recentSearchKey = 'safe-nav-route-recent-v1'
const legacyRecentSearchKey = 'localhub-route-recent-v1'
const mapEl = ref(null)
const loading = ref(true)
const error = ref('')
const routeError = ref('')
const locationError = ref('')
const cctv = ref([])
const police = ref([])
const summary = ref(null)
const showCctv = ref(true)
const showHeatmap = ref(false)
const showPolice = ref(true)
const district = ref('전체')
const startQuery = ref('광주 중심')
const destinationQuery = ref('')
const routeLoading = ref(false)
const routeInfo = ref(null)
const routeChoices = ref(null)
const routeMode = ref('shortest')
const guides = ref([])
const hasDestination = ref(false)
const startAddress = ref('광주 중심')
const destinationAddress = ref('목적지를 선택하세요')
const navigationActive = ref(false)
const nearestPolice = ref([])
const recentSearches = ref(readRecentSearches())
let kakao, map, clusterer, startMarker, endMarker, routeLine, alternateLine, infoWindow
let markers = []
let policeMarkers = []
let policeZones = []
let heatCircles = []
let blindCircles = []

function readRecentSearches() {
  try {
    const current = localStorage.getItem(recentSearchKey)
    const legacy = localStorage.getItem(legacyRecentSearchKey)
    if (!current && legacy) localStorage.setItem(recentSearchKey, legacy)
    const value = JSON.parse(current || legacy || '[]')
    return Array.isArray(value) ? value.slice(0, 5) : []
  } catch { return [] }
}

const districts = computed(() => ['전체', ...new Set(police.value.map(item => item.district).filter(Boolean))])
const filteredPolice = computed(() => police.value.filter(item => district.value === '전체' || item.district === district.value))

function markerImage(color) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="34" height="42"><path fill="${color}" stroke="white" stroke-width="2" d="M17 1C8 1 2 8 2 17c0 12 15 24 15 24s15-12 15-24C32 8 26 1 17 1z"/><circle cx="17" cy="17" r="6" fill="white"/></svg>`
  return new kakao.maps.MarkerImage(`data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`, new kakao.maps.Size(34, 42), { offset: new kakao.maps.Point(17, 42) })
}
function resolveAddress(lat, lng, target) {
  const service = new kakao.maps.services.Geocoder()
  service.coord2Address(lng, lat, (result, status) => {
    if (status === kakao.maps.services.Status.OK) target.value = result[0]?.road_address?.address_name || result[0]?.address?.address_name || `${lat.toFixed(5)}, ${lng.toFixed(5)}`
  })
}
function clearRoute() {
  routeLine?.setMap(null)
  alternateLine?.setMap(null)
  routeLine = null
  alternateLine = null
  blindCircles.forEach(circle => circle.setMap(null))
  blindCircles = []
  routeInfo.value = null
  routeChoices.value = null
  guides.value = []
  navigationActive.value = false
  routeError.value = ''
}
function setStart(lat, lng, label = '') {
  clearRoute()
  startMarker?.setMap(null)
  startMarker = new kakao.maps.Marker({ map, position: new kakao.maps.LatLng(lat, lng), image: markerImage('#16805e'), title: '출발지' })
  if (label) {
    startAddress.value = label
    startQuery.value = label
  } else {
    resolveAddress(lat, lng, startAddress)
    resolveAddress(lat, lng, startQuery)
  }
  map.panTo(startMarker.getPosition())
  nearestPolice.value = nearestFacilities({ lat, lng }, police.value)
}
function setEnd(lat, lng, label = '') {
  clearRoute()
  endMarker?.setMap(null)
  endMarker = new kakao.maps.Marker({ map, position: new kakao.maps.LatLng(lat, lng), image: markerImage('#d64545'), title: label || '목적지' })
  hasDestination.value = true
  if (label) {
    destinationAddress.value = label
    destinationQuery.value = label
  } else {
    resolveAddress(lat, lng, destinationAddress)
    resolveAddress(lat, lng, destinationQuery)
  }
  map.panTo(endMarker.getPosition())
}
function locate() {
  locationError.value = ''
  if (!navigator.geolocation) return locationError.value = '이 브라우저는 위치 정보를 지원하지 않습니다.'
  navigator.geolocation.getCurrentPosition(
    position => setStart(position.coords.latitude, position.coords.longitude),
    event => locationError.value = event.code === 1 ? '위치 권한이 거부되어 광주 중심을 출발지로 사용합니다.' : '현재 위치를 확인하지 못했습니다.',
    { enableHighAccuracy: true, timeout: 10000 },
  )
}
function geocode(query, target = 'end') {
  if (!(query || '').trim()) return
  const service = new kakao.maps.services.Geocoder()
  service.addressSearch(query, (result, status) => {
    if (status === kakao.maps.services.Status.OK) {
      const first = result[0]
      const display = first.road_address?.address_name || first.address?.address_name || query
      if (target === 'start') setStart(Number(first.y), Number(first.x), display)
      else setEnd(Number(first.y), Number(first.x), display)
      routeError.value = ''
    } else routeError.value = '주소를 찾지 못했습니다. 도로명 또는 지번 주소를 입력해주세요.'
  })
}
function swapPoints() {
  if (!startMarker || !endMarker) return
  const oldStart = startMarker.getPosition()
  const oldEnd = endMarker.getPosition()
  const oldStartAddress = startAddress.value
  const oldEndAddress = destinationAddress.value
  setStart(oldEnd.getLat(), oldEnd.getLng(), oldEndAddress)
  setEnd(oldStart.getLat(), oldStart.getLng(), oldStartAddress)
}
function createCctvMarkers() {
  markers = cctv.value.map(item => {
    const marker = new kakao.maps.Marker({ position: new kakao.maps.LatLng(item.lat, item.lng), title: `CCTV ${item.count}대` })
    kakao.maps.event.addListener(marker, 'click', () => {
      infoWindow?.close()
      infoWindow = new kakao.maps.InfoWindow({ content: `<div style="padding:10px 12px;min-width:170px;font-size:13px"><b>이 위치 CCTV ${item.count}대</b><br>위도 ${item.lat}<br>경도 ${item.lng}</div>` })
      infoWindow.open(map, marker)
    })
    return marker
  })
  clusterer = new kakao.maps.MarkerClusterer({ map, averageCenter: true, minLevel: 6, markers })
}
function createSafetyLayers() {
  policeMarkers = police.value.filter(item => item.mapReady).map(item => {
    const position = new kakao.maps.LatLng(item.lat, item.lng)
    const marker = new kakao.maps.Marker({ map: showPolice.value ? map : null, position, image: markerImage('#f5b82e'), title: item.name })
    const zone = new kakao.maps.Circle({ map: showPolice.value ? map : null, center: position, radius: item.type === '지구대' ? 180 : 130, strokeWeight: 1, strokeColor: '#0f8a60', strokeOpacity: .6, strokeStyle: 'dashed', fillColor: '#3ac68c', fillOpacity: .08 })
    kakao.maps.event.addListener(marker, 'click', () => {
      infoWindow?.close()
      infoWindow = new kakao.maps.InfoWindow({ content: `<div style="padding:10px 12px;min-width:180px;font-size:13px"><b>${item.name}</b><br>${item.type} · ${item.address}<br><span style="color:#16805e">안전구역 반경 ${item.type === '지구대' ? 180 : 130}m</span></div>` })
      infoWindow.open(map, marker)
    })
    policeZones.push(zone)
    return marker
  })
  const groups = new Map()
  cctv.value.forEach(item => {
    const id = `${item.lat.toFixed(2)},${item.lng.toFixed(2)}`
    const group = groups.get(id) || { lat: 0, lng: 0, weight: 0, points: 0 }
    group.lat += item.lat
    group.lng += item.lng
    group.weight += item.count || 1
    group.points += 1
    groups.set(id, group)
  })
  heatCircles = [...groups.values()].sort((a, b) => b.weight - a.weight).slice(0, 45).map(group => {
    const density = group.weight
    return new kakao.maps.Circle({ map: showHeatmap.value ? map : null, center: new kakao.maps.LatLng(group.lat / group.points, group.lng / group.points), radius: 450 + Math.min(650, density * 20), strokeWeight: 0, fillColor: density >= 35 ? '#149d69' : density >= 15 ? '#f0b629' : '#df5656', fillOpacity: .16 })
  })
}
function lineCoordinates(features) {
  return features.filter(item => item.geometry?.type === 'LineString').flatMap(item => item.geometry.coordinates)
}
function analyseRoute(features, route) {
  guides.value = features.filter(item => item.geometry?.type === 'Point' && item.properties?.description).slice(0, 10).map((step, index) => ({
    title: step.properties.description,
    text: index === 0 ? '출발 전 주변을 확인하고 이동하세요.' : step.properties.turnType === 200 ? '목적지에 도착합니다.' : route.blindRatio > .25 && index === Math.floor(features.length / 3) ? 'CCTV 사각 구간이 포함됩니다. 주변을 확인하세요.' : `${step.properties.distance || 0}m 이동 · CCTV와 경찰 안전구역을 확인하세요.`,
  }))
}
function drawRoute(mode) {
  if (!routeChoices.value) return
  routeMode.value = mode
  navigationActive.value = false
  routeLine?.setMap(null)
  alternateLine?.setMap(null)
  blindCircles.forEach(circle => circle.setMap(null))
  blindCircles = []
  const selected = mode === 'safe' ? routeChoices.value.safest : routeChoices.value.fastest
  routeInfo.value = selected
  const selectedPath = selected.coordinates.map(([lng, lat]) => new kakao.maps.LatLng(lat, lng))
  routeLine = new kakao.maps.Polyline({ map, path: selectedPath, strokeWeight: 8, strokeColor: mode === 'safe' ? '#0f8a60' : '#3277d5', strokeOpacity: .95, strokeStyle: 'solid' })
  blindCircles = selected.blindSamples.slice(0, 24).map(point => new kakao.maps.Circle({ map, center: new kakao.maps.LatLng(point.lat, point.lng), radius: 65, strokeWeight: 2, strokeColor: '#df3f49', strokeOpacity: .65, fillColor: '#ef5350', fillOpacity: .13 }))
  analyseRoute(selected.features, selected)
  const bounds = new kakao.maps.LatLngBounds()
  selectedPath.forEach(position => bounds.extend(position))
  map.setBounds(bounds)
}
function selectRouteMode(mode) {
  if (routeChoices.value) drawRoute(mode)
  else routeMode.value = mode
}
async function findRoute() {
  routeError.value = ''
  routeInfo.value = null
  guides.value = []
  navigationActive.value = false
  if (!endMarker) return routeError.value = '지도 클릭 또는 주소 검색으로 목적지를 지정해주세요.'
  if (!startMarker) setStart(center.lat, center.lng, '광주 중심')
  const key = import.meta.env.VITE_TMAP_APP_KEY
  if (!key) return routeError.value = 'TMAP API 키가 설정되지 않았습니다.'
  routeLoading.value = true
  try {
    const start = startMarker.getPosition()
    const end = endMarker.getPosition()
    const requests = [0, 4, 10].map(async option => {
      const response = await fetch('https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1&format=json', {
        method: 'POST', headers: { appKey: key, 'Content-Type': 'application/json' },
        body: JSON.stringify({ startX: String(start.getLng()), startY: String(start.getLat()), endX: String(end.getLng()), endY: String(end.getLat()), startName: startAddress.value, endName: destinationAddress.value, searchOption: option }),
      })
      if (!response.ok) throw new Error(response.status === 401 ? 'TMAP API 키를 확인해주세요.' : 'TMAP 길찾기 요청에 실패했습니다.')
      const data = await response.json()
      const features = data.features || []
      const coordinates = lineCoordinates(features)
      const properties = features.find(item => item.properties?.totalDistance)?.properties || features[0]?.properties || {}
      if (coordinates.length < 2) throw new Error('경로 데이터가 비어 있습니다.')
      return { id: `tmap-${option}`, option, coordinates, features, distance: Number(properties.totalDistance || 0), time: Number(properties.totalTime || 0) }
    })
    const settled = await Promise.allSettled(requests)
    const candidates = settled.filter(item => item.status === 'fulfilled').map(item => item.value)
    if (!candidates.length) throw settled[0]?.reason || new Error('경로 후보를 찾지 못했습니다.')
    const unique = candidates.filter((candidate, index, list) => list.findIndex(item => `${item.coordinates.length}-${item.distance}` === `${candidate.coordinates.length}-${candidate.distance}`) === index)
    routeChoices.value = chooseRoutes(unique, cctv.value, police.value)
    drawRoute(routeMode.value)
    recentSearches.value = [destinationAddress.value, ...recentSearches.value.filter(item => item !== destinationAddress.value)].slice(0, 5)
    localStorage.setItem(recentSearchKey, JSON.stringify(recentSearches.value))
  } catch (event) {
    routeError.value = event instanceof TypeError ? 'TMAP 연결이 차단되었습니다. 네트워크 또는 CORS 설정을 확인해주세요.' : event.message
  } finally { routeLoading.value = false }
}

watch(showCctv, value => { if (clusterer) value ? clusterer.addMarkers(markers) : clusterer.clear() })
watch(showPolice, value => { policeMarkers.forEach(marker => marker.setMap(value ? map : null)); policeZones.forEach(zone => zone.setMap(value ? map : null)) })
watch(showHeatmap, value => heatCircles.forEach(circle => circle.setMap(value ? map : null)))
onMounted(async () => {
  try {
    const [cctvResponse, policeResponse, summaryResponse] = await Promise.all([fetch('/data/cctv_gwangju.clean.json'), fetch('/data/police_gwangju.clean.json'), fetch('/data/gwangju-data-summary.json')])
    if (!cctvResponse.ok || !policeResponse.ok || !summaryResponse.ok) throw new Error('공공데이터 파일을 불러오지 못했습니다.')
    ;[cctv.value, police.value, summary.value] = await Promise.all([cctvResponse.json(), policeResponse.json(), summaryResponse.json()])
    if (!cctv.value.length) throw new Error('CCTV 데이터가 비어 있습니다.')
    kakao = await loadKakaoMap()
    loading.value = false
    await nextTick()
    if (!mapEl.value) throw new Error('지도 화면을 준비하지 못했습니다.')
    map = new kakao.maps.Map(mapEl.value, { center: new kakao.maps.LatLng(center.lat, center.lng), level: 8 })
    createCctvMarkers()
    createSafetyLayers()
    setStart(center.lat, center.lng, '광주 중심')
    kakao.maps.event.addListener(map, 'click', event => setEnd(event.latLng.getLat(), event.latLng.getLng()))
  } catch (event) { error.value = event.message }
  finally { loading.value = false }
})
onBeforeUnmount(() => { routeLine?.setMap(null); alternateLine?.setMap(null); clusterer?.clear(); policeMarkers.forEach(marker => marker.setMap(null)); policeZones.forEach(zone => zone.setMap(null)); heatCircles.forEach(circle => circle.setMap(null)); blindCircles.forEach(circle => circle.setMap(null)) })
</script>

<template>
  <main class="page map-page">
    <div class="map-heading">
      <div><span class="eyebrow">SAFE WALKING</span><h1 class="page-title">안심 귀가 길찾기</h1><p class="page-subtitle">빠른 길과 안전시설 정보를 함께 확인하세요.</p></div>
      <div v-if="summary" class="data-badge"><b>● 데이터 연결</b><span>CCTV {{ summary.cctvTotal }}대 · 경찰시설 {{ summary.policeTotal }}곳</span></div>
    </div>
    <div v-if="error" class="error-box">{{ error }}</div>
    <div v-else-if="loading" class="empty map-loading">지도와 공공데이터를 불러오는 중입니다…</div>
    <template v-else>
      <section class="route-workspace">
        <aside class="planner card">
          <div class="planner-title"><div><span>도보</span><h2>어디로 걸어갈까요?</h2></div><button class="swap" title="출발지와 목적지 바꾸기" :disabled="!startMarker || !endMarker" @click="swapPoints">⇅</button></div>
          <div class="route-points">
            <div class="point-row"><i class="start-dot"></i><div class="destination-input"><small>출발</small><input v-model="startQuery" aria-label="출발지 주소" placeholder="출발지 주소" @keyup.enter="geocode(startQuery, 'start')"></div><div class="point-actions"><button @click="geocode(startQuery, 'start')">검색</button><button @click="locate">현위치</button></div></div>
            <div class="point-line"></div>
            <div class="point-row"><i class="end-dot"></i><div class="destination-input"><small>도착</small><input v-model="destinationQuery" aria-label="도착지 주소" placeholder="도로명 또는 지번 주소" @keyup.enter="geocode(destinationQuery)"></div><button @click="geocode(destinationQuery)">검색</button></div>
          </div>
          <p v-if="locationError" class="mini-error">{{ locationError }}</p>
          <p class="map-tip">지도에서 원하는 지점을 눌러 목적지로 지정할 수도 있어요.</p>
          <div v-if="recentSearches.length" class="recent-routes"><span>최근 검색</span><button v-for="item in recentSearches" :key="item" @click="destinationQuery = item; geocode(item)">{{ item }}</button></div>
          <div class="mode-label">경로 선택</div>
          <div class="route-options">
            <button :class="{ active: routeMode === 'shortest' }" @click="selectRouteMode('shortest')"><span class="route-icon blue-route">↗</span><div><b>최단 시간</b><small v-if="routeChoices">{{ Math.ceil(routeChoices.fastest.time / 60) }}분 · {{ (routeChoices.fastest.distance / 1000).toFixed(1) }}km · 안전 {{ routeChoices.fastest.safetyScore }}</small><small v-else>가장 빠른 보행 경로</small></div><em v-if="routeMode === 'shortest'">✓</em></button>
            <button :class="{ active: routeMode === 'safe' }" @click="selectRouteMode('safe')"><span class="route-icon green-route">✓</span><div><b>CCTV 우선 안전경로</b><small v-if="routeChoices">{{ Math.ceil(routeChoices.safest.time / 60) }}분 · CCTV {{ routeChoices.safest.cctvCount }}대 · 안전 {{ routeChoices.safest.safetyScore }}<template v-if="routeChoices.safest.id === routeChoices.fastest.id"> · 최단과 동일</template></small><small v-else>CCTV가 많은 구간과 사각지대가 적은 경로</small></div><em v-if="routeMode === 'safe'">✓</em></button>
          </div>
          <button class="find-button" :disabled="!hasDestination || routeLoading" @click="findRoute"><span>{{ routeLoading ? '경로 분석 중…' : '안전 경로 찾기' }}</span><b>→</b></button>
          <p v-if="routeError" class="mini-error">{{ routeError }}</p>
          <div v-if="routeInfo" class="route-summary">
            <div class="summary-head"><span>{{ routeMode === 'safe' ? '추천 안전 경로' : '최단 보행 경로' }}</span><b>{{ Math.ceil(routeInfo.time / 60) }}분</b></div>
            <div class="summary-numbers"><span><b>{{ (routeInfo.distance / 1000).toFixed(1) }}</b> km</span><span><b>{{ routeInfo.safetyScore }}</b> 안전점수</span><span><b>{{ routeInfo.cctvCount }}</b> CCTV</span></div>
            <p class="route-facility">경찰 안전구역 {{ routeInfo.policeCount }}곳 · 사각 비율 {{ Math.round(routeInfo.blindRatio * 100) }}%</p>
            <button class="guide-button" @click="navigationActive = !navigationActive">{{ navigationActive ? '안내 종료' : '안내 시작' }}</button>
          </div>
          <div v-if="routeInfo?.blindRatio > .2" class="blind-warning"><b>⚠ CCTV 사각 구간 주의</b><span>붉은 원으로 표시된 구간은 반경 90m 안에 CCTV·치안시설이 확인되지 않습니다.</span><button v-if="routeMode !== 'safe'" @click="selectRouteMode('safe')">안전 경로로 우회</button></div>
          <div class="layer-toggles">
            <label><input v-model="showCctv" type="checkbox"> CCTV</label>
            <label><input v-model="showHeatmap" type="checkbox"> 안전도 히트맵</label>
          </div>
          <div v-if="nearestPolice.length" class="nearest-box"><span>가까운 경찰시설</span><button v-for="item in nearestPolice" :key="item.id" @click="geocode(item.address)"><b>{{ item.name }}</b><small>{{ Math.round(item.distance) }}m · {{ item.type }}</small></button></div>
        </aside>

        <section class="map-panel">
          <div v-if="navigationActive" class="navigation-banner"><span>다음 안내</span><b>{{ guides[1]?.title || guides[0]?.title || '경로를 따라 이동하세요' }}</b><small>실제 현장 상황과 주변을 함께 확인하세요.</small></div>
          <div ref="mapEl" class="map" aria-label="카카오 안전지도"></div>
          <div class="map-legend"><span><i class="cluster-dot"></i>CCTV</span><span><i class="police-dot"></i>경찰</span><span><i class="start-dot"></i>출발</span><span><i class="end-dot"></i>도착</span></div>
          <div class="address-strip card">
            <div><i class="start-dot"></i><span><small>출발 주소</small><b>{{ startAddress }}</b></span></div>
            <span class="arrow">→</span>
            <div><i class="end-dot"></i><span><small>도착 주소</small><b>{{ destinationAddress }}</b></span></div>
          </div>
          <div v-if="routeChoices" class="safety-method card"><b>safe_nav 안전 가중치</b><span>CCTV 밀도 30점</span><span>경찰 안전구역 18점</span><span>사각지대 없는 구간 14점</span><small>실제 TMAP 후보 3개를 비교하며 예상 시간은 동점 경로의 우선순위에 반영합니다.</small></div>
        </section>
      </section>

      <section v-if="guides.length" class="guidance card">
        <div class="section-title"><div><span class="eyebrow">TURN BY TURN</span><h2>단계별 길안내</h2></div><span>{{ guides.length }}단계</span></div>
        <ol><li v-for="(guide, index) in guides" :key="index"><b>{{ index + 1 }}</b><div><strong>{{ guide.title }}</strong><p>{{ guide.text }}</p></div></li></ol>
      </section>

      <section class="police card">
        <div class="section-title"><div><span class="eyebrow">SAFE PLACE</span><h2>목적지로 선택할 경찰시설</h2></div><select v-model="district"><option v-for="item in districts" :key="item">{{ item }}</option></select></div>
        <div class="police-grid"><button v-for="item in filteredPolice" :key="item.id" @click="geocode(item.address)"><span class="shield">✓</span><div><b>{{ item.name }}</b><small>{{ item.type }} · {{ item.address }}</small></div><em>목적지</em></button></div>
      </section>
      <p class="data-warning">※ 현재 CCTV 데이터는 광산구 지역에 편중되어 있습니다. CCTV와 경로 정보는 참고용이며 실제 안전을 보장하지 않습니다.</p>
    </template>
  </main>
</template>

<style scoped>
.map-page{max-width:1400px}.map-heading{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:24px}.eyebrow{display:block;color:var(--green);font-size:.7rem;font-weight:900;letter-spacing:.14em;margin-bottom:5px}.page-subtitle{margin-bottom:0}.data-badge{display:flex;flex-direction:column;align-items:flex-end;padding:10px 14px;border-radius:12px;background:#e8f5ef;color:var(--green)}.data-badge b{font-size:.78rem}.data-badge span{color:#527069;font-size:.7rem;margin-top:2px}.map-loading{min-height:560px;display:grid;place-items:center}.route-workspace{display:grid;grid-template-columns:390px minmax(0,1fr);gap:16px;align-items:start}.planner{padding:21px;position:sticky;top:88px}.planner-title{display:flex;justify-content:space-between;align-items:center}.planner-title span{color:var(--green);font-size:.7rem;font-weight:900}.planner-title h2{margin:3px 0 18px;font-size:1.2rem}.swap{width:34px;height:34px;border-radius:10px;background:#edf4f1;color:var(--green);font-weight:900}.swap:disabled{opacity:.4;cursor:not-allowed}.route-points{position:relative;background:#f7faf8;border:1px solid #e0e9e4;border-radius:14px;padding:5px 12px}.point-row{display:grid;grid-template-columns:14px minmax(0,1fr) auto;gap:10px;align-items:center;min-height:61px}.point-row>div:not(.destination-input),.destination-input{min-width:0}.point-row small,.address-strip small{display:block;color:#7b8e87;font-size:.68rem}.point-row strong{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:.84rem}.point-row button{background:#e3f1eb;color:var(--green);border-radius:8px;padding:7px 9px;font-size:.72rem;font-weight:850}.point-actions{display:flex;gap:4px}.point-actions button{padding-inline:7px}.point-line{position:absolute;left:30px;top:54px;height:18px;border-left:2px dotted #9cb5ac}.start-dot,.end-dot,.cluster-dot,.police-dot{display:inline-block;width:10px;height:10px;border-radius:50%;flex:0 0 auto}.start-dot{background:#11815e;box-shadow:0 0 0 4px #11815e18}.end-dot{background:#e14949;box-shadow:0 0 0 4px #e1494918}.cluster-dot{background:#3277d5}.police-dot{background:#f5b82e}.destination-input input{width:100%;border:0;background:transparent;padding:2px 0;font-size:.84rem;font-weight:700;color:var(--ink);outline:0}.map-tip{font-size:.7rem;color:#758780;margin:9px 2px}.recent-routes{display:flex;gap:5px;overflow:auto;margin:0 0 14px;align-items:center}.recent-routes>span{flex:0 0 auto;font-size:.65rem;color:#7b8e87}.recent-routes button{flex:0 0 auto;max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;padding:5px 8px;border-radius:20px;background:#edf4f1;color:#42665a;font-size:.65rem}.mode-label{font-size:.72rem;font-weight:850;margin:0 0 7px}.route-options{display:grid;gap:7px}.route-options>button{display:grid;grid-template-columns:34px 1fr auto;gap:9px;align-items:center;text-align:left;background:#fff;border:1px solid var(--line);border-radius:12px;padding:10px}.route-options>button.active{border:2px solid var(--green);padding:9px;background:#f5fbf8}.route-options b,.route-options small{display:block}.route-options b{font-size:.82rem}.route-options mark{border-radius:8px;padding:2px 5px;background:#daf3e7;color:#087351;font-size:.56rem}.route-options small{font-size:.68rem;color:var(--muted);margin-top:2px}.route-options em{font-style:normal;color:var(--green);font-weight:900}.route-icon{display:grid;place-items:center;width:32px;height:32px;border-radius:10px;color:#fff;font-weight:900}.blue-route{background:#3277d5}.green-route{background:var(--green)}.find-button{width:100%;display:flex;justify-content:space-between;align-items:center;margin-top:13px;padding:14px 16px;border-radius:12px;background:var(--green);color:#fff;font-weight:900;box-shadow:0 8px 22px #0f765732}.find-button:disabled{background:#a9bbb5;box-shadow:none;cursor:not-allowed}.mini-error{font-size:.75rem;color:#ae3030;background:#fff1f1;padding:8px;border-radius:8px}.route-summary{margin-top:12px;border-radius:13px;padding:13px;background:#0f4d3c;color:#fff}.summary-head{display:flex;justify-content:space-between;align-items:center}.summary-head span{font-size:.72rem;color:#b6ded0}.summary-head b{font-size:1.35rem}.summary-numbers{display:grid;grid-template-columns:repeat(3,1fr);gap:5px;margin:12px 0 6px}.summary-numbers span{font-size:.64rem;color:#b6ded0}.summary-numbers b{display:block;color:#fff;font-size:.94rem}.route-facility{font-size:.65rem;color:#b6ded0;margin:0 0 10px}.guide-button{width:100%;border-radius:9px;padding:10px;background:#fff;color:#0f4d3c;font-weight:900}.blind-warning{display:grid;gap:5px;margin-top:10px;padding:10px;border:1px solid #f1b6b6;border-radius:10px;background:#fff1f1;color:#9d3030}.blind-warning b{font-size:.72rem}.blind-warning span{font-size:.64rem;line-height:1.45}.blind-warning button{justify-self:start;padding:5px 8px;border-radius:7px;background:#d9434b;color:#fff;font-size:.65rem;font-weight:800}.layer-toggles{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}.layer-toggles label{display:flex;align-items:center;gap:5px;padding:6px 8px;border-radius:8px;background:#f1f6f3;color:#526a62;font-size:.68rem}.nearest-box{display:grid;gap:5px;margin-top:11px;padding-top:10px;border-top:1px solid #e5ece8}.nearest-box>span{font-size:.67rem;font-weight:850;color:#657b73}.nearest-box button{display:flex;justify-content:space-between;text-align:left;padding:6px 8px;border-radius:8px;background:#fff;border:1px solid #e6ece9}.nearest-box b{font-size:.68rem}.nearest-box small{font-size:.62rem;color:#72837d}.map-panel{min-width:0;position:relative}.map{width:100%;height:650px;border:1px solid var(--line);border-radius:18px;background:#e9efec;overflow:hidden}.navigation-banner{position:absolute;z-index:5;top:15px;left:50%;transform:translateX(-50%);width:min(520px,calc(100% - 30px));padding:13px 16px;border-radius:13px;background:#143f35ed;color:#fff;box-shadow:0 8px 24px #10231d55}.navigation-banner span,.navigation-banner b,.navigation-banner small{display:block}.navigation-banner span{color:#9ed7c4;font-size:.65rem}.navigation-banner b{font-size:1rem;margin:2px 0}.navigation-banner small{opacity:.74}.map-legend{position:absolute;top:14px;right:14px;display:flex;gap:12px;padding:8px 10px;border-radius:9px;background:#fffffff2;z-index:3;font-size:.68rem}.map-legend span{display:flex;align-items:center;gap:5px}.address-strip{display:grid;grid-template-columns:1fr 24px 1fr;align-items:center;gap:8px;margin-top:10px;padding:14px 17px}.address-strip>div{display:flex;align-items:center;gap:10px;min-width:0}.address-strip span span{min-width:0}.address-strip b{display:block;font-size:.78rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.arrow{text-align:center;color:#9aaba5}.safety-method{display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin-top:8px;padding:11px 14px}.safety-method b{font-size:.7rem;color:var(--green)}.safety-method span{padding:4px 7px;border-radius:12px;background:#edf5f1;font-size:.62rem}.safety-method small{width:100%;color:#72847d;font-size:.61rem}.guidance,.police{margin-top:16px;padding:22px}.section-title{display:flex;align-items:end;justify-content:space-between;margin-bottom:15px}.section-title h2{font-size:1.15rem;margin:0}.section-title>span{color:var(--muted);font-size:.75rem}.guidance ol{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;list-style:none;padding:0;margin:0}.guidance li{display:flex;gap:10px;padding:12px;background:#f6f9f7;border-radius:11px}.guidance li>b{display:grid;place-items:center;flex:0 0 26px;height:26px;border-radius:50%;background:var(--green);color:#fff;font-size:.72rem}.guidance strong{font-size:.78rem}.guidance p{color:var(--muted);font-size:.68rem;margin:3px 0}.police select{border:1px solid #bfd0c8;border-radius:9px;padding:8px;background:#fff}.police-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;max-height:290px;overflow:auto}.police-grid button{display:grid;grid-template-columns:34px 1fr auto;gap:9px;align-items:center;text-align:left;border:1px solid #e2eae6;border-radius:11px;background:#fff;padding:11px}.shield{display:grid;place-items:center;width:32px;height:32px;border-radius:10px;background:#e4f3ec;color:var(--green);font-weight:900}.police-grid b,.police-grid small{display:block}.police-grid b{font-size:.78rem}.police-grid small{font-size:.63rem;color:var(--muted);margin-top:2px}.police-grid em{font-style:normal;color:var(--green);font-size:.64rem;font-weight:850}.data-warning{text-align:center;color:#71827c;font-size:.7rem;margin:16px 0 0}@media(max-width:1000px){.route-workspace{grid-template-columns:350px 1fr}.map{height:590px}.police-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:760px){.map-page{width:calc(100% - 20px)}.map-heading{display:block}.data-badge{align-items:flex-start;margin-top:14px}.route-workspace{display:flex;flex-direction:column}.planner{width:100%;position:static}.map-panel{width:100%}.map{height:480px}.guidance ol,.police-grid{grid-template-columns:1fr}.address-strip{grid-template-columns:1fr}.address-strip .arrow{transform:rotate(90deg)}.section-title{align-items:flex-start;gap:10px}.police{padding:17px}}@media(max-width:430px){.map{height:430px}.planner{padding:16px}.map-legend{top:auto;bottom:12px;gap:7px}.address-strip{padding:12px}.guidance{padding:16px}.summary-numbers{gap:2px}.point-row{gap:7px}.point-actions button{padding-inline:5px}.nearest-box{display:none}}
</style>
