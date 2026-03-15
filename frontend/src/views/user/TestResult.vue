<template>
  <div class="min-h-screen bg-gradient-to-br from-mint-50 via-mint-100 to-mint-200 flex flex-col items-center p-4">
    <div class="bg-white rounded-2xl shadow-lg p-8 w-full max-w-lg text-center mt-8">
      <div class="text-6xl mb-4">🎉</div>
      <h1 class="text-2xl font-bold text-gray-800 mb-2">测验完成！</h1>
      <p class="text-gray-500 mb-6">你的成绩是：</p>
      
      <div class="text-5xl font-bold mb-6" :class="scoreColor">
        {{ scorePercentage }}%
      </div>
      
      <div class="bg-gray-50 rounded-xl p-4 mb-6">
        <div class="flex justify-between text-sm">
          <span class="text-gray-600">正确答案</span>
          <span class="font-medium text-gray-800">{{ correctCount }} / {{ totalQuestions }}</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
          <div
            class="h-2 rounded-full transition-all"
            :class="scoreBarColor"
            :style="{ width: `${scorePercentage}%` }"
          ></div>
        </div>
      </div>
      
      <div class="grid grid-cols-2 gap-4 mb-6">
        <div class="bg-blue-50 rounded-xl p-4">
          <p class="text-sm text-blue-600 mb-1">单选题</p>
          <p class="text-2xl font-bold text-blue-700">{{ wordCorrectCount }} / {{ wordTotal }}</p>
        </div>
        <div class="bg-green-50 rounded-xl p-4">
          <p class="text-sm text-green-600 mb-1">完形填空</p>
          <p class="text-2xl font-bold text-green-700">{{ clozeCorrectCount }} / {{ clozeTotal }}</p>
        </div>
      </div>
      
      <div class="flex gap-4">
        <button
          @click="goHome"
          class="flex-1 px-6 py-3 bg-gray-100 text-gray-600 rounded-xl hover:bg-gray-200 font-medium"
        >
          返回首页
        </button>
        <button
          @click="retry"
          class="flex-1 px-6 py-3 bg-mint-500 text-white rounded-xl hover:bg-mint-600 font-medium"
        >
          重新测验
        </button>
      </div>
    </div>
    
    <!-- Wrong Questions Section -->
    <div v-if="wrongQuestions.length > 0" class="bg-white rounded-2xl shadow-lg p-6 w-full max-w-lg mt-6 mb-8">
      <h2 class="text-xl font-bold text-gray-800 mb-4 flex items-center">
        <span class="text-2xl mr-2">📝</span>
        错题回顾
      </h2>
      
      <div class="space-y-4">
        <div
          v-for="(question, index) in wrongQuestions"
          :key="index"
          class="p-4 rounded-xl border-2"
          :class="question.question_type === 'word' ? 'border-blue-200 bg-blue-50' : 'border-green-200 bg-green-50'"
        >
          <div class="flex items-center mb-2">
            <span
              class="px-2 py-1 rounded text-xs font-medium"
              :class="question.question_type === 'word' ? 'bg-blue-200 text-blue-700' : 'bg-green-200 text-green-700'"
            >
              {{ question.question_type === 'word' ? '单选题' : '完形填空' }}
            </span>
          </div>
          
          <p class="font-medium text-gray-800 mb-2">
            {{ question.main_word || question.sentence }}
          </p>
          
          <div class="flex gap-4 text-sm">
            <div class="flex-1">
              <span class="text-gray-500">你的答案：</span>
              <span class="text-red-600 font-medium">{{ question.selected_answer }}</span>
            </div>
            <div class="flex-1">
              <span class="text-gray-500">正确答案：</span>
              <span class="text-green-600 font-medium">{{ question.correct_answer }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const results = ref(null)

const totalQuestions = computed(() => results.value?.total || 0)
const correctCount = computed(() => results.value?.correct || 0)
const scorePercentage = computed(() => {
  if (totalQuestions.value === 0) return 0
  return Math.round((correctCount.value / totalQuestions.value) * 100)
})

const wordCorrectCount = computed(() => {
  if (!results.value?.wordResults) return 0
  return results.value.wordResults.filter(r => r.is_correct).length
})

const wordTotal = computed(() => results.value?.wordResults?.length || 0)

const clozeCorrectCount = computed(() => {
  if (!results.value?.clozeResults) return 0
  return results.value.clozeResults.filter(r => r.is_correct).length
})

const clozeTotal = computed(() => results.value?.clozeResults?.length || 0)

const wrongQuestions = computed(() => results.value?.wrongQuestions || [])

const scoreColor = computed(() => {
  const pct = scorePercentage.value
  if (pct >= 80) return 'text-green-500'
  if (pct >= 60) return 'text-blue-500'
  if (pct >= 40) return 'text-amber-500'
  return 'text-red-500'
})

const scoreBarColor = computed(() => {
  const pct = scorePercentage.value
  if (pct >= 80) return 'bg-green-500'
  if (pct >= 60) return 'bg-blue-500'
  if (pct >= 40) return 'bg-amber-500'
  return 'bg-red-500'
})

onMounted(() => {
  const stored = sessionStorage.getItem('testResults')
  if (stored) {
    results.value = JSON.parse(stored)
    sessionStorage.removeItem('testResults')
  } else {
    router.push({ name: 'home' })
  }
})

const goHome = () => {
  router.push({ name: 'home' })
}

const retry = () => {
  router.push({ name: 'test' })
}
</script>
