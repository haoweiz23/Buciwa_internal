<template>
  <div class="min-h-screen bg-gradient-to-br from-mint-50 via-mint-100 to-mint-200 flex flex-col items-center justify-center p-4">
    <div class="text-center mb-8">
      <h1 class="text-4xl font-bold text-mint-700 mb-4">单词记忆测验</h1>
      <p class="text-mint-600">测试你的英语单词记忆能力</p>
    </div>
    
    <!-- Loading -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="inline-block w-8 h-8 border-4 border-mint-200 border-t-mint-500 rounded-full animate-spin"></div>
      <p class="text-mint-600 mt-2">加载中...</p>
    </div>
    
    <!-- No Active Quiz -->
    <div v-else-if="!activeTest" class="text-center py-12">
      <div class="text-6xl mb-4">📝</div>
      <p class="text-mint-600 text-lg mb-4">暂无可用的测验</p>
      <p class="text-mint-500 text-sm">请等待管理员设置测验题集</p>
    </div>
    
    <!-- Active Quiz Info -->
    <div v-else class="bg-white rounded-2xl shadow-lg p-8 max-w-md w-full">
      <h2 class="text-2xl font-bold text-mint-700 text-center mb-6">{{ activeTest.quiz_set.name }}</h2>
      <p v-if="activeTest.quiz_set.description" class="text-gray-500 text-center mb-6">
        {{ activeTest.quiz_set.description }}
      </p>
      
      <div class="flex justify-center gap-8 mb-8">
        <div class="text-center">
          <div class="text-3xl font-bold text-mint-600">{{ activeTest.word_questions.length }}</div>
          <div class="text-gray-400 text-sm">单选题</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-bold text-mint-600">{{ activeTest.cloze_questions.length }}</div>
          <div class="text-gray-400 text-sm">完形填空</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-bold text-mint-600">{{ activeTest.total_questions }}</div>
          <div class="text-gray-400 text-sm">总题数</div>
        </div>
      </div>
      
      <button
        @click="startTest"
        class="w-full px-6 py-4 bg-mint-500 text-white rounded-xl text-lg font-bold
               hover:bg-mint-600 transition-colors"
      >
        开始测验
      </button>
    </div>
    
    <!-- Admin Link -->
    <div class="mt-8">
      <router-link to="/login" class="text-mint-500 hover:text-mint-600 text-sm">
        管理员登录
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { testApi } from '../../api'

const router = useRouter()

const isLoading = ref(false)
const activeTest = ref(null)

const fetchActiveTest = async () => {
  isLoading.value = true
  try {
    activeTest.value = await testApi.getActive()
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const startTest = () => {
  router.push({ name: 'test' })
}

onMounted(() => {
  fetchActiveTest()
})
</script>
