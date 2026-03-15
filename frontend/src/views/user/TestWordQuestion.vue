<template>
  <div class="min-h-screen bg-gradient-to-br from-mint-50 via-mint-100 to-mint-200 flex flex-col">
    <!-- Progress Bar -->
    <div class="bg-white shadow-md p-4">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm text-gray-600">答题进度</span>
        <span class="text-sm font-medium text-mint-600">{{ questionIndex + 1 }} / {{ totalQuestions }}</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-3">
        <div
          class="bg-mint-500 h-3 rounded-full transition-all duration-300"
          :style="{ width: `${((questionIndex + 1) / totalQuestions) * 100}%` }"
        ></div>
      </div>
    </div>
    
    <!-- Content -->
    <div class="flex-1 flex items-center justify-center p-4">
      <div v-if="currentQuestion" class="w-full max-w-2xl">
        <div class="bg-white rounded-2xl shadow-lg p-6">
          <div class="text-center mb-6">
            <h2 class="text-3xl font-bold text-gray-800">{{ currentQuestion.main_word }}</h2>
            <p class="text-gray-500 mt-2">请选择与单词对应的图片</p>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <button
              v-for="(option, index) in shuffledOptions"
              :key="option.word"
              @click="selectOption(option)"
              :disabled="isAnswered"
              :class="[
                'p-4 rounded-xl border-2 transition-all',
                selectedOption?.word === option.word ? 'border-mint-500 bg-mint-50 ring-2 ring-mint-300' : 'border-gray-200 hover:border-mint-300',
                isAnswered && option.word === correctAnswer ? 'border-green-500 bg-green-50 ring-2 ring-green-300' : '',
                isAnswered && selectedOption?.word === option.word && option.word !== correctAnswer ? 'border-red-500 bg-red-50 ring-2 ring-red-300' : ''
              ]"
            >
              <div class="aspect-square bg-gray-100 rounded-lg mb-2 overflow-hidden relative">
                <img
                  v-if="option.image_local_path"
                  :src="option.image_local_path"
                  :alt="option.word"
                  class="w-full h-full object-cover"
                />
                <!-- 正确/错误标记 -->
                <div
                  v-if="isAnswered && option.word === correctAnswer"
                  class="absolute inset-0 bg-green-500 bg-opacity-20 flex items-center justify-center"
                >
                  <svg class="w-16 h-16 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
                  </svg>
                </div>
                <div
                  v-if="isAnswered && selectedOption?.word === option.word && option.word !== correctAnswer"
                  class="absolute inset-0 bg-red-500 bg-opacity-20 flex items-center justify-center"
                >
                  <svg class="w-16 h-16 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                </div>
              </div>
              <!-- 只在检查答案后显示单词和释义 -->
              <div v-if="isAnswered" class="text-center">
                <p class="font-medium text-gray-800">{{ option.word }}</p>
                <p class="text-sm text-gray-500">{{ option.meaning }}</p>
              </div>
              <div v-else class="text-center">
                <p class="text-gray-400 text-sm">选项 {{ index + 1 }}</p>
              </div>
            </button>
          </div>
          
          <div class="mt-6 flex justify-center">
            <button
              v-if="!isAnswered"
              @click="checkAnswer"
              :disabled="!selectedOption"
              class="px-6 py-3 bg-mint-500 text-white rounded-xl hover:bg-mint-600 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium transition-colors"
            >
              检查答案
            </button>
            <button
              v-else
              @click="nextQuestion"
              class="px-6 py-3 bg-mint-500 text-white rounded-xl hover:bg-mint-600 font-medium transition-colors"
            >
              {{ questionIndex < totalQuestions - 1 ? '下一题' : '继续完形填空' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { wordSetApi } from '../../api'

const router = useRouter()
const route = useRoute()

const questionIndex = ref(parseInt(route.params.index) || 0)
const questions = ref([])
const selectedOption = ref(null)
const isAnswered = ref(false)
const results = ref([])

const totalQuestions = computed(() => questions.value.length)

const currentQuestion = computed(() => {
  if (questions.value.length === 0) return null
  return questions.value[questionIndex.value]
})

const shuffledOptions = computed(() => {
  if (!currentQuestion.value) return []
  return [...currentQuestion.value.words].sort(() => Math.random() - 0.5)
})

const correctAnswer = computed(() => {
  if (!currentQuestion.value) return null
  const mainWord = currentQuestion.value.words.find(w => w.word_type === 'main')
  return mainWord?.word
})

const fetchQuestion = async () => {
  try {
    // Get question data from sessionStorage
    const testData = JSON.parse(sessionStorage.getItem('testData') || '{}')
    if (testData.wordQuestions && testData.wordQuestions[questionIndex.value]) {
      const wordSetId = testData.wordQuestions[questionIndex.value].id
      const result = await wordSetApi.get(wordSetId)
      questions.value = [result]
    }
  } catch (e) {
    console.error(e)
  }
}

const selectOption = (option) => {
  if (!isAnswered.value) {
    selectedOption.value = option
  }
}

const checkAnswer = () => {
  if (!selectedOption.value) return
  isAnswered.value = true
  
  // Store result in sessionStorage
  const storedResults = JSON.parse(sessionStorage.getItem('wordResults') || '[]')
  storedResults.push({
    word_set_id: currentQuestion.value.id,
    main_word: currentQuestion.value.main_word,
    selected_word: selectedOption.value.word,
    correct_word: correctAnswer.value,
    is_correct: selectedOption.value.word === correctAnswer.value
  })
  sessionStorage.setItem('wordResults', JSON.stringify(storedResults))
}

const nextQuestion = () => {
  if (questionIndex.value < totalQuestions.value - 1) {
    // Go to next word question
    router.push({ name: 'test-word', params: { index: questionIndex.value + 1 } })
  } else {
    // Go to cloze questions
    router.push({ name: 'test-cloze', params: { index: 0 } })
  }
}

onMounted(() => {
  fetchQuestion()
})
</script>
