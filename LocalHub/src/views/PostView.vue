<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const id = route.params.id

const post = ref({
  id: id,
  tag: '관광지',
  author: '익명의 작성자',
  date: '2026-07-14 10:30',
  title: '로컬 예시 게시글 제목',
  content: `<p>여기에 게시글 본문이 들어갑니다. 제공된 JSON/DB에서 불러온 HTML 또는 마크다운을 렌더하세요.</p>
            <p>위치, 연락처, 팁 등 상세 내용을 여기에 배치합니다.</p>`,
  views: 129,
  likes: 24
})

const loading = ref(false)

const tagIcons = {
  '관광지': '📍',
  '맛집': '🍽️',
  '축제행사': '🎉',
  '꿀팁정보': '💡'
}

const tagIcon = computed(() => tagIcons[post.value.tag] ?? '🔖')

async function loadPost() {
  loading.value = true
  try {
    const res = await fetch(`/api/posts/${id}`)
    if (!res.ok) {
      throw new Error('포스트를 불러오지 못했습니다.')
    }
    const data = await res.json()
    post.value = {
      id: data.id,
      tag: data.category || '기타',
      author: data.author || '익명의 작성자',
      date: data.created_at || '',
      title: data.title || '',
      content: data.content || '',
      views: data.views || 0,
      likes: data.likes || 0
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}
async function doLike(){
  try {
    const res = await fetch(`/api/posts/${id}/like`, { method: 'POST' })
    if (!res.ok) throw new Error('좋아요 실패')
    const data = await res.json()
    post.value.likes = data.likes
  } catch (e) {
    alert('좋아요 실패: ' + e.message)
  }
}

function goBack(){
  const cat = route.query.category || post.value.tag || '전체'
  if (cat && cat !== '전체') {
    router.push({ name: 'board', params: { category: cat } })
  } else {
    router.push({ name: 'board' })
  }
}

function onEdit(){
  router.push({ name: 'new', query: { id: post.value.id } })
}

async function onDelete(){
  const pwd = prompt('삭제하려면 비밀번호를 입력하세요.')
  if (!pwd) return
  if (!confirm('정말 삭제하시겠습니까?')) return

  try {
    const res = await fetch(`/api/posts/${id}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: pwd })
    })
    if (!res.ok) {
      const txt = await res.text()
      throw new Error(txt || `삭제 실패 (${res.status})`)
    }
    alert('삭제되었습니다.')
    const returnCat = route.query.category || post.value.tag || '전체'
    if (returnCat && returnCat !== '전체') {
      router.push({ name: 'board', params: { category: returnCat } })
    } else {
      router.push({ name: 'board' })
  }
  } catch (e) {
    alert('삭제 중 오류: ' + e.message)
  }
}

onMounted(loadPost)
</script>

<template>
  <section class="post-detail">
    <div class="container">
      <router-link
        class="back"
        :to="(route.query.category && route.query.category !== '') ? { name: 'board', params: { category: route.query.category } } : { name: 'board' }"
      >
        ← 목록으로 돌아가기
      </router-link>
      <article class="card">
        <header class="card-header">
          <span :class="['tag', `tag-${post.tag}`]">
            <span class="tag-icon">{{ tagIcon }}</span>
            <span class="tag-label">{{ post.tag }}</span>
          </span>

          <div class="meta">
            <span class="author">{{ post.author }}</span>
            <span>·</span>
            <span class="date">{{ post.date }}</span>
          </div>
        </header>

        <h1 class="title">{{ post.title }}</h1>

        <div class="content" v-html="post.content"></div>

        <footer class="card-footer">
          <div class="stats">
            <span class="views">👁 조회 {{ post.views }}</span>
            <button class="likes btn" @click="doLike">❤ {{ post.likes }}</button>
          </div>

          <div class="actions">
            <button class="btn edit" @click="onEdit">수정</button>
            <button class="btn danger" @click="onDelete">삭제</button>
          </div>
        </footer>
      </article>
    </div>
  </section>
</template>

<style scoped>
.post-detail { padding: 28px 16px; background: #f8fafc; min-height: calc(100vh - 80px); }
.container { max-width: 1000px; margin: 0 auto; }

.back { background: transparent; border: none; color:#3b82f6; cursor:pointer; margin-bottom:12px; font-size:14px }

.card {
  background: #fff;
  border-radius:16px;
  padding:24px;
  border:1px solid #eef2f7;
  box-shadow: 0 20px 40px rgba(13,20,40,0.04);
}

.card-header { display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:12px; }

/* tag base */
.tag {
  display:inline-flex;
  align-items:center;
  gap:8px;
  padding:6px 10px;
  border-radius:8px;
  font-weight:700;
  font-size:13px;
  color:#fff;
}
.tag-icon { font-size:16px; line-height:1; }
.tag-label { display:inline-block; }

/* 색상 매핑 (BoardPage와 동일하게 유지) */
.tag-관광지 { background:#ff7ab6; }
.tag-맛집 { background:#7dd3fc; color:#03324b; }
.tag-축제행사 { background:#fbd38d; color:#5a3b00; }
.tag-꿀팁정보 { background:#c4b5fd; color:#2b1750; }

.meta { color:#6b7280; font-size:13px; display:flex; gap:8px; align-items:center; }

.title { margin:6px 0 16px; font-size:26px; color:#0f172a; line-height:1.2; }

.content { color:#374151; line-height:1.7; font-size:16px; margin-bottom:18px; }
.content p { margin:12px 0; }

.card-footer { display:flex; justify-content:space-between; align-items:center; gap:12px; border-top:1px solid #f1f5f9; padding-top:14px; }
.stats { color:#6b7280; display:flex; gap:16px; font-size:14px; }
.actions { display:flex; gap:8px; }
.btn { padding:8px 12px; border-radius:8px; border:1px solid #e6e9ef; cursor:pointer; background:#fff; }
.btn.edit { background: #fff; color:#0b76ef; border-color:#dbeafe; }
.btn.danger { background:#fff5f5; color:#b91c1c; border-color:#fecaca; }
.back { position: relative; z-index: 9999; pointer-events: auto; }
@media (max-width:700px){
  .title { font-size:20px; }
  .card { padding:16px; border-radius:12px; }
}
</style>