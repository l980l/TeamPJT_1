<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const mapContainer = ref(null)
let mapInstance = null
let markerLayers = []

const state = reactive({
    query: '',
    guChips: ['종로구', '중구', '용산구', '성동구', '광진구', '동대문구', '중랑구', '성북구', '강북구', '도봉구', '노원구', '은평구', '서대문구', '마포구', '양천구', '강서구', '구로구', '금천구', '영등포구', '동작구', '관악구', '서초구', '강남구', '송파구', '강동구'],
    selectedGus: [],
    categories: {
        관광지: false,
        레포츠: false,
        문화시설: false,
        쇼핑: false,
        숙박: false,
        여행코스: false,
        축제공연행사: false
    },
    resultsCount: 0,
    selectedPlace: null,
    popupVisible: false,
    popupLatLng: null
})

const COLORS = {
    관광지: '#2b7a5e',
    레포츠: '#2b62a8',
    문화시설: '#7a5a2b',
    쇼핑: '#a8462a',
    숙박: '#7d3a6a',
    여행코스: '#3f7d6a',
    축제공연행사: '#ee7a52'
}

function svgPin(color = '#888') {
    const svg = encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="28" height="36" viewBox="0 0 24 24" fill="${color}" stroke="white" stroke-width="1"><path d="M12 2C7.6 2 4 5.6 4 10c0 6 8 12 8 12s8-6 8-12c0-4.4-3.6-8-8-8Z"/><circle cx="12" cy="10" r="3" fill="white"/></svg>`)
    return L.divIcon({
        className: 'pin',
        html: `<img src="data:image/svg+xml;utf8,${svg}" style="display:block">`,
        iconSize: [28, 36],
        iconAnchor: [14, 36]
    })
}

function clearMarkers() {
    markerLayers.forEach(m => {
        try { mapInstance.removeLayer(m) } catch (e) { }
    })
    markerLayers = []
}

function buildQueryParams() {
    const params = new URLSearchParams()
    if (state.query) params.append('q', state.query)
    if (state.selectedGus.length) params.append('gu', state.selectedGus.join(','))
    const cats = Object.keys(state.categories).filter(k => state.categories[k])
    if (cats.length) params.append('categories', cats.join(','))
    return params.toString()
}

async function fetchLocations() {
    const qs = buildQueryParams()
    const url = `/api/locations${qs ? '?' + qs : ''}`
    try {
        const res = await fetch(url)
        if (!res.ok) throw new Error('fetch failed')
        const data = await res.json()
        state.resultsCount = data.length || 0
        renderMarkers(data)
    } catch (e) {
        console.error(e)
    }
}

function renderMarkers(items = []) {
    clearMarkers()
    items.forEach(it => {
        const lat = parseFloat(it.mapy), lng = parseFloat(it.mapx)
        if (!lat || !lng) return
        const cat = it.contentType || '기타'
        const icon = svgPin(COLORS[cat] || '#888')
        const marker = L.marker([lat, lng], { icon }).addTo(mapInstance)
        marker.on('click', async () => { await openLocationDetail(it.contentid, [lat, lng]) })
        markerLayers.push(marker)
    })
    if (items.length) {
        const first = items.find(i => i.mapy && i.mapx)
        if (first) mapInstance.setView([first.mapy, first.mapx], 13)
    }
}

async function openLocationDetail(contentid, latlng) {
    try {
        const res = await fetch(`/api/locations/${encodeURIComponent(contentid)}`)
        if (!res.ok) throw new Error('not found')
        const data = await res.json()
        state.selectedPlace = data
        state.popupLatLng = latlng
        state.popupVisible = true
        if (latlng && mapInstance) mapInstance.panTo(latlng, { animate: true })
    } catch (e) { console.error(e) }
}

function closePopup() {
    state.popupVisible = false
    state.selectedPlace = null
    state.popupLatLng = null
}

/* 자치구 추가: select에서 값 고르면 selectedGus에 추가(중복 방지) */
function addGu(evt) {
    const val = evt.target.value
    if (!val || val === '__none') return
    if (!state.selectedGus.includes(val)) state.selectedGus.push(val)
    evt.target.value = '__none'
}

/* 태그 삭제 (x 클릭) */
function removeGu(idx) {
    state.selectedGus.splice(idx, 1)
}

onMounted(() => {
    mapInstance = L.map(mapContainer.value, { zoomControl: true }).setView([37.5665, 126.9780], 12)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OpenStreetMap contributors' }).addTo(mapInstance)
    const refresh = () => { try { mapInstance.invalidateSize() } catch (_) { } }
    mapInstance.whenReady(() => { refresh(); setTimeout(refresh, 100); setTimeout(refresh, 500) })
    window.addEventListener('resize', refresh)
})

onBeforeUnmount(() => {
    try { clearMarkers(); mapInstance.remove() } catch (_) { }
})
</script>

<template>
    <section class="map-shell">
        <div ref="mapContainer" id="map" class="map-main" role="region" aria-label="지도"></div>

        <aside class="panel">
            <div class="panel__title">🔎 원하는 지역·장소 찾기</div>

            <div class="panel__label">검색</div>
            <input v-model="state.query" placeholder="키워드, 단어를 입력해주세요" class="search-input" aria-label="장소 검색" />

            <div class="panel__label">지역 (자치구)</div>
            <select @change="addGu" aria-label="자치구 선택">
                <option value="__none" selected>자치구 선택</option>
                <option v-for="c in state.guChips" :key="c" :value="c">{{ c }}</option>
            </select>

            <div class="selected-tags" v-if="state.selectedGus.length">
                <button v-for="(g, idx) in state.selectedGus" :key="g" class="tag" @click="removeGu(idx)"
                    aria-label="자치구 삭제">
                    <span class="tag-x">✕</span><span class="tag-label">{{ g }}</span>
                </button>
            </div>

            <div class="panel__label">카테고리</div>
            <div class="cat-grid">
                <label class="cat-toggle" :class="{ on: state.categories.관광지 }"
                    @click.prevent="state.categories.관광지 = !state.categories.관광지">
                    <span class="dot" style="background:#2b7a5e"></span>관광지
                </label>
                <label class="cat-toggle" :class="{ on: state.categories.레포츠 }"
                    @click.prevent="state.categories.레포츠 = !state.categories.레포츠">
                    <span class="dot" style="background:#2b62a8"></span>레포츠
                </label>
                <label class="cat-toggle" :class="{ on: state.categories.문화시설 }"
                    @click.prevent="state.categories.문화시설 = !state.categories.문화시설">
                    <span class="dot" style="background:#7a5a2b"></span>문화시설
                </label>
                <label class="cat-toggle" :class="{ on: state.categories.쇼핑 }"
                    @click.prevent="state.categories.쇼핑 = !state.categories.쇼핑">
                    <span class="dot" style="background:#a8462a"></span>쇼핑
                </label>
                <label class="cat-toggle" :class="{ on: state.categories.숙박 }"
                    @click.prevent="state.categories.숙박 = !state.categories.숙박">
                    <span class="dot" style="background:#7d3a6a"></span>숙박
                </label>
                <label class="cat-toggle" :class="{ on: state.categories.여행코스 }"
                    @click.prevent="state.categories.여행코스 = !state.categories.여행코스">
                    <span class="dot" style="background:#3f7d6a"></span>여행코스
                </label>
                <label class="cat-toggle" :class="{ on: state.categories.축제공연행사 }"
                    @click.prevent="state.categories.축제공연행사 = !state.categories.축제공연행사">
                    <span class="dot" style="background:#ee7a52"></span>축제공연행사
                </label>
            </div>

            <button class="panel__submit" @click="fetchLocations">검색 결과 보기</button>
            <p class="panel__count">현재 지도에 표시된 장소 · {{ state.resultsCount }}곳</p>
        </aside>

        <aside v-if="state.popupVisible && state.selectedPlace" class="place-pop" style="left:20px;bottom:20px">
            <div class="place-pop__img">
                <img :src="state.selectedPlace.firstimage || '/default_place.jpg'" alt="img" />
                <div class="place-pop__badge">{{ state.selectedPlace.contentType || '' }}</div>
                <button class="place-pop__close" @click="closePopup">✕</button>
            </div>
            <div class="place-pop__body">
                <div class="place-pop__name">{{ state.selectedPlace.title }}</div>
                <div class="place-pop__addr">📍 {{ state.selectedPlace.addr1 }}</div>

                <div class="place-pop__rel-title">이 장소를 언급한 게시글</div>
                <template v-if="(state.selectedPlace.related_posts || []).length">
                    <a v-for="p in state.selectedPlace.related_posts" :key="p.id" :href="`/post/${p.id}`"
                        class="rel-item">
                        <span class="rel-item__dot">·</span>
                        <span class="rel-item__title">{{ p.title }}</span>
                        <span class="rel-item__meta">👁 {{ p.views ?? 0 }}</span>
                    </a>
                </template>
                <div v-else class="rel-item" style="padding:8px 0;color:#999">관련 게시글이 없습니다</div>

                <a class="place-pop__write" :href="`/new?title=${encodeURIComponent(state.selectedPlace.title)}`">＋ 이
                    장소로 게시글
                    작성하기</a>
            </div>
        </aside>
    </section>
</template>

<style scoped>
:root {
    --coral: #ee7a52;
    --coral-soft: #f2946f;
    --submit-color: #ff7e5f;
    --purple: #4b3f9e;
    --purple-soft: #6b78e8;
    --ink: #2b2b3a;
    --ink-soft: #6b6b7b;
    --ink-faint: #a6a6b4;
    --line: #ececf1;
    --page: #f6f6fb;
    --card: #fff;
    --font: 'Pretendard', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue';
}

.map-shell {
    position: relative;
    height: calc(100vh - 56px);
    background: var(--page);
    font-family: var(--font);
}

.map-main {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
}

/* panel (right) - 흰 배경 + 연한 테두리 */
.panel {
    position: absolute;
    top: 20px;
    right: 20px;
    z-index: 600;
    width: 320px;
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 12px 36px rgba(40, 30, 90, 0.08);
    padding: 16px;
    max-height: calc(100% - 40px);
    overflow-y: auto;
    border: 1px solid var(--line);
}

.panel__title {
    font-size: 15px;
    font-weight: 700;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
    text-align: left;
}

.panel__label {
    font-size: 12.5px;
    font-weight: 600;
    color: var(--ink-soft);
    margin-bottom: 8px;
    text-align: left;
}

/* inputs/selects: 연한 테두리 유지, 너비 가득 채움 */
.panel input,
.panel select {
    width: 100%;
    border: 1px solid var(--line);
    border-radius: 9px;
    padding: 10px 12px;
    font-family: inherit;
    font-size: 13px;
    color: var(--ink);
    background: #fff;
    margin-bottom: 12px;
    box-sizing: border-box;
}

/* 검색 input이 박스 길이에 맞게 확장하도록 수정 */
.search-input {
    width: 100%;
    display: block;
    box-sizing: border-box;
    border: none;
    outline: none;
    font-size: 14px;
    padding: 0;
}

/* selected tags */
.selected-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 12px;
}

.tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 10px;
    border-radius: 16px;
    background: #f7f5ff;
    border: 1px solid var(--line);
    color: var(--purple);
    font-weight: 600;
    cursor: pointer;
}

.tag-x {
    color: var(--purple);
    font-weight: 700;
    margin-right: 6px;
    background: transparent;
    border: none;
}

/* categories */
.cat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 7px;
    margin-bottom: 12px;
}

.cat-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12.5px;
    cursor: pointer;
    border: 1px solid var(--line);
    border-radius: 9px;
    padding: 8px 10px;
    background: #fff;
    color: var(--ink-soft);
    user-select: none;
    justify-content: flex-start;
    text-align: left;
}

.cat-toggle.on {
    border-color: currentColor;
    font-weight: 600;
    background: #faf9ff;
    color: inherit;
}

.cat-toggle .dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    flex-shrink: 0;
}

/* 검색 버튼 — 지정 색상 (#ff7e5f) */
.panel__submit {
    width: 100%;
    border: none;
    background: #ee7a52;
    color: #fff;
    font-family: inherit;
    font-size: 14px;
    font-weight: 600;
    padding: 12px;
    border-radius: 11px;
    cursor: pointer;
    margin-top: 6px;
    box-shadow: 0 8px 18px rgba(16, 24, 40, 0.08);
}

/* count */
.panel__count {
    text-align: center;
    font-size: 12px;
    color: var(--ink-faint);
    margin-top: 10px;
}

/* place popup */
.place-pop {
    position: absolute;
    z-index: 700;
    width: 300px;
    background: var(--card);
    border-radius: 16px;
    box-shadow: 0 12px 36px rgba(40, 30, 90, 0.16);
    overflow: hidden;
    border: 1px solid var(--line);
}

.place-pop__img {
    height: 140px;
    position: relative;
    background: linear-gradient(135deg, #cfd3f2, #e6dcf0);
}

.place-pop__img img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}

.place-pop__badge {
    position: absolute;
    top: 12px;
    left: 12px;
    font-size: 11px;
    font-weight: 600;
    color: #fff;
    background: rgba(43, 34, 60, 0.72);
    padding: 4px 10px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    gap: 4px;
}

.place-pop__badge::before {
    content: "📷";
}


.place-pop__close {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: #ffffff;
    color: #4b4b57;
    border: none;
    cursor: pointer;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 10px rgba(40, 30, 90, 0.2);
}

.place-pop__body {
    padding: 14px 16px 16px;
    background: white;
}

.place-pop__name {
    font-size: 18px;
    font-weight: 800;
    color: var(--ink);
    margin-bottom: 6px;
}

.place-pop__addr {
    font-size: 12.5px;
    color: var(--ink-soft);
    margin-bottom: 10px;
}

.place-pop__rel-title {
    font-size: 12px;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 8px;
    padding-top: 10px;
    border-top: 1px solid var(--line);
}

.rel-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
    font-size: 12.5px;
    color: var(--ink);
    text-decoration: none;
}

.rel-item:hover {
    color: var(--purple);
}

.rel-item__dot {
    color: var(--coral);
    font-weight: 700;
}

.rel-item__title {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.rel-item__meta {
    font-size: 11px;
    color: var(--ink-faint);
}

.place-pop__write {
    display: block;
    text-align: center;
    margin-top: 14px;
    font-size: 13px;
    font-weight: 700;
    color: var(--purple);
    background: #efeafb;
    border-radius: 14px;
    padding: 12px;
    text-decoration: none;
}

/* responsive */
@media (max-width:760px) {
    .panel {
        width: calc(100% - 40px);
        right: 10px;
        left: 10px;
        top: 14px;
        max-height: 40%;
        z-index: 1100;
    }

    .place-pop {
        width: calc(100% - 40px);
        left: 10px;
        bottom: 10px;
    }
}
</style>