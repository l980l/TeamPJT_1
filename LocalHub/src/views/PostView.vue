<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const id = route.params.id

const loading = ref(true)
const post = ref(null)
const related = ref([])

async function fetchPost() {
  loading.value = true
  try {
    const res = await fetch(`/api/posts/${id}`)
    if (!res.ok) throw new Error('포스트를 불러오지 못했습니다.')
    const data = await res.json()
    post.value = {
      id: data.id,
      category: data.category || '기타',
      author: data.author || '익명의 작성자',
      created_at: data.created_at || '',
      title: data.title || '',
      content: data.content || '', // 서버에서 HTML 반환 권장
      views: data.views ?? 0,
      likes: data.likes ?? 0,
      place: data.place || null
    }
  } catch (e) {
    console.error(e)
    post.value = null
  } finally {
    loading.value = false
  }
}

async function fetchRelated() {
  if (!post.value || !post.value.category) return
  try {
    const res = await fetch(`/api/posts?category=${encodeURIComponent(post.value.category)}&limit=5`)
    if (res.ok) related.value = await res.json()
  } catch (e) { console.error(e) }
}

function goBack() {
  const cat = route.query.category || ''
  router.push({ name: 'board', params: { category: cat || '' } })
}

async function onLike() {
  try {
    const res = await fetch(`/api/posts/${id}/like`, { method: 'POST' })
    if (!res.ok) throw new Error('like failed')
    const data = await res.json()
    post.value.likes = data.likes ?? post.value.likes + 1
  } catch (e) {
    alert('좋아요 처리 오류')
  }
}

function onEdit() {
  router.push({ name: 'new', query: { id: post.value.id } })
}

async function onDelete() {
  const pwd = prompt('삭제 비밀번호를 입력하세요')
  if (!pwd) return
  if (!confirm('정말 삭제하시겠습니까?')) return
  try {
    const res = await fetch(`/api/posts/${id}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: pwd })
    })
    if (!res.ok) throw new Error('삭제 실패')
    alert('삭제되었습니다')
    goBack()
  } catch (e) {
    alert('삭제 오류: ' + e.message)
  }
}

onMounted(async () => {
  await fetchPost()
  if (post.value) await fetchRelated()
})
</script>

<template>
  <section class="post-page">
    <div class="container">
      <div class="post-top-nav">
        <router-link to="/" class="top-link top-left">홈으로</router-link>
        <router-link :to="{ name: 'board', params: { category: '' } }" class="top-link top-right">게시글 목록보기</router-link>
      </div>

      <section v-if="loading" class="loading">로딩 중…</section>

      <article v-else-if="post" class="post-card">
        <header class="post-band">
          <div class="band-left">
            <a class="crumb" @click.prevent="goBack">← 게시판 목록</a>
            <div class="band-cat">{{ post.category }}</div>
            <h1 class="band-title">{{ post.title }}</h1>
            <div class="band-meta">
              <span>📅 {{ new Date(post.created_at).toLocaleDateString() }}</span>
              <span>👁 {{ post.views }}</span>
              <span>❤️ {{ post.likes }}</span>
            </div>
          </div>
        </header>

        <div class="wrap">
          <div class="content-card">
            <div class="content-body" v-html="post.content"></div>

            <a v-if="post.place" class="place-link" :href="post.place.url" target="_blank" rel="noopener">
              <span class="place-link__icon">📍</span>
              <span class="place-link__txt">
                <span class="place-link__name">{{ post.place.name }}</span>
                <span class="place-link__hint">{{ post.place.address }}</span>
              </span>
              <span class="place-link__arrow">→</span>
            </a>

            <div class="actions">
              <button class="btn-like" @click="onLike">❤️ 좋아요 {{ post.likes }}</button>
              <div class="actions__right">
                <button class="btn" @click="onEdit">수정</button>
                <button class="btn btn--danger" @click="onDelete">삭제</button>
              </div>
            </div>
          </div>

          <section class="related" v-if="related.length">
            <h3 class="related__title">같은 카테고리의 다른 글</h3>
            <div class="related__list">
              <router-link v-for="r in related" :key="r.id" :to="{ name: 'post', params: { id: r.id } }"
                class="related__row">
                <span class="related__tag">{{ r.category }}</span>
                <span class="related__name">{{ r.title }}</span>
                <span class="related__date">{{ new Date(r.created_at).toLocaleDateString() }}</span>
              </router-link>
            </div>
          </section>
        </div>
      </article>

      <div v-else class="notfound">게시글을 찾을 수 없습니다.</div>
    </div>
  </section>
</template>

<style scoped>
.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 18px;
}

.back {
  background: transparent;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  margin-bottom: 12px;
}

.post-card {
  background: #fff;
  border-radius: 14px;
  padding: 18px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

.band-title {
  font-size: 22px;
  margin: 8px 0;
}

.content-card {
  margin-top: 12px;
  background: #fff;
  padding: 18px;
  border-radius: 12px;
}

.content-body {
  line-height: 1.8;
  color: #333;
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #eee;
}

.btn-like {
  border: 1px solid #f2c7bd;
  background: #fff;
  padding: 8px 12px;
  border-radius: 18px;
  color: #ee7a52;
  cursor: pointer;
}

.actions__right .btn {
  margin-left: 8px;
}

.related__list {
  margin-top: 12px;
  border: 1px solid #f0f0f5;
  border-radius: 10px;
  overflow: hidden;
}

.related__row {
  display: flex;
  gap: 10px;
  padding: 12px;
  border-bottom: 1px solid #f0f0f5;
  text-decoration: none;
  color: inherit;
}

.related__row:last-child {
  border-bottom: none;
}

.post-top-nav {
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  margin-bottom:10px;
}
.top-link {
  font-size:14px;
  color:var(--accent, #6b78e8);
  text-decoration:none;
  padding:6px 10px;
  border-radius:8px;
  transition: background .12s, color .12s;
}
.top-link:hover {
  background: rgba(107,120,232,0.08);
  color: var(--accent-border, #4a5fe0);
}
.top-left { justify-self:flex-start; }
.top-right { justify-self:flex-end; }
</style>