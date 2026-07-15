<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  categories: { type: Array, default: () => ['관광지','레포츠','문화시설','쇼핑','숙박','여행코스','축제공연행사'] },
  selected: { type: String, default: '' }
})
const emit = defineEmits(['select'])
const current = ref(props.selected)

watch(() => props.selected, v => (current.value = v))

const icons = {
  관광지: '📍',
  레포츠: '🏄‍♂️',
  문화시설: '🏛️',
  쇼핑: '🛍️',
  숙박: '🏨',
  여행코스: '🗺️',
  축제공연행사: '🎉'
}

function onClick(cat){
  current.value = cat
  emit('select', cat)
}

const items = computed(() => props.categories.map(c => ({
  label: c,
  icon: icons[c] ?? '🔖'
})))
</script>

<template>
  <div class="category-grid" role="list">
    <button
      v-for="it in items"
      :key="it.label"
      class="card"
      :class="{ active: it.label === current }"
      @click="onClick(it.label)"
      role="listitem"
      :aria-pressed="it.label === current"
    >
      <div class="icon">{{ it.icon }}</div>
      <div class="label">{{ it.label }}</div>
    </button>
  </div>
</template>

<style scoped>
/* 넓이 중심: 카드 폭을 키우기 위해 컨테이너 최대너비 증가하고 칸 최소값 설정 */
.category-grid {
  max-width: 1600px;        /* 전체 그리드 너비 증가 */
  margin: 36px auto;
  padding: 24px 32px;
  box-sizing: border-box;

  display: grid;
  grid-template-columns: repeat(4, minmax(260px, 1fr)); /* 각 칸 최소 260px → 카드 넓음 */
  grid-auto-rows: 220px;
  gap: 28px;
  align-items: stretch;
  justify-items: center; /* 카드가 셀 중앙에서 넓게 보이도록 */
}

/* 카드가 그리드 셀에 맞춰 벌어지도록 가득 채움 */
.card {
  width: 100%;
  height: 100%;
  min-width: 260px;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 20px;
  border-radius: 18px;
  border: 1px solid rgba(107,120,232,0.08);
  background: #fff;
  box-shadow: 0 12px 30px rgba(11,16,40,0.05);
}

/* 반응형: 칸 최소값 유지하면서 열 수 감소 */
@media (max-width: 1400px) {
  .category-grid { grid-template-columns: repeat(3, minmax(220px, 1fr)); grid-auto-rows: 180px; max-width: 1200px; }
  .card { min-width: 220px; min-height: 180px; padding: 18px; }
}
@media (max-width: 1000px) {
  .category-grid { grid-template-columns: repeat(2, minmax(200px, 1fr)); grid-auto-rows: 160px; max-width: 900px; }
  .card { min-width: 200px; min-height: 160px; padding: 16px; }
}
@media (max-width: 600px) {
  .category-grid { grid-template-columns: 1fr; grid-auto-rows: 140px; padding: 12px; max-width: 480px; }
  .card { min-width: auto; min-height: 140px; padding: 12px; }
}
.icon { font-size: 64px; }   /* 이모지 크게 */
.label { font-size: 18px; font-weight: 800; } /* 라벨 크게 + 굵게 */
</style>