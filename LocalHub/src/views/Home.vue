<script setup>
import Banner from '../components/Banner.vue'
import CategoryButtons from '../components/CategoryButtons.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
function onCategorySelected(cat){
  router.push({ name: 'board', params: { category: cat } })
}
</script>

<template>
  <Banner />
  <section style="max-width:1200px; margin-top: 80px; margin-left:auto; margin-right:auto; padding:0 16px;">
    <CategoryButtons mode="emit" @select="onCategorySelected" />
  </section>
</template>