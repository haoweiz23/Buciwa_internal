<template>
  <div class="min-h-screen bg-gradient-to-br from-mint-50 via-mint-100 to-mint-200 flex flex-col">
    <!-- Progress Bar -->
    <div class="bg-white shadow-md p-4">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm text-gray-600">答题进度</span>
        <span class="text-sm font-medium text-mint-600">{{ currentIndex + 1 }} / {{ totalQuestions }}</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-3">
        <div
          class="bg-mint-500 h-3 rounded-full transition-all duration-300"
          :style="{ width: `${((currentIndex + 1) / totalQuestions) * 100}%` }"
        ></div>
      </div>
      <div class="flex justify-between text-xs text-gray-500 mt-1">
        <span>单选题: {{ wordQuestions.length }}</span>
        <span>完形填空: {{ clozeQuestions.length }}</span>
      </div>
    </div>
    
    <!-- Content -->
    <div class="flex-1 flex items-center justify-center p-4">
      <div v-if="currentQuestion" class="w-full max-w-2xl">
        <!-- Word Question -->
        <div v-if="currentType === 'word'" class="bg-white rounded-2xl shadow-lg p-6">
          <div class="text-center mb-6">
            <h2 class="text-3xl font-bold text-gray-800">{{ currentQuestion.main_word }}</h2>
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
              class="px-6 py-3 bg-mint-500 text-white rounded-xl hover:bg-mint-600 disabled:bg-gray-300 font-medium"
            >
              检查答案
            </button>
            <button
              v-else
              @click="nextQuestion"
              class="px-6 py-3 bg-mint-500 text-white rounded-xl hover:bg-mint-600 font-medium"
            >
              {{ currentIndex < totalQuestions - 1 ? '下一题' : '查看结果' }}
            </button>
          </div>
        </div>
        
        <!-- Cloze Question -->
        <div v-else class="bg-white rounded-2xl shadow-lg p-6">
          <!-- Language Toggle -->
          <div class="flex justify-end mb-4">
            <button
              @click="language = 'zh'"
              :class="[
                'px-3 py-1 rounded-lg text-sm font-medium transition-colors',
                language === 'zh' ? 'bg-mint-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              ]"
            >
              中文
            </button>
            <button
              @click="language = 'en'"
              :class="[
                'px-3 py-1 rounded-lg text-sm font-medium transition-colors',
                language === 'en' ? 'bg-mint-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              ]"
            >
              English
            </button>
          </div>
          
          <!-- Image -->
          <div class="aspect-video bg-gray-100 rounded-lg mb-4 overflow-hidden">
            <img
              v-if="currentQuestion.image_local_path"
              :src="currentQuestion.image_local_path"
              alt="Question"
              class="w-full h-full object-cover"
            />
          </div>
          
          <!-- Sentence with clickable blanks -->
          <div class="text-center mb-6 text-xl text-gray-800 leading-relaxed">
            <template v-if="language === 'zh'">
              <span>{{ getSentenceParts(currentQuestion.sentence).before }}</span>
              <!-- 第一个空 -->
              <span
                @click="removeFromBlank(0)"
                :class="[
                  'inline-block min-w-[80px] px-3 py-1 mx-1 rounded-lg border-2 transition-all cursor-pointer',
                  filledBlanks[0]
                    ? (isAnswered
                        ? (correctAnswers.includes(filledBlanks[0]) ? 'border-green-500 bg-green-50 text-green-700' : 'border-red-500 bg-red-50 text-red-700')
                        : 'border-mint-500 bg-mint-50 text-mint-700 hover:border-red-400')
                    : 'border-gray-300 bg-gray-50 text-gray-400'
                ]"
              >
                {{ filledBlanks[0] || '___1___' }}
              </span>
              <span>{{ getSentenceParts(currentQuestion.sentence).middle }}</span>
              <!-- 第二个空 -->
              <span
                @click="removeFromBlank(1)"
                :class="[
                  'inline-block min-w-[80px] px-3 py-1 mx-1 rounded-lg border-2 transition-all cursor-pointer',
                  filledBlanks[1]
                    ? (isAnswered
                        ? (correctAnswers.includes(filledBlanks[1]) ? 'border-green-500 bg-green-50 text-green-700' : 'border-red-500 bg-red-50 text-red-700')
                        : 'border-mint-500 bg-mint-50 text-mint-700 hover:border-red-400')
                    : 'border-gray-300 bg-gray-50 text-gray-400'
                ]"
              >
                {{ filledBlanks[1] || '___2___' }}
              </span>
              <span>{{ getSentenceParts(currentQuestion.sentence).after }}</span>
            </template>
            <template v-else>
              <span>{{ getSentenceParts(currentQuestion.sentence_en).before }}</span>
              <span
                @click="removeFromBlank(0)"
                :class="[
                  'inline-block min-w-[80px] px-3 py-1 mx-1 rounded-lg border-2 transition-all cursor-pointer',
                  filledBlanks[0]
                    ? (isAnswered
                        ? (correctAnswers.includes(filledBlanks[0]) ? 'border-green-500 bg-green-50 text-green-700' : 'border-red-500 bg-red-50 text-red-700')
                        : 'border-mint-500 bg-mint-50 text-mint-700 hover:border-red-400')
                    : 'border-gray-300 bg-gray-50 text-gray-400'
                ]"
              >
                {{ filledBlanks[0] || '___1___' }}
              </span>
              <span>{{ getSentenceParts(currentQuestion.sentence_en).middle }}</span>
              <span
                @click="removeFromBlank(1)"
                :class="[
                  'inline-block min-w-[80px] px-3 py-1 mx-1 rounded-lg border-2 transition-all cursor-pointer',
                  filledBlanks[1]
                    ? (isAnswered
                        ? (correctAnswers.includes(filledBlanks[1]) ? 'border-green-500 bg-green-50 text-green-700' : 'border-red-500 bg-red-50 text-red-700')
                        : 'border-mint-500 bg-mint-50 text-mint-700 hover:border-red-400')
                    : 'border-gray-300 bg-gray-50 text-gray-400'
                ]"
              >
                {{ filledBlanks[1] || '___2___' }}
              </span>
              <span>{{ getSentenceParts(currentQuestion.sentence_en).after }}</span>
            </template>
          </div>
          
          <!-- Answer feedback after checking -->
          <div v-if="isAnswered" class="mb-6 p-4 bg-gray-50 rounded-lg">
            <h4 class="font-medium text-gray-700 mb-2">正确答案：</h4>
            <div class="flex gap-4">
              <div class="flex-1 p-2 bg-green-50 rounded border border-green-200">
                <span class="font-medium text-green-700">{{ currentQuestion.word1 }}</span>
                <span class="text-sm text-gray-500 ml-2">{{ currentQuestion.word1_meaning || '' }}</span>
              </div>
              <div class="flex-1 p-2 bg-green-50 rounded border border-green-200">
                <span class="font-medium text-green-700">{{ currentQuestion.word2 }}</span>
                <span class="text-sm text-gray-500 ml-2">{{ currentQuestion.word2_meaning || '' }}</span>
              </div>
            </div>
          </div>
          
          <!-- Options - 4 words with meanings -->
          <div class="flex flex-wrap justify-center gap-3 mb-6">
            <button
              v-for="option in shuffledClozeOptionsWithMeanings"
              :key="option.word"
              @click="selectClozeOption(option.word)"
              :disabled="isAnswered"
              :class="[
                'px-5 py-2 rounded-lg border-2 transition-all font-medium',
                filledBlanks.includes(option.word)
                  ? (isAnswered && correctAnswers.includes(option.word)
                      ? 'border-green-500 bg-green-100 text-green-700'
                      : (isAnswered && !correctAnswers.includes(option.word)
                          ? 'border-gray-300 bg-gray-100 text-gray-500'
                          : 'border-mint-500 bg-mint-100 text-mint-700 cursor-pointer'))
                  : 'border-gray-200 bg-white text-gray-700 hover:border-mint-400 hover:bg-mint-50',
                isAnswered && correctAnswers.includes(option.word) && !filledBlanks.includes(option.word) ? 'border-green-500 bg-green-50' : ''
              ]"
            >
              {{ option.word }}
              <span v-if="isAnswered" class="text-xs text-gray-500 ml-1">{{ option.meaning }}</span>
            </button>
          </div>
          
          <div class="flex justify-center">
            <button
              v-if="!isAnswered"
              @click="checkClozeAnswer"
              :disabled="filledBlanks.includes(null)"
              class="px-6 py-3 bg-mint-500 text-white rounded-xl hover:bg-mint-600 disabled:bg-gray-300 font-medium"
            >
              检查答案
            </button>
            <button
              v-else
              @click="nextQuestion"
              class="px-6 py-3 bg-mint-500 text-white rounded-xl hover:bg-mint-600 font-medium"
            >
              {{ currentIndex < totalQuestions - 1 ? '下一题' : '查看结果' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { testApi } from '../../api'

const router = useRouter()

const activeTest = ref(null)
const wordQuestions = ref([])
const clozeQuestions = ref([])
const currentIndex = ref(0)
const language = ref('zh')

const selectedOption = ref(null)
const filledBlanks = ref([null, null])
const isAnswered = ref(false)
const results = ref({ word: [], cloze: [] })

const totalQuestions = computed(() => wordQuestions.value.length + clozeQuestions.value.length)

const currentType = computed(() => {
  if (currentIndex.value < wordQuestions.value.length) {
    return 'word'
  }
  return 'cloze'
})

const currentQuestion = computed(() => {
  if (currentType.value === 'word') {
    return wordQuestions.value[currentIndex.value]
  }
  const clozeIndex = currentIndex.value - wordQuestions.value.length
  return clozeQuestions.value[clozeIndex]
})

const shuffledOptions = computed(() => {
  if (!currentQuestion.value || currentType.value !== 'word') return []
  const options = [...currentQuestion.value.words]
  return options.sort(() => Math.random() - 0.5)
})

const shuffledClozeOptionsWithMeanings = computed(() => {
  if (!currentQuestion.value || currentType.value !== 'cloze') return []
  const options = [
    { word: currentQuestion.value.word1, meaning: currentQuestion.value.word1_meaning },
    { word: currentQuestion.value.word2, meaning: currentQuestion.value.word2_meaning },
    { word: currentQuestion.value.distractor1, meaning: currentQuestion.value.distractor1_meaning },
    { word: currentQuestion.value.distractor2, meaning: currentQuestion.value.distractor2_meaning }
  ].filter(o => o.word)
  return options.sort(() => Math.random() - 0.5)
})

const correctAnswer = computed(() => {
  if (!currentQuestion.value || currentType.value !== 'word') return null
  return currentQuestion.value.words.find(w => w.word_type === 'main')?.word
})

const correctAnswers = computed(() => {
  if (!currentQuestion.value || currentType.value !== 'cloze') return []
  return [currentQuestion.value.word1, currentQuestion.value.word2]
})

const fetchActiveTest = async () => {
  try {
    const result = await testApi.getActive()
    if (!result) {
      router.push({ name: 'home' })
      return
    }
    
    activeTest.value = result.quiz_set
    wordQuestions.value = result.word_questions
    clozeQuestions.value = result.cloze_questions
    
    // Fetch full question details
    const wordDetails = await Promise.all(
      wordQuestions.value.map(wq => fetch(`/api/word-sets/${wq.id}`).then(r => r.json()))
    )
    wordQuestions.value = wordDetails
    
    const clozeDetails = await Promise.all(
      clozeQuestions.value.map(cq => fetch(`/api/cloze-tests/${cq.id}`).then(r => r.json()))
    )
    clozeQuestions.value = clozeDetails
  } catch (e) {
    console.error(e)
    router.push({ name: 'home' })
  }
}

const selectOption = (option) => {
  if (!isAnswered.value) {
    selectedOption.value = option
  }
}

const selectClozeOption = (option) => {
  if (isAnswered.value) return
  
  // If the option is already used, remove it from the blank (toggle off)
  const usedIndex = filledBlanks.value.indexOf(option)
  if (usedIndex !== -1) {
    const newBlanks = [...filledBlanks.value]
    newBlanks[usedIndex] = null
    filledBlanks.value = newBlanks
    return
  }
  
  // Otherwise, find first empty blank and fill it
  const firstEmpty = filledBlanks.value.indexOf(null)
  if (firstEmpty !== -1) {
    const newBlanks = [...filledBlanks.value]
    newBlanks[firstEmpty] = option
    filledBlanks.value = newBlanks
  }
}

const removeFromBlank = (index) => {
  if (isAnswered.value) return
  const newBlanks = [...filledBlanks.value]
  newBlanks[index] = null
  filledBlanks.value = newBlanks
}

const checkAnswer = () => {
  isAnswered.value = true
  const isCorrect = selectedOption.value?.word === correctAnswer.value
  
  results.value.word.push({
    word_set_id: currentQuestion.value.id,
    main_word: currentQuestion.value.main_word,
    selected_word: selectedOption.value.word,
    correct_word: correctAnswer.value,
    is_correct: isCorrect
  })
}

const checkClozeAnswer = () => {
  isAnswered.value = true
  
  results.value.cloze.push({
    cloze_test_id: currentQuestion.value.id,
    sentence: currentQuestion.value.sentence,
    selected_answer1: filledBlanks.value[0],
    selected_answer2: filledBlanks.value[1],
    correct_answer1: correctAnswers.value[0],
    correct_answer2: correctAnswers.value[1],
    is_correct: filledBlanks.value.every((b, i) => b === correctAnswers.value[i])
  })
}

const nextQuestion = () => {
  if (currentIndex.value < totalQuestions.value - 1) {
    currentIndex.value++
    selectedOption.value = null
    filledBlanks.value = [null, null]
    isAnswered.value = false
  } else {
    // Submit results
    submitResults()
  }
}

const submitResults = async () => {
  const correctCount =
    results.value.word.filter(r => r.is_correct).length +
    results.value.cloze.filter(r => r.is_correct).length
  
  // Build wrong questions list
  const wrongQuestions = []
  
  // Add wrong word questions
  results.value.word.filter(r => !r.is_correct).forEach(r => {
    wrongQuestions.push({
      question_type: 'word',
      question_id: r.word_set_id,
      main_word: r.main_word,
      selected_answer: r.selected_word,
      correct_answer: r.correct_word
    })
  })
  
  // Add wrong cloze questions
  results.value.cloze.filter(r => !r.is_correct).forEach(r => {
    wrongQuestions.push({
      question_type: 'cloze',
      question_id: r.cloze_test_id,
      sentence: r.sentence,
      selected_answer: `${r.selected_answer1}, ${r.selected_answer2}`,
      correct_answer: `${r.correct_answer1}, ${r.correct_answer2}`
    })
  })
  
  try {
    await testApi.submit({
      quiz_set_id: activeTest.value.id,
      total_questions: totalQuestions.value,
      correct_answers: correctCount,
      word_results: results.value.word,
      cloze_results: results.value.cloze,
      wrong_questions: wrongQuestions
    })
    
    // Store results for result page
    sessionStorage.setItem('testResults', JSON.stringify({
      total: totalQuestions.value,
      correct: correctCount,
      wordResults: results.value.word,
      clozeResults: results.value.cloze,
      wrongQuestions: wrongQuestions
    }))
    
    router.push({ name: 'test-result' })
  } catch (e) {
    console.error(e)
  }
}

const getSentenceParts = (sentence) => {
  if (!sentence) return { before: '', middle: '', after: '' }
  const parts = sentence.split('___')
  if (parts.length === 3) {
    return { before: parts[0], middle: parts[1], after: parts[2] }
  }
  return { before: sentence, middle: '', after: '' }
}

onMounted(() => {
  fetchActiveTest()
})
</script>
