<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const id = route.query.id || null
const placeQuery = ref('')
const places = ref([])            // 검색 결과 목록
const selectedPlace = ref(null)   // 선택된 장소 object { contentid, title, addr1 }
const loadingPlaces = ref(false)
const categories = ['관광지','레포츠','문화시설','쇼핑','숙박','여행코스','축제공연행사']

const category = ref(route.query.category || categories[0])
const title = ref(route.query.title || '')
const content = ref('')
const password = ref('') // 평문 (요구사항)
const loading = ref(false)
const error = ref('')
const info = ref('')
// 서울 고정: 행정구(구/군) 목록만 관리
const selectedRegion = ref('서울특별시')
const districts = ref([])          // 예: ['강남구', '종로구', ...]
const selectedDistrict = ref('')
const selectedPlaceId = ref('') // select에서 contentid만 바인딩

// simple debounce helper
function debounce(fn, wait = 300) {
  let timer = null
  return (...args) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn(...args), wait)
  }
}

// debounced wrapper for loadPlaces (defined later, but wrapper can be created now)
let debouncedLoadPlaces = null

function onPlaceInput() {
  // placeQuery is v-model bound
  if (!placeQuery.value || placeQuery.value.trim() === '') {
    places.value = []
    return
  }
  if (!debouncedLoadPlaces) {
    debouncedLoadPlaces = debounce((q) => loadPlaces(q, category.value, selectedRegion.value, selectedDistrict.value), 300)
  }
  debouncedLoadPlaces(placeQuery.value)
}

async function loadExisting(){
  if (!id) return
  loading.value = true
  try {
    const res = await fetch(`/api/posts/${id}`)
    if (!res.ok) {
      error.value = '게시글을 불러오지 못했습니다.'
      return
    }
    const data = await res.json()
    category.value = data.category || category.value
    title.value = data.title || ''
    content.value = data.content || ''
    // 복원 (백엔드가 place_* 필드 반환한다고 가정)
    if (data.place_contentid) {
      selectedPlace.value = {
        contentid: data.place_contentid,
        title: data.place_title,
        addr: data.place_addr
      }
      placeQuery.value = selectedPlace.value.title
    }
    // 서버가 비밀번호를 반환하지 않는 것이 정상입니다.
    info.value = '수정하려면 비밀번호를 입력하세요.'
  } catch (e) {
    error.value = '데이터 로드 중 오류'
  } finally {
    loading.value = false
  }
}

async function loadRegionDistrictLists() {
  try {
    const res = await fetch(`/api/items?limit=1000`)
    if (!res.ok) { districts.value = []; return }
    const data = await res.json()
    const set = new Set()
    const re = /서울[^\s,]*\s*([^\s,]+(?:구|군))/i

    data.forEach(it => {
      const raw = (it.addr1 || it.addr2 || it.region || '').replace(/[,\(\)]/g,'').trim()
      if (!raw) return
      const m = raw.match(re)
      if (m && m[1]) { set.add(m[1].trim()); return }
      const parts = raw.split(/\s+/)
      if (parts.length >= 2) {
        const candidate = parts[1].trim()
        if (/(구|군)$/.test(candidate)) set.add(candidate)
      }
    })

    districts.value = Array.from(set).sort()
    selectedDistrict.value = districts.value.length ? districts.value[0] : ''
  } catch (e) {
    districts.value = []
    selectedDistrict.value = ''
    console.error('loadRegionDistrictLists error', e)
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
      const res = await fetch(`/api/posts/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category: category.value,
          title: title.value,
          content: content.value,
          password: password.value,
          place_contentid: selectedPlace.value ? selectedPlace.value.contentid : null,
          place_title:     selectedPlace.value ? selectedPlace.value.title     : null,
          place_addr:      selectedPlace.value ? selectedPlace.value.addr      : null
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
      const res = await fetch(`/api/posts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category: category.value || '관광지',
          title: title.value,
          content: content.value,
          edit_password: password.value,
          place_contentid: selectedPlace.value ? selectedPlace.value.contentid : null,
          place_title:     selectedPlace.value ? selectedPlace.value.title     : null,
          place_addr:      selectedPlace.value ? selectedPlace.value.addr      : null
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

async function loadPlaces(q = '', cat = '', region = '', district = '') {
  loadingPlaces.value = true
  try {
    const params = new URLSearchParams({ q: q || '', limit: 50 })
    const categoryToUse = (cat || category.value) || ''
    if (categoryToUse && categoryToUse !== '전체') params.set('category', categoryToUse)
    if (region || selectedRegion.value) params.set('region', region || selectedRegion.value)
    if (district || selectedDistrict.value) params.set('district', district || selectedDistrict.value)
    const res = await fetch(`/api/items?${params.toString()}`)
    if (!res.ok) { places.value = []; return }
    const data = await res.json()
    places.value = data.map(it => ({
      contentid: it.contentid,
      title: it.title,
      addr: it.addr1 || it.addr2 || ''
    }))
  } catch (e) {
    places.value = []
  } finally {
    loadingPlaces.value = false
  }
}

function selectPlace(p) {
  selectedPlace.value = p
  selectedPlaceId.value = p.contentid
  placeQuery.value = p.title
  // places는 지우지 않아서 select 박스는 계속 보입니다
}

// 카테고리 바뀌면 장소 선택 초기화
watch(category, async () => {
  selectedPlace.value = null
  placeQuery.value = ''
  places.value = []
  selectedPlaceId.value = ''
  // 카테고리 변경 시 행정구 목록 갱신
  await loadRegionDistrictLists(category.value)
  // 그리고 새 카테고리 기준으로 장소 목록도 로드
  await loadPlaces('', category.value, selectedRegion.value, selectedDistrict.value)
})

watch(selectedDistrict, async (v) => {
  selectedPlace.value = null
  selectedPlaceId.value = ''
  placeQuery.value = ''
  places.value = []
  // 구가 비어있어도(전체 선택) 해당 카테고리/지역 기준으로 장소 로드
  await loadPlaces('', category.value, selectedRegion.value, v || '')
})

onMounted(async () => {
  await loadRegionDistrictLists()
  // 초기 장소 리스트(구 선택 전 전체/카테고리 기준)를 미리 로드
  await loadPlaces('', category.value, selectedRegion.value, selectedDistrict.value)
  loadExisting()
})
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

      <label class="label">행정구 · 장소 선택 (선택)</label>
      <div class="inline-row">
        <select v-model="selectedDistrict"
                @change="() => loadPlaces(placeQuery, category.value, selectedRegion, selectedDistrict)">
          <option value="">전체</option>
          <option v-for="d in districts" :key="d" :value="d">{{ d }}</option>
        </select>

        <select v-if="places.length"
                v-model="selectedPlaceId"
                @change="() => {
                  const p = places.find(x => x.contentid === selectedPlaceId)
                  if (p) selectPlace(p)
                }">
          <option value="">선택하세요</option>
          <option v-for="p in places" :key="p.contentid" :value="p.contentid">
            {{ p.title }} — {{ p.addr }}
          </option>
        </select>
      </div>

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
.editor {
  box-sizing: border-box;
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 24px;
}
.card {
  width: 100%;
  max-width: none;
  border-radius: 12px;
}
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
.place-list { list-style:none; padding:6px; margin:6px 0 0; border:1px solid #eef2f7; max-height:220px; overflow:auto; background:#fff; border-radius:8px; }
.place-list li { padding:8px; cursor:pointer; border-bottom:1px solid #f3f5f8; }
.place-list li:last-child { border-bottom: none; }
.place-list li:hover { background:#f6f9ff; }
.selected-place { margin-top:8px; font-size:13px; color:#334155; display:flex; gap:8px; align-items:center; }
</style>