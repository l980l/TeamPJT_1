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
      posts.value = []
    } finally {
      loading.value = false
    }
  }

  // 추가: 조회수 기준 상위 로드 함수
  async function loadTopByViews(limit = 5) {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`/api/posts?limit=${limit}&sort=views_desc`)
      if (!response.ok) throw new Error(`로드 실패: ${response.status}`)
      posts.value = await response.json()
    } catch (e: any) {
      error.value = e.message || '로드 실패'
      posts.value = []
    } finally {
      loading.value = false
    }
  }

  return { posts, loading, error, loadRecent, loadTopByViews }
}