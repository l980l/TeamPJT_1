import { ref } from 'vue'

export function usePosts() {
  const posts = ref<any[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function loadRecent(limit = 5) {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`/api/posts?limit=${limit}&sort=desc`)
      if (!response.ok) {
        throw new Error(`로드 실패: ${response.status}`)
      }
      posts.value = await response.json()
    } catch (e: any) {
      error.value = e.message || '로드 실패'
      // 백엔드가 아직 없으면 간단한 모킹으로 대체 가능
      posts.value = [{ id:1, title:'샘플', content:'내용', category:'카테고리', created_at: new Date().toISOString() }]
    } finally {
      loading.value = false
    }
  }

  return { posts, loading, error, loadRecent }
}