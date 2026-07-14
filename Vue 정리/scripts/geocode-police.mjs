import { readFile, writeFile } from 'node:fs/promises'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const project = join(dirname(fileURLToPath(import.meta.url)), '..')
const root = join(project, '..')
const env = Object.fromEntries((await readFile(join(root, '.env'), 'utf8'))
  .split(/\r?\n/)
  .filter(line => line && !line.startsWith('#') && line.includes('='))
  .map(line => [line.slice(0, line.indexOf('=')), line.slice(line.indexOf('=') + 1).trim()]))
const key = env.VITE_KAKAO_REST_API_KEY
if (!key) throw new Error('VITE_KAKAO_REST_API_KEY가 필요합니다.')

const sourcePath = join(root, '데이터들', '광주_정제데이터', 'police_gwangju.json')
const outputPath = join(project, 'public', 'data', 'police_gwangju.coordinates.json')
const facilities = JSON.parse(await readFile(sourcePath, 'utf8'))
const result = []

for (const facility of facilities) {
  const url = new URL('https://dapi.kakao.com/v2/local/search/address.json')
  url.searchParams.set('query', facility.address.replace(/\s+/g, ' ').trim())
  const response = await fetch(url, { headers: { Authorization: `KakaoAK ${key}` } })
  if (!response.ok) throw new Error(`경찰시설 좌표 변환 실패: ${response.status}`)
  const document = (await response.json()).documents?.[0]
  result.push({
    id: facility.id,
    lat: document ? Number(document.y) : null,
    lng: document ? Number(document.x) : null,
  })
  await new Promise(resolve => setTimeout(resolve, 90))
}

await writeFile(outputPath, `${JSON.stringify(result, null, 2)}\n`, 'utf8')
console.log(`광주 경찰시설 좌표 준비 완료: ${result.filter(item => item.lat && item.lng).length}/${result.length}곳`)
