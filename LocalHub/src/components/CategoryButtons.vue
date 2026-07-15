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
/* 컨테이너를 뷰포트 전체 폭으로 확장(센터 레이아웃 안에서 full-bleed) */
.category-grid {
  width: 100vw;
  margin-left: calc(50% - 50vw);
  box-sizing: border-box;
  padding: 12px 20px;
  display: grid;
  gap: 12px;

  /* 기본: 7개를 균등 분할하여 한 줄로 채움 */
  grid-template-columns: repeat(7, minmax(0, 1fr));
  align-items: stretch;
  justify-items: stretch;
}

/* 카드(버튼) 스타일 */
.card {
  width: 100%;
  height: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: #ffffff;
  border-radius: 14px;
  border: 1.5px solid rgba(16, 22, 32, 0);
  box-shadow: 0 6px 18px rgba(11,16,40,0.04);
  padding: 12px;
  text-align: center;
  color: #1f2937;
  font-weight: 700;
  cursor: pointer;
  transition: transform .18s, box-shadow .18s, background .18s, border-color .12s;
}

/* 아이콘 / 라벨 */
.icon { font-size: 35px; line-height: 1; }
.label { font-size: 15px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width:100%; }

/* 반응형 전환: 뷰포트가 좁아지면 자동으로 min 크기 기준으로 칸수를 줄여 래핑 */
@media (max-width: 1050px) {
  /* 버튼 최소 너비를 140px로 설정 — 공간이 부족하면 칸 수가 줄어듦 */
  .category-grid {
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  }
}

@media (max-width: 700px) {
  .category-grid {
    grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
    padding: 8px;
    gap: 8px;
  }
  .card { height: 100px; padding: 10px; }
  .icon { font-size: 30px; }
  .label { font-size: 13px; }
}
</style>