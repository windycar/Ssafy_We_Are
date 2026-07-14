import { readFile, mkdir, writeFile } from 'node:fs/promises'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const project = join(dirname(fileURLToPath(import.meta.url)), '..')
const source = join(project, '..', '데이터들', '광주_정제데이터')
const output = join(project, 'public', 'data')
const cctvSource = JSON.parse(await readFile(join(source, 'cctv_gwangju.json'), 'utf8'))
const policeSource = JSON.parse(await readFile(join(source, 'police_gwangju.json'), 'utf8'))
let policeCoordinates = []
try { policeCoordinates = JSON.parse(await readFile(join(output, 'police_gwangju.coordinates.json'), 'utf8')) } catch {}
const coordinateMap = new Map(policeCoordinates.map(item => [item.id, item]))
const grouped = new Map()

for (const item of cctvSource) {
  const key = `${item.lat},${item.lng}`
  const current = grouped.get(key) || { id: `cctv-${grouped.size + 1}`, lat: item.lat, lng: item.lng, count: 0, sourceIds: [], type: 'CCTV' }
  current.count += 1
  current.sourceIds.push(item.id)
  grouped.set(key, current)
}
const cctv = [...grouped.values()]
const police = policeSource.map(item => {
  const point = coordinateMap.get(item.id)
  return { ...item, lat: point?.lat || null, lng: point?.lng || null, mapReady: Boolean(point?.lat && point?.lng) }
})
const summary = { cctvTotal: cctv.reduce((sum, item) => sum + item.count, 0), cctvMarkers: cctv.length, policeTotal: police.length, generatedAt: new Date().toISOString() }
await mkdir(output, { recursive: true })
await Promise.all([
  writeFile(join(output, 'cctv_gwangju.clean.json'), JSON.stringify(cctv, null, 2)),
  writeFile(join(output, 'police_gwangju.clean.json'), JSON.stringify(police, null, 2)),
  writeFile(join(output, 'gwangju-data-summary.json'), JSON.stringify(summary, null, 2)),
])
console.log(`공공데이터 준비 완료: CCTV ${summary.cctvTotal}대/${summary.cctvMarkers}개 지점, 경찰 시설 ${summary.policeTotal}곳`)
