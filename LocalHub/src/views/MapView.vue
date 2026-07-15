<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import L from 'leaflet'
const mapContainer = ref(null)
let mapInstance = null
let resizeHandler = null
let resizeObserver = null

onMounted(() => {
  if (!mapContainer.value) return

  mapInstance = L.map(mapContainer.value, { zoomControl: true }).setView([37.5665, 126.9780], 12)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(mapInstance)

  // 예시 마커 (백엔드에서 데이터 받아 마커 렌더하면 대체)
  L.marker([37.5665, 126.9780]).addTo(mapInstance).bindPopup('서울 중심')

  const refresh = () => { try { mapInstance.invalidateSize() } catch (e) {} }

  mapInstance.whenReady(() => {
    refresh()
    setTimeout(refresh, 100)
    setTimeout(refresh, 500)
  })

  resizeHandler = () => refresh()
  window.addEventListener('resize', resizeHandler)
  if (typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(refresh)
    resizeObserver.observe(mapContainer.value)
  }
})

onBeforeUnmount(() => {
  if (resizeHandler) window.removeEventListener('resize', resizeHandler)
  if (resizeObserver) resizeObserver.disconnect()
  if (mapInstance) { mapInstance.remove(); mapInstance = null }
})
</script>

<template>
  <section class="map-view">
    <div ref="mapContainer" class="map-full" role="region" aria-label="전체 지도"></div>
  </section>
</template>

<style scoped>
.map-view { width: 100%; min-height: calc(100vh - var(--nav-height, 56px)); box-sizing: border-box; }
.map-full { width: 100%; height: 100%; min-height: calc(100vh - var(--nav-height, 56px)); }
</style>