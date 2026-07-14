<script setup>
import { ref } from 'vue'
const title = ref('')
const content = ref('')
function submit(){ alert('샘플: 서버에 POST 요청 전송하세요') }
</script>

<template>
  <section style="padding:20px; max-width:900px; margin:0 auto">
    <h2>글쓰기</h2>
    <input v-model="title" placeholder="제목" style="width:100%; padding:8px; margin-bottom:8px" />
    <textarea v-model="content" rows="8" placeholder="내용" style="width:100%; padding:8px"></textarea>
    <div style="margin-top:10px"><button @click="submit">등록</button></div>
  </section>
</template>