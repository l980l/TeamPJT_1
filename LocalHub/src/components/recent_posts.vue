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
  <div class="recent-posts">
    <div class="header">
      <h2>최근 게시글</h2>
      <router-link to="/posts" id="more-posts" aria-label="전체 게시글 보기">더보기</router-link>
    </div>

    <ul class="posts-list">
        <li v-for="post in posts" :key="post.id" class="post-item">
        <router-link
            :to="`/posts/${post.id}`"
            class="post-link"
            :aria-label="`게시글 ${post.title} 보기`"
        >
            <div class="post-row">
                <div class="post-left">
                    <div class="post-category">{{ post.category }}</div>
                    <div class="post-title-text">{{ post.title }}</div>
                </div>

                <div class="post-meta">
                    <div class="post-views">{{ post.view_count }} views</div>
                    <div class="post-date">{{ new Date(post.created_at).toLocaleDateString() }}</div>
                </div>
            </div>
        </router-link>
    </li>
  <li v-if="posts.length === 0" class="empty">게시글이 없습니다.</li>
</ul>
  </div>
</template>

<style scoped>
.recent-posts { 
    margin: 20px; 
    color: #fff; 
}

.header { 
    display: flex; 
    align-items: center; 
    gap: 12px; 
    margin-bottom: 10px; 
}

.header h2 { 
    font-size: 20px; 
    margin: 0; 
    text-align: left; 
}

#more-posts { 
    margin-left: auto; 
    font-size: 14px; 
    color: #4ea1ff; 
    text-decoration: none;
    cursor: pointer; 
}

.posts-list { 
    list-style: none; 
    padding: 0; 
    margin: 0; 
}

/* 왼쪽 컬럼: 카테고리/제목/요약 (좌측 정렬) */
.post-main {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  min-width: 0;
}

.post-item { 
    padding: 10px 0;
    border-bottom: 1px solid rgba(255,255,255,0.06); 
}

.post-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.post-category {
  flex: 0 0 90px;
  color: #a8d0ff;
  font-size: 13px;
}

.post-title {
  display: flex;
  flex-direction: column;
  justify-content: center;
  flex: 1 1 auto;
  min-width: 0;
}

.post-title a { 
    color: #fff; 
    text-decoration: none; 
    font-weight: 600; 
}

.post-title-text {
  flex: 1 1 auto;
  min-width: 0;
  font-weight: 600;
  color: #fff;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.post-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  flex: 1 1 auto;
}

.post-snippet {
  color: #d0d6dd;
  font-size: 13px;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.post-views,
.post-date {
  color: #cfd8df;
  font-size: 13px;
}

.post-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex: 0 0 140px;
  text-align: right;
}

.post-link {
  display: block;
  color: inherit;
  text-decoration: none;
}

.post-link:focus { 
    outline: 2px solid rgba(78,161,255,0.6); 
    outline-offset: 2px; 
}

.post-views,
.post-date {
  color: #cfd8df;
  font-size: 13px;
}

/* 반응형: 좁은 화면에서는 column으로 전환 */
@media (max-width: 640px) {
  .post-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .post-category, .post-views, .post-date {
    width: auto; 
    text-align: left; 
  }

  .post-views, .post-date { 
    font-size: 12px; 
    color: #bfc8cf; 
  }

  #more-posts { 
    margin-left: 0; 
    align-self: flex-end; 
  }

  .post-meta {
    align-items: flex-start;
    width: auto;
  }
}
</style>