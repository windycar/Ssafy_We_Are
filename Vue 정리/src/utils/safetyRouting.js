const EARTH_RADIUS = 6371000

export function distanceMeters(a, b) {
  const rad = Math.PI / 180
  const dLat = (b.lat - a.lat) * rad
  const dLng = (b.lng - a.lng) * rad
  const lat1 = a.lat * rad
  const lat2 = b.lat * rad
  const value = Math.sin(dLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) ** 2
  return EARTH_RADIUS * 2 * Math.atan2(Math.sqrt(value), Math.sqrt(1 - value))
}

function localPoint(point, origin) {
  const rad = Math.PI / 180
  return {
    x: (point.lng - origin.lng) * rad * EARTH_RADIUS * Math.cos(origin.lat * rad),
    y: (point.lat - origin.lat) * rad * EARTH_RADIUS,
  }
}

function pointSegmentDistance(point, start, end) {
  const p = localPoint(point, start)
  const b = localPoint(end, start)
  const length = b.x ** 2 + b.y ** 2
  const ratio = length ? Math.max(0, Math.min(1, (p.x * b.x + p.y * b.y) / length)) : 0
  return Math.hypot(p.x - b.x * ratio, p.y - b.y * ratio)
}

function nearRoute(point, coordinates, radius) {
  for (let index = 1; index < coordinates.length; index += 1) {
    const start = { lng: coordinates[index - 1][0], lat: coordinates[index - 1][1] }
    const end = { lng: coordinates[index][0], lat: coordinates[index][1] }
    if (pointSegmentDistance(point, start, end) <= radius) return true
  }
  return false
}

function routeSamples(coordinates, interval = 100) {
  const samples = []
  for (let index = 1; index < coordinates.length; index += 1) {
    const start = { lng: coordinates[index - 1][0], lat: coordinates[index - 1][1] }
    const end = { lng: coordinates[index][0], lat: coordinates[index][1] }
    const length = distanceMeters(start, end)
    const count = Math.max(1, Math.ceil(length / interval))
    for (let step = 0; step < count; step += 1) {
      const ratio = step / count
      samples.push({ lat: start.lat + (end.lat - start.lat) * ratio, lng: start.lng + (end.lng - start.lng) * ratio })
    }
  }
  const last = coordinates.at(-1)
  if (last) samples.push({ lng: last[0], lat: last[1] })
  return samples
}

export function scoreRoute(route, cctv, police) {
  const cctvNear = cctv.filter(point => nearRoute(point, route.coordinates, 55))
  const policeNear = police.filter(point => point.mapReady && nearRoute(point, route.coordinates, 120))
  const samples = routeSamples(route.coordinates)
  const blindSamples = samples.filter(sample => {
    const hasCctv = cctv.some(point => distanceMeters(sample, point) <= 90)
    const hasPolice = police.some(point => point.mapReady && distanceMeters(sample, point) <= 180)
    return !hasCctv && !hasPolice
  })
  const weightedCctv = cctvNear.reduce((sum, point) => sum + (point.count || 1), 0)
  const distanceKm = Math.max(.2, route.distance / 1000)
  const density = weightedCctv / distanceKm
  const coverage = samples.length ? 1 - blindSamples.length / samples.length : 0
  const rawScore = 38 + Math.min(30, density * 1.6) + Math.min(18, policeNear.length * 6) + coverage * 14
  return {
    ...route,
    cctvCount: weightedCctv,
    policeCount: policeNear.length,
    policeNames: policeNear.slice(0, 3).map(item => item.name),
    blindSamples,
    blindRatio: samples.length ? blindSamples.length / samples.length : 0,
    safetyScore: Math.round(Math.max(0, Math.min(100, rawScore))),
    weightedScore: rawScore - route.time / 900,
  }
}

export function chooseRoutes(routes, cctv, police) {
  const scored = routes.map(route => scoreRoute(route, cctv, police))
  const fastest = [...scored].sort((a, b) => a.time - b.time)[0]
  const safest = [...scored].sort((a, b) => b.weightedScore - a.weightedScore)[0]
  return { fastest, safest, all: scored }
}

export function nearestFacilities(origin, facilities, limit = 3) {
  return facilities.filter(item => item.mapReady).map(item => ({ ...item, distance: distanceMeters(origin, item) })).sort((a, b) => a.distance - b.distance).slice(0, limit)
}
