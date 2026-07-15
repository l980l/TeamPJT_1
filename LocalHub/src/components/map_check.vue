<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import L from 'leaflet'

// 카테고리 수를 prop으로 받을 수도 있고, 여기선 mock/ref 사용
// 필요하면 defineProps로 바꿔서 상위에서 전달하세요.
const categoryCount = ref(12) // 예: 12개

const router = useRouter()
const mapContainer = ref(null)
let mapInstance = null
let _resizeHandler = null
let _resizeObserver = null

onMounted(() => {
  if (!mapContainer.value) return

   // 지도 초기화
  mapInstance = L.map(mapContainer.value, { zoomControl: true }).setView([37.5665, 126.9780], 11)

  // 타일 레이어 추가
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(mapInstance)

  // 예시 마커
  L.marker([37.5665, 126.9780]).addTo(mapInstance).bindPopup('서울 중심')

  // 강제 리사이즈 함수
  const refresh = () => {
    if (mapInstance) {
      try { mapInstance.invalidateSize() } catch (e) { /* 안전 장치 */ }
    }
  }

  // 초기 렌더 안정화를 위해 whenReady + 여러 시차 호출
  mapInstance.whenReady(() => {
  refresh()
  setTimeout(refresh, 100)
  setTimeout(refresh, 500)
  setTimeout(refresh, 1000)
})

  // 윈도우 리사이즈에 대응
  _resizeHandler = () => refresh()
  window.addEventListener('resize', _resizeHandler)

  // 부모 레이아웃 변경(숨김→표시, flex/animation 등)에 더 잘 대응하려면 ResizeObserver 사용
  if (typeof ResizeObserver !== 'undefined') {
    // 참고: 파일 상단에 let _resizeObserver = null 추가 필요
    _resizeObserver = new ResizeObserver(() => refresh())
    _resizeObserver.observe(mapContainer.value)
  }
})

onBeforeUnmount(() => {
  if (_resizeHandler) window.removeEventListener('resize', _resizeHandler)
  if (_resizeObserver) {
    _resizeObserver.disconnect()
    _resizeObserver = null
  }
  if (mapInstance) {
    mapInstance.remove()
    mapInstance = null
  }
})

function goToFullMap() {
  router.push({ path: '/map' }) // 전체지도 라우트로 변경
}
</script>

<template>
  <div class="map-check">
    <div class="map-header">
      <button class="all-map-btn" @click="goToFullMap" aria-label="전체지도 보기">전체지도</button>
    </div>

    <div ref="mapContainer" class="map-container" role="region" aria-label="지도"></div>

    <p class="map-caption">
      지도에서 유형별로 필터링해 보세요.
    </p>
  </div>
</template>

<style scoped>
.map-check {
  margin: 20px;
  color: #fff;
}

.map-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.map-header h2 {
  font-size: 20px;
  margin: 0;
  text-align: left;
}

.all-map-btn {
  margin-left: auto;
  background: transparent;
  border: none;
  color: #4ea1ff;
  font-size: 14px;
  cursor: pointer;
  padding: 6px 8px;
}

.map-container {
  width: 100%;
  height: 360px; /* 필요시 조정 */
  border-radius: 8px;
  overflow: hidden;
  background: #eaeaea;
  margin-bottom: 10px;
  position: relative;
  display: block;
}

/* 캡션: 줄 바꿈 허용, 한 줄 넘어가면 다음 줄에 계속 */
.map-caption {
  color: #d0d6dd;
  font-size: 14px;
  line-height: 1.4;
  margin: 0;
}

/* 반응형: 모바일에서 지도 높이 축소 */
@media (max-width: 640px) {
  .map-container { height: 240px; }
  .all-map-btn { font-size: 13px; }
}
</style>