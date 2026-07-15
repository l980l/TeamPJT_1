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
      posts.value = [
        { id:1, title:'샘플 인기글 1', view_count:420, created_at: new Date().toISOString(), category:'맛집' },
        { id:2, title:'샘플 인기글 2', view_count:312, created_at: new Date().toISOString(), category:'명소' }
      ]
    } finally {
      loading.value = false
    }
  }

  return { posts, loading, error, loadRecent, loadTopByViews }
}