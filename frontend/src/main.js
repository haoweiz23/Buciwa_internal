import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

// Import admin views
import LoginView from './views/admin/LoginView.vue'
import AdminLayout from './views/admin/AdminLayout.vue'
import AdminHome from './views/admin/AdminHome.vue'
import AdminWordList from './views/admin/AdminWordList.vue'
import AdminWordDetail from './views/admin/AdminWordDetail.vue'
import AdminClozeList from './views/admin/AdminClozeList.vue'
import AdminClozeCreate from './views/admin/AdminClozeCreate.vue'
import AdminClozeDetail from './views/admin/AdminClozeDetail.vue'
import AdminListeningList from './views/admin/AdminListeningList.vue'
import AdminListeningCreate from './views/admin/AdminListeningCreate.vue'
import AdminQuizSetList from './views/admin/AdminQuizSetList.vue'
import AdminQuizSetDetail from './views/admin/AdminQuizSetDetail.vue'
import AdminTestResults from './views/admin/AdminTestResults.vue'

// Import user views
import UserHome from './views/user/UserHome.vue'
import TestView from './views/user/TestView.vue'
import TestWordQuestion from './views/user/TestWordQuestion.vue'
import TestClozeQuestion from './views/user/TestClozeQuestion.vue'
import TestResult from './views/user/TestResult.vue'

// Router configuration
const routes = [
  // ===== User routes (public) =====
  { path: '/', name: 'home', component: UserHome },
  { path: '/test', name: 'test', component: TestView },
  { path: '/test/word/:index', name: 'test-word', component: TestWordQuestion },
  { path: '/test/cloze/:index', name: 'test-cloze', component: TestClozeQuestion },
  { path: '/test/result', name: 'test-result', component: TestResult },
  
  // ===== Auth routes =====
  { path: '/login', name: 'login', component: LoginView },
  
  // ===== Admin routes (protected) =====
  { 
    path: '/admin', 
    component: AdminLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'admin-home', component: AdminHome },
      { path: 'words', name: 'admin-words', component: AdminWordList },
      { path: 'words/:id', name: 'admin-word-detail', component: AdminWordDetail },
      { path: 'cloze', name: 'admin-cloze', component: AdminClozeList },
      { path: 'cloze/create', name: 'admin-cloze-create', component: AdminClozeCreate },
      { path: 'cloze/:id', name: 'admin-cloze-detail', component: AdminClozeDetail },
      { path: 'listening', name: 'admin-listening', component: AdminListeningList },
      { path: 'listening/create', name: 'admin-listening-create', component: AdminListeningCreate },
      { path: 'quiz-sets', name: 'admin-quiz-sets', component: AdminQuizSetList },
      { path: 'quiz-sets/:id', name: 'admin-quiz-set-detail', component: AdminQuizSetDetail },
      { path: 'results', name: 'admin-results', component: AdminTestResults },
    ]
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const isAuthenticated = !!token
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.name === 'login' && isAuthenticated) {
    next({ name: 'admin-home' })
  } else {
    next()
  }
})

// Create and mount app
const app = createApp(App)
app.use(router)
app.mount('#app')
