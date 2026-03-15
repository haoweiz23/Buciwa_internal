<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold text-gray-800 mb-6">管理后台首页</h1>
    
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-xl shadow p-6">
        <div class="flex items-center">
          <div class="p-3 bg-blue-100 rounded-lg">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-gray-500 text-sm">单选题</p>
            <p class="text-2xl font-bold text-gray-800">{{ stats.wordSets }}</p>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-xl shadow p-6">
        <div class="flex items-center">
          <div class="p-3 bg-green-100 rounded-lg">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-gray-500 text-sm">完形填空</p>
            <p class="text-2xl font-bold text-gray-800">{{ stats.clozeTests }}</p>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-xl shadow p-6">
        <div class="flex items-center">
          <div class="p-3 bg-purple-100 rounded-lg">
            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-gray-500 text-sm">听力练习</p>
            <p class="text-2xl font-bold text-gray-800">{{ stats.listening }}</p>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-xl shadow p-6">
        <div class="flex items-center">
          <div class="p-3 bg-orange-100 rounded-lg">
            <svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-gray-500 text-sm">题集</p>
            <p class="text-2xl font-bold text-gray-800">{{ stats.quizSets }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Quick Actions -->
    <div class="bg-white rounded-xl shadow p-6 mb-8">
      <h2 class="text-lg font-bold text-gray-800 mb-4">快捷操作</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <router-link
          to="/admin/words"
          class="flex flex-col items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <svg class="w-8 h-8 text-blue-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          <span class="text-gray-700 text-sm">创建单选题</span>
        </router-link>
        
        <router-link
          to="/admin/cloze/create"
          class="flex flex-col items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <svg class="w-8 h-8 text-green-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          <span class="text-gray-700 text-sm">创建完形填空</span>
        </router-link>
        
        <router-link
          to="/admin/listening/create"
          class="flex flex-col items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <svg class="w-8 h-8 text-purple-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          <span class="text-gray-700 text-sm">创建听力</span>
        </router-link>
        
        <router-link
          to="/admin/quiz-sets"
          class="flex flex-col items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <svg class="w-8 h-8 text-orange-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          <span class="text-gray-700 text-sm">创建题集</span>
        </router-link>
      </div>
    </div>
    
    <!-- Active Quiz Set -->
    <div class="bg-white rounded-xl shadow p-6">
      <h2 class="text-lg font-bold text-gray-800 mb-4">当前激活题集</h2>
      <div v-if="activeQuizSet" class="p-4 bg-green-50 rounded-lg">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-bold text-green-800">{{ activeQuizSet.name }}</h3>
            <p class="text-green-600 text-sm">
              单选题: {{ activeQuizSet.word_count }} | 完形填空: {{ activeQuizSet.cloze_count }}
            </p>
          </div>
          <span class="px-3 py-1 bg-green-500 text-white text-sm rounded-full">激活中</span>
        </div>
      </div>
      <div v-else class="p-4 bg-gray-50 rounded-lg text-center text-gray-500">
        暂无激活的题集，请前往题集管理激活一个题集
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { wordSetApi, clozeTestApi, listeningExerciseApi, quizSetApi } from '../../api'

const stats = ref({
  wordSets: 0,
  clozeTests: 0,
  listening: 0,
  quizSets: 0
})

const activeQuizSet = ref(null)

const fetchStats = async () => {
  try {
    const [wordSets, clozeTests, listening, quizSets] = await Promise.all([
      wordSetApi.list(),
      clozeTestApi.list(),
      listeningExerciseApi.list(),
      quizSetApi.list()
    ])
    
    stats.value = {
      wordSets: wordSets.length,
      clozeTests: clozeTests.length,
      listening: listening.length,
      quizSets: quizSets.length
    }
    
    // Find active quiz set
    activeQuizSet.value = quizSets.find(q => q.is_active) || null
  } catch (e) {
    console.error('Failed to fetch stats:', e)
  }
}

onMounted(() => {
  fetchStats()
})
</script>
