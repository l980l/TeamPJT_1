<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const id = computed(() => route.params.id)

const loading = ref(true)
const post = ref(null)
const related = ref([])

const tagIcons = {
  '관광지': '📍',
  '레포츠': '🏄‍♂️',
  '문화시설': '🏛️',
  '쇼핑': '🛍️',
  '숙박': '🏨',
  '여행코스': '🗺️',
  '축제공연행사': '🎉'
}
const tagIcon = computed(() => tagIcons[post.value?.category] ?? '🔖')

async function fetchPost() {
  loading.value = true
  try {
    const res = await fetch(`/api/posts/${id.value}`)
    if (!res.ok) throw new Error('포스트를 불러오지 못했습니다.')
    const data = await res.json()
    post.value = {
      id: data.id,
      category: data.category || '기타',
      author: data.author || '익명의 작성자',
      created_at: data.created_at || '',
      title: data.title || '',
      content: data.content ?? '', // 서버에서 HTML 반환 권장
      views: data.views ?? 0,
      likes: data.likes ?? 0,
      place: data.place ?? null,
      placeTitle: data.place_title || null,
      placeAddr: data.place_addr || null
    }
  } catch (e) {
    console.error(e)
    post.value = null
  } finally {
    loading.value = false
  }
}

async function fetchRelated() {
  if (!post.value?.category) return
  try {
    const res = await fetch(`/api/posts?category=${encodeURIComponent(post.value.category)}&limit=5`)
    if (res.ok) related.value = await res.json()
  } catch (e) { console.error(e) }
}

function goBack() {
  const cat = route.query.category || post.value?.category || ''
  router.push({ name: 'board', params: { category: cat && cat !== '전체' ? cat : '' } })
}

async function onLike() {
  try {
    const res = await fetch(`/api/posts/${id.value}/like`, { method: 'POST' })
    if (!res.ok) throw new Error('좋아요 처리 실패')
    const data = await res.json()
    post.value.likes = data.likes ?? post.value.likes + 1
  } catch (e) {
    alert('좋아요 처리 오류: ' + e.message)
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
    const res = await fetch(`/api/posts/${id.value}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: pwd })
    })
    if (!res.ok) {
      const txt = await res.text()
      throw new Error(txt || `삭제 실패 (${res.status})`)
    }
    alert('삭제되었습니다.')
    goBack()
  } catch (e) {
    alert('삭제 오류: ' + e.message)
  }
}

onMounted(async () => {
  await fetchPost()
  if (post.value) await fetchRelated()
})

watch(id, async (newId, oldId) => {
  if (!newId || newId === oldId) return
  await fetchPost()
  if (post.value) await fetchRelated()
})
</script>

<template>
  <section class="post-page">
    <div class="container">
      <div class="post-top-nav">
        <button class="top-link top-left" @click="$router.back()">‹ 뒤로</button>
        <router-link to="/" class="top-link top-right">홈으로</router-link>
      </div>

      <section v-if="loading" class="loading">로딩 중…</section>

      <article v-else-if="post" class="post-card">
        <header class="post-band">
          <div class="band-left">
            <div :class="['band-cat', `tag-${post.category}`]">{{ tagIcon }} {{ post.category }}</div>
            <h1 class="band-title">{{ post.title }}</h1>
            <div class="band-meta">
              <span>📅 {{ new Date(post.created_at).toLocaleDateString() }}</span>
              <span class="meta-dot">·</span>
              <span>👁 {{ post.views }}</span>
              <span class="meta-dot">·</span>
              <span>❤ {{ post.likes }}</span>
            </div>
          </div>
        </header>

        <div v-if="post.placeTitle" class="place-info">
          <strong>장소: </strong>
          <span class="place-name">{{ post.placeTitle }}</span>
          <span v-if="post.placeAddr" class="place-addr"> — {{ post.placeAddr }}</span>
        </div>
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
                <span :class="['related__tag', `tag-${r.category}`]">{{ r.category }}</span>
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
.post-page {
  background: #f7f7fb;
  min-height: calc(100vh - 56px);
  padding: 32px 16px 60px;
  box-sizing: border-box;
  text-align: left;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0;
}

.post-top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.top-link {
  font-family: inherit;
  font-size: 13.5px;
  font-weight: 600;
  color: #4b3f9e;
  text-decoration: none;
  padding: 8px 14px;
  border-radius: 999px;
  background: #fff;
  border: 1px solid #eef2f7;
  cursor: pointer;
  transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease;
}

.top-link:hover {
  border-color: #d9ddff;
  box-shadow: 0 6px 16px rgba(75, 63, 158, 0.12);
  transform: translateY(-1px);
}

.loading,
.notfound {
  text-align: center;
  padding: 60px 0;
  color: #9aa4ad;
  background: #fff;
  border-radius: 16px;
  border: 1px solid #eef2f7;
}

.post-card {
  background: #fff;
  border-radius: 18px;
  padding: 0;
  overflow: hidden;
  border: 1px solid #eef2f7;
  box-shadow: 0 16px 40px rgba(20, 20, 43, 0.06);
}

.post-band {
  padding: 28px 28px 20px;
  border-bottom: 1px solid #f2f3f8;
}

.band-cat {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  background: #9aa0b3;
  margin-bottom: 10px;
}

.tag-관광지 { background: #ff7ab6; }
.tag-맛집 { background: #7dd3fc; color: #03324b; }
.tag-축제공연행사 { background: #fbd38d; color: #5a3b00; }
.tag-레포츠 { background: #7ee3b3; color: #063a2e; }
.tag-문화시설 { background: #c4b5fd; color: #2b1750; }
.tag-쇼핑 { background: #ffd166; color: #4b2e00; }
.tag-숙박 { background: #90cdf4; color: #02263a; }
.tag-여행코스 { background: #fbb6b6; color: #3b0f0f; }

.band-title {
  font-size: 26px;
  font-weight: 800;
  line-height: 1.45;
  letter-spacing: -0.01em;
  color: #1a1f2e;
  margin: 4px 0 12px;
}

.band-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #9aa0b3;
  font-size: 13px;
}

.meta-dot {
  color: #d7dae6;
}

.place-info {
  margin: 16px 28px 0;
  padding: 10px 14px;
  background: #f7f6ff;
  border: 1px solid #ece9ff;
  border-radius: 10px;
  font-size: 13.5px;
  color: #475569;
}

.place-name { font-weight: 700; color: #1a1f2e; }
.place-addr { color: #6b7280; margin-left: 6px; }

.wrap {
  padding: 24px 28px 28px;
}

.content-card {
  margin-top: 0;
  background: transparent;
  padding: 0;
  border-radius: 0;
}

.content-body {
  line-height: 1.9;
  font-size: 15.5px;
  color: #333c4d;
}

.place-link {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-top: 20px;
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid #eef2f7;
  background: #fafaff;
  text-decoration: none;
  color: inherit;
  transition: transform .14s ease, box-shadow .14s ease, border-color .14s ease;
}

.place-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 26px rgba(12, 20, 40, 0.08);
  border-color: #d9ddff;
}

.place-link__icon {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6b76ff, #4b3f9e);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.place-link__txt {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.place-link__name { font-weight: 700; color: #1a1f2e; }

.place-link__hint {
  font-size: 12.5px;
  color: #9aa0b3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.place-link__arrow { color: #4b3f9e; font-weight: 700; }

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding-top: 18px;
  border-top: 1px solid #f2f3f8;
}

.btn-like {
  border: 1px solid #f2c7bd;
  background: #fff5f2;
  padding: 10px 16px;
  border-radius: 999px;
  color: #ee7a52;
  font-weight: 700;
  cursor: pointer;
  transition: transform .12s ease, box-shadow .12s ease;
}

.btn-like:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(238, 122, 82, 0.18);
}

.actions__right {
  display: flex;
  gap: 8px;
}

.actions__right .btn {
  margin-left: 0;
  padding: 9px 16px;
  border-radius: 10px;
  border: 1px solid #eef2f7;
  background: #fff;
  color: #4b5563;
  font-weight: 600;
  cursor: pointer;
  transition: background .12s ease, border-color .12s ease;
}

.actions__right .btn:hover {
  background: #f7f7fb;
  border-color: #d9ddff;
}

.actions__right .btn--danger { color: #c0392b; }

.actions__right .btn--danger:hover {
  background: #fff5f4;
  border-color: #f3c9c2;
}

.related {
  margin-top: 28px;
}

.related__title {
  font-size: 15px;
  font-weight: 700;
  color: #1a1f2e;
  margin-bottom: 10px;
}

.related__list {
  margin-top: 0;
  border: 1px solid #f0f0f5;
  border-radius: 12px;
  overflow: hidden;
}

.related__row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 13px 14px;
  border-bottom: 1px solid #f0f0f5;
  text-decoration: none;
  color: inherit;
  transition: background .12s ease;
}

.related__row:hover {
  background: #fafaff;
}

.related__row:last-child {
  border-bottom: none;
}

.related__tag {
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 9px;
  border-radius: 999px;
  color: #fff;
  background: #9aa0b3;
}

.related__name {
  flex: 1 1 auto;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 600;
  color: #333c4d;
}

.related__date {
  flex-shrink: 0;
  font-size: 12px;
  color: #9aa0b3;
}

@media (max-width: 640px) {
  .post-page {
    padding: 16px 12px 40px;
  }

  .post-band {
    padding: 20px 18px 16px;
  }

  .wrap {
    padding: 18px;
  }

  .place-info {
    margin: 14px 18px 0;
  }

  .band-title {
    font-size: 20px;
  }

  .actions {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .actions__right .btn {
    flex: 1;
  }

  .related__row {
    flex-wrap: wrap;
  }
}
</style>