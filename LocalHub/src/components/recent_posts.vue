<script setup>
import { onMounted } from 'vue'
import { usePosts } from '../composables/usePosts'

const { posts, loading, error, loadRecent } = usePosts()
onMounted(() => loadRecent(5))

function shortText(text = '', max = 120) {
  return text.length > max ? text.slice(0, max) + '…' : text
}
</script>

<template>
  <section class="recent">
    <div class="recent__card">
      <header class="recent__head">
        <h3 class="recent__title">최근 게시글</h3>
        <router-link :to="{ name: 'board', params: { category: '' } }" class="recent__more">더보기</router-link>
      </header>

      <div class="recent__row recent__row--head">
        <span>카테고리</span>
        <span class="recent__sample">제목</span>
        <span class="recent__meta">views</span>
      </div>

      <ul class="recent__list">
        <li v-for="post in posts" :key="post.id">
          <router-link class="recent__row"
            :to="{ name: 'post', params: { id: post.id }, query: { category: post.category } }">
            <span class="recent__cat">{{ post.category }}</span>
            <span class="recent__sample">{{ post.title }}</span>
            <span class="recent__meta">
              {{ post.views ?? 0 }} views
              <br />
              {{ new Date(post.created_at).toLocaleDateString() }}
            </span>
          </router-link>
        </li>

        <li v-if="posts.length === 0" class="recent__row recent__empty">
          게시글이 없습니다.
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.recent {
  max-width: 1000px;
  margin: 40px auto 70px;
  padding: 0 20px;
}

.recent__card {
  background: #fff;
  border: 1px solid rgba(220, 220, 230, 0.6);
  border-radius: 14px;
  box-shadow: 0 6px 20px rgba(40, 30, 90, 0.04);
  padding: 22px 20px;
  color: #222;
}

.recent__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.recent__title {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
}

.recent__more {
  color: #6b78e8;
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
}

.recent__list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.recent__row {
  display: grid;
  grid-template-columns: 120px 1fr 140px;
  align-items: center;
  padding: 12px 6px;
  border-top: 1px solid rgba(230, 230, 235, 0.7);
  font-size: 14px;
  gap: 8px;
  text-decoration: none;
}

.recent__row--head {
  border-top: none;
  color: #9aa0b3;
  font-size: 13px;
}

.recent__cat {
  color: #6b78e8;
  font-weight: 600;
}

.recent__sample {
  text-align: left;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recent__meta {
  text-align: right;
  color: #9aa4ad;
  font-size: 13px;
  line-height: 1.6;
}

.recent__empty {
  grid-column: 1 / -1;
  text-align: center;
  color: #9aa4ad;
  padding: 14px 0;
}

/* 반응형: 좁아지면 컬럼 비율 변경 */
@media (max-width:900px) {
  .recent__row {
    grid-template-columns: 80px 1fr 90px;
  }

  .recent {
    padding: 0 12px;
    margin-top: 24px;
  }
}
</style>
