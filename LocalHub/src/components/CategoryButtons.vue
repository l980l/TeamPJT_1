<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  categories: { type: Array, default: () => ['관광지','맛집','축제','꿀팁'] },
  selected: { type: String, default: '' }
})
const emit = defineEmits(['select'])
const current = ref(props.selected)

watch(() => props.selected, v => (current.value = v))

const icons = {
  관광지: '📍',
  맛집: '🍽️',
  축제: '🎉',
  꿀팁: '💡'
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
.category-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(200px, 1fr));
  gap: 28px;
  padding: 28px 16px;
  max-width: 1100px;
  margin: 24px auto;
  justify-items: center;
  align-items: stretch;
}

/* 카드 스타일: 넉넉한 크기, 중앙정렬, 부드러운 호버 */
.card {
  width: 100%;
  max-width: 280px;
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  gap:10px;
  min-height:140px;
  background: #ffffff;
  border-radius:14px;
  border: 1.5px solid rgba(16, 22, 32, 0.226);
  box-shadow: 0 6px 18px rgba(11,16,40,0.04);
  cursor:pointer;
  transition: transform .18s ease, box-shadow .18s ease, background .18s, border-color .12s;
  padding: 18px;
  text-align:center;
  color:#1f2937;
  font-weight:700;
  outline: none;
}

/* 아이콘/라벨 */
.icon { font-size:30px; line-height:1; }
.label { font-size:16px; }

/* Hover에서 배경/색상 변경 + 경계선 색 변화 + 링 효과 */
.card:hover:not(.active) {
  background: linear-gradient(180deg, #f8fbff 0%, #eef7ff 100%);
  border-color: rgba(11, 117, 239, 0.342);
  color: #063970;
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 30px 30px rgba(11, 16, 40, 0.151);
}

/* 키보드 포커스 접근성 */
.card:focus-visible {
  box-shadow: 0 8px 28px rgba(11,16,40,0.10), 0 0 0 6px rgba(11,118,239,0.06);
  border-color: rgba(11,118,239,0.2);
}

/* 활성화 표시 */
.card.active {
  background: linear-gradient(180deg, #f0f8ff 0%, #e8f3ff 100%);
  border-color: rgba(11,118,239,0.18);
  box-shadow: 0 12px 28px rgba(11,118,239,0.07);
  color:#063970;
}

/* 반응형: 2열 / 1열 */
@media (max-width: 1100px) {
  .category-grid { grid-template-columns: repeat(2, minmax(180px, 1fr)); max-width: 760px; }
}
@media (max-width: 600px) {
  .category-grid { grid-template-columns: repeat(1, 1fr); padding: 18px; }
  .card { min-height:120px; max-width: 520px; }
}
</style>