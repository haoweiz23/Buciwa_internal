import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

// Import views
import ListView from './views/ListView.vue'
import DetailView from './views/DetailView.vue'
import WordList from './views/WordList.vue'
import ClozeTestView from './views/ClozeTestView.vue'
import ClozeList from './views/ClozeList.vue'
import ListeningView from './views/ListeningView.vue'
import ListeningList from './views/ListeningList.vue'

// Router configuration
const routes = [
  { path: '/', name: 'list', component: ListView },
  { path: '/words', name: 'word-list', component: WordList },
  { path: '/word/:id', name: 'detail', component: DetailView },
  { path: '/cloze', name: 'cloze-list', component: ClozeList },
  { path: '/cloze/create', name: 'cloze-test', component: ClozeTestView },
  { path: '/cloze/:id', name: 'cloze-test-detail', component: ClozeTestView },
  { path: '/listening', name: 'listening-list', component: ListeningList },
  { path: '/listening/create', name: 'listening-test', component: ListeningView },
  { path: '/listening/:id', name: 'listening-test-detail', component: ListeningView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Create and mount app
const app = createApp(App)
app.use(router)
app.mount('#app')
