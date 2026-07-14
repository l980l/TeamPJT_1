<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import L from 'leaflet'

// 카테고리 수를 prop으로 받을 수도 있고, 여기선 mock/ref 사용
// 필요하면 defineProps로 바꿔서 상위에서 전달하세요.
const categoryCount = ref(12) // 예: 12개

const router = useRouter()
const mapContainer = ref(null)
let mapInstance = null

onMounted(() => {
  if (!mapContainer.value) return
  mapInstance = L.map(mapContainer.value, { zoomControl: true }).setView([37.5665, 126.9780], 11)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(mapInstance)

  // 예시 마커(실데이터로 대체)
  L.marker([37.5665, 126.9780]).addTo(mapInstance).bindPopup('서울 중심')
})

function goToFullMap() {
  router.push({ path: '/map' }) // 전체지도 라우트로 변경
}
</script>

<template>
  <div class="map-check">
    <div class="map-header">
      <h2>지도로 둘러보기</h2>
      <button class="all-map-btn" @click="goToFullMap" aria-label="전체지도 보기">전체지도</button>
    </div>

    <div ref="mapContainer" class="map-container" role="region" aria-label="지도"></div>

    <p class="map-caption">
      서울 관광지, 맛집, 축제 및 행사 (<strong>{{ categoryCount }}</strong>곳)
      <br />
      지도에서 유형별로 필터링해 보세요
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