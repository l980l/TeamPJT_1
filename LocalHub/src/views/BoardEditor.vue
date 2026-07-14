<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const id = route.query.id || null

const categories = ['관광지','맛집','축제행사','꿀팁정보']

const category = ref(route.query.category || categories[0])
const title = ref('')
const content = ref('')
const password = ref('') // 평문 (요구사항)
const loading = ref(false)
const error = ref('')
const info = ref('')

async function loadExisting(){
  if (!id) return
  loading.value = true
  try {
    const res = await fetch(`/api/boards/${id}`)
    if (!res.ok) {
      error.value = '게시글을 불러오지 못했습니다.'
      return
    }
    const data = await res.json()
    category.value = data.category || category.value
    title.value = data.title || ''
    content.value = data.content || ''
    // 서버가 비밀번호를 반환하지 않는 것이 정상입니다.
    info.value = '수정하려면 비밀번호를 입력하세요.'
  } catch (e) {
    error.value = '데이터 로드 중 오류'
  } finally {
    loading.value = false
  }
}

async function submit(){
  error.value = ''
  info.value = ''
  if (!title.value.trim()) { error.value = '제목을 입력하세요.'; return }
  if (!content.value.trim()) { error.value = '내용을 입력하세요.'; return }
  if (!password.value) { error.value = '수정/삭제용 비밀번호를 반드시 설정하세요.'; return }

  loading.value = true
  try {
    if (id) {
      // 수정: 비밀번호 포함하여 PUT 요청 (백엔드에서 비밀번호 비교 후 허용)
      const res = await fetch(`/api/boards/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category: category.value,
          title: title.value,
          content: content.value,
          password: password.value
        })
      })
      if (!res.ok) {
        const txt = await res.text()
        throw new Error(txt || '수정 실패')
      }
      info.value = '수정되었습니다.'
      router.push({ name: 'post', params: { id } })
    } else {
      // 생성: POST 요청
      const res = await fetch(`/api/boards`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category: category.value,
          title: title.value,
          content: content.value,
          password: password.value
        })
      })
      if (!res.ok) {
        const txt = await res.text()
        throw new Error(txt || '등록 실패')
      }
      const data = await res.json()
      info.value = '등록되었습니다.'
      const newId = data.id || null
      if (newId) router.push({ name: 'post', params: { id: newId } })
      else router.push({ name: 'board', params: { category: category.value === '전체' ? '' : category.value } })
    }
  } catch (e) {
    error.value = e.message || '요청 실패'
  } finally {
    loading.value = false
  }
}

onMounted(loadExisting)
</script>

<template>
  <main class="editor">
    <section class="card">
      <h2>{{ id ? '게시글 수정' : '새로운 정보 등록' }}</h2>

      <label class="label">정보 카테고리</label>
      <div class="category-row">
        <button
          v-for="c in categories"
          :key="c"
          :class="['cat', { active: c === category }]"
          @click="category = c"
        >{{ c }}</button>
      </div>

      <label class="label">글 제목</label>
      <input v-model="title" placeholder="예: 경복궁 근처 숨겨진 한옥카페 찾았습니다" />

      <label class="label">본문 내용</label>
      <textarea v-model="content" rows="8" placeholder="공유하고 싶은 상세 내용을 정성스럽게 기재해 주세요."></textarea>

      <label class="label">수정/삭제용 비밀번호</label>
      <input v-model="password" type="password" placeholder="비밀번호 설정 (숫자 4자리 권장)" />

      <div class="notes">
        <small>※ 비밀번호는 평문으로 전송됩니다(요구사항). 백엔드에서 안전하게 비교하세요.</small>
      </div>

      <div class="actions">
        <button @click="submit" :disabled="loading" class="primary">{{ loading ? '처리중...' : (id ? '수정하기' : '등록하기') }}</button>
        <button @click="$router.back()" class="ghost">취소</button>
      </div>

      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="info" class="info">{{ info }}</div>
    </section>
  </main>
</template>

<style scoped>
.editor { max-width:900px; margin:28px auto; padding:16px; }
.card { background:#fff; border-radius:12px; padding:20px; border:1px solid #eef2f7; box-shadow:0 8px 20px rgba(12,20,40,0.04); }
.label { display:block; margin:12px 0 6px; font-weight:700; color:#334155; }
input, textarea { width:100%; padding:10px 12px; border-radius:8px; border:1px solid #e6e9ef; }
.category-row { display:flex; gap:8px; margin-bottom:8px; flex-wrap:wrap; }
.cat { padding:8px 12px; border-radius:999px; border:1px solid #eef2f7; background:#fff; cursor:pointer; }
.cat.active { background: linear-gradient(180deg,#eef7ff,#e6f3ff); color:#0b76ef; border-color:#cfe9ff; font-weight:700; }
.actions { display:flex; gap:10px; margin-top:14px; }
.primary { background:#5b6cff; color:#fff; border:none; padding:10px 16px; border-radius:10px; cursor:pointer; }
.ghost { background:transparent; border:1px solid #eef2f7; padding:10px 16px; border-radius:10px; cursor:pointer; }
.notes { margin-top:8px; color:#64748b; font-size:13px; }
.error { margin-top:12px; color:#b91c1c; }
.info { margin-top:12px; color:#0b76ef; }
</style>