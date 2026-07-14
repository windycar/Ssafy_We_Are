import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Map from '../views/Map.vue'
import CommunityList from '../views/CommunityList.vue'
import PostEditor from '../views/PostEditor.vue'
import PostDetail from '../views/PostDetail.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/map', component: Map },
    { path: '/community', component: CommunityList },
    { path: '/community/write', component: PostEditor },
    { path: '/community/:id', component: PostDetail },
    { path: '/community/:id/edit', component: PostEditor },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
