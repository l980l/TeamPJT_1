import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import BoardPage from '../views/BoardPage.vue'
import PostView from '../views/PostView.vue'
import BoardEditor from '../views/BoardEditor.vue'

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/board/:category', name: 'board', component: BoardPage, props: true },
  { path: '/post/:id', name: 'post', component: PostView, props: true },
  { path: '/new', name: 'new', component: BoardEditor }
]

export default createRouter({
  history: createWebHistory(),
  routes
})