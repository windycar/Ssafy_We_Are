export const STORAGE_KEY = 'safe-nav-posts-v1'
const SEED_KEY = 'safe-nav-posts-seeded-v1'
const LEGACY_STORAGE_KEY = 'localhub-posts-v1'
const LEGACY_SEED_KEY = 'localhub-posts-seeded-v1'
export const CATEGORIES = ['안전제보', '동네정보', '질문', '자유']

function migrateLegacyStorage() {
  const legacyPosts = localStorage.getItem(LEGACY_STORAGE_KEY)
  if (!localStorage.getItem(STORAGE_KEY) && legacyPosts) localStorage.setItem(STORAGE_KEY, legacyPosts)
  if (!localStorage.getItem(SEED_KEY) && localStorage.getItem(LEGACY_SEED_KEY)) localStorage.setItem(SEED_KEY, 'true')
}

export function getPosts() {
  try {
    migrateLegacyStorage()
    const value = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    return Array.isArray(value) ? value : []
  } catch {
    localStorage.setItem(STORAGE_KEY, '[]')
    return []
  }
}
function save(posts) { localStorage.setItem(STORAGE_KEY, JSON.stringify(posts)) }
export async function ensureSeedPosts() {
  const current = getPosts()
  if (current.length || localStorage.getItem(SEED_KEY)) return current
  try {
    const response = await fetch('/data/community-seed.json')
    if (!response.ok) return current
    const seed = await response.json()
    if (!Array.isArray(seed)) return current
    save(seed)
    localStorage.setItem(SEED_KEY, 'true')
    return seed
  } catch { return current }
}
export function getPost(id) { return getPosts().find(post => post.id === id) }
export function createPost(data) {
  const now = new Date().toISOString()
  const post = { id: crypto.randomUUID(), ...data, createdAt: now, updatedAt: now, viewCount: 0 }
  save([post, ...getPosts()]); return post
}
export function updatePost(id, data) {
  let updated
  save(getPosts().map(post => post.id === id ? (updated = { ...post, ...data, id, updatedAt: new Date().toISOString() }) : post))
  return updated
}
export function deletePost(id) { save(getPosts().filter(post => post.id !== id)) }
export function incrementView(id) {
  const posts = getPosts(); const post = posts.find(item => item.id === id)
  if (post) { post.viewCount = (post.viewCount || 0) + 1; save(posts) }
  return post
}
export function verifyPassword(post, password) { return Boolean(post && password === post.password) }
