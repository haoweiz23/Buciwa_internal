<template>
  <div class="min-h-screen bg-gradient-to-br from-mint-50 via-mint-100 to-mint-200 flex flex-col">
    <!-- Progress Bar -->
    <div class="bg-white shadow-md p-4">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm text-gray-600">完形填空进度</span>
        <span class="text-sm font-medium text-mint-600">{{ questionIndex + 1 }} / {{ clozeQuestions.length }}</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-3">
        <div
          class="bg-mint-500 h-3 rounded-full transition-all duration-300"
          :style="{ width: `${((questionIndex + 1) / clozeQuestions.length) * 100}%` }"
        ></div>
      </div>
    </div>
    
    <!-- Content -->
    <div class="flex-1 flex items-center justify-center p-4">
      <div v-if="currentQuestion" class="w-full max-w-2xl">
        <div class="bg-white rounded-2xl shadow-lg p-6">
          <!-- Language Toggle -->
          <div class="flex justify-end mb-4">
            <button
              @click="language = 'zh'"
              :class="[
                'px-3 py-1 rounded-lg text-sm font-medium transition-colors',
                language === 'zh' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              ]"
            >
              中文
            </button>
            <button
              @click="language = 'en'"
              :class="[
                'px-3 py-1 rounded-lg text-sm font-medium transition-colors',
                language === 'en' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
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
              alt="Question image"
              class="w-full h-full object-cover"
            />
          </div>
          
          <!-- Sentence with clickable blanks -->
          <div class="text-center mb-6 text-xl text-gray-800 leading-relaxed">
            <template v-if="language === 'zh'">
              <span>{{ sentenceParts.before }}</span>
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
              <span>{{ sentenceParts.middle }}</span>
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
              <span>{{ sentenceParts.after }}</span>
            </template>
            <template v-else>
              <span>{{ sentencePartsEn.before }}</span>
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
              <span>{{ sentencePartsEn.middle }}</span>
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
              <span>{{ sentencePartsEn.after }}</span>
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
          
          <!-- Options - 4 words -->
          <div class="flex flex-wrap justify-center gap-3 mb-6">
            <button
              v-for="option in shuffledOptions"
              :key="option.word"
              @click="selectOption(option)"
              :disabled="isAnswered"
              :class="[
                'px-5 py-2 rounded-lg border-2 transition-all font-medium',
                isOptionUsed(option.word)
                  ? (isAnswered && correctAnswers.includes(option.word)
                      ? 'border-green-500 bg-green-100 text-green-700'
                      : (isAnswered && !correctAnswers.includes(option.word)
                          ? 'border-gray-300 bg-gray-100 text-gray-500'
                          : 'border-mint-500 bg-mint-100 text-mint-700 cursor-pointer'))
                  : 'border-gray-200 bg-white text-gray-700 hover:border-mint-400 hover:bg-mint-50',
                isAnswered && correctAnswers.includes(option.word) && !isOptionUsed(option.word) ? 'border-green-500 bg-green-50' : ''
              ]"
            >
              {{ option.word }}
              <span v-if="isAnswered" class="text-xs text-gray-500 ml-1">{{ option.meaning }}</span>
            </button>
          </div>
          
          <div class="flex justify-center">
            <button
              v-if="!isAnswered"
              @click="checkAnswer"
              :disabled="filledBlanks.includes(null)"
              class="px-6 py-3 bg-mint-500 text-white rounded-xl hover:bg-mint-600 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium transition-colors"
            >
              检查答案
            </button>
            <button
              v-else
              @click="nextQuestion"
              class="px-6 py-3 bg-mint-500 text-white rounded-xl hover:bg-mint-600 font-medium transition-colors"
            >
              {{ questionIndex < clozeQuestions.length - 1 ? '下一题' : '查看结果' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { testApi } from '../../api'

const router = useRouter()

const wordQuestions = ref([])
const clozeQuestions = ref([])
const questionIndex = ref(0)
const language = ref('zh')
const filledBlanks = ref([null, null])
const isAnswered = ref(false)

const currentQuestion = computed(() => {
  return clozeQuestions.value[questionIndex.value]
})

const sentenceParts = computed(() => {
  const sentence = currentQuestion.value?.sentence || ''
  if (!sentence) return { before: '', middle: '', after: '' }
  const parts = sentence.split('___')
  if (parts.length >= 3) {
    return { before: parts[0], middle: parts[1], after: parts.slice(2).join('___') }
  }
  return { before: sentence, middle: '', after: '' }
})

const sentencePartsEn = computed(() => {
  const sentence = currentQuestion.value?.sentence_en || currentQuestion.value?.sentence || ''
  if (!sentence) return { before: '', middle: '', after: '' }
  const parts = sentence.split('___')
  if (parts.length >= 3) {
    return { before: parts[0], middle: parts[1], after: parts.slice(2).join('___') }
  }
  return { before: sentence, middle: '', after: '' }
})

const shuffledOptions = computed(() => {
  if (!currentQuestion.value) return []
  const options = [
    { word: currentQuestion.value.word1, meaning: currentQuestion.value.word1_meaning },
    { word: currentQuestion.value.word2, meaning: currentQuestion.value.word2_meaning },
    { word: currentQuestion.value.distractor1, meaning: currentQuestion.value.distractor1_meaning },
    { word: currentQuestion.value.distractor2, meaning: currentQuestion.value.distractor2_meaning }
  ].filter(o => o.word)
  return [...options].sort(() => Math.random() - 0.5)
})

const correctAnswers = computed(() => {
  if (!currentQuestion.value) return []
  return [currentQuestion.value.word1, currentQuestion.value.word2]
})

const isOptionUsed = (word) => {
  return filledBlanks.value.includes(word)
}

const selectOption = (option) => {
  if (isAnswered.value) return
  
  // If the option is already used, remove it from the blank (toggle off)
  const usedIndex = filledBlanks.value.indexOf(option.word)
  if (usedIndex !== -1) {
    const newBlanks = [...filledBlanks.value]
    newBlanks[usedIndex] = null
    filledBlanks.value = newBlanks
    return
  }
  
  // Otherwise, find first empty blank and fill it
  const firstEmptyIndex = filledBlanks.value.indexOf(null)
  if (firstEmptyIndex !== -1) {
    const newBlanks = [...filledBlanks.value]
    newBlanks[firstEmptyIndex] = option.word
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
  if (filledBlanks.value.includes(null)) return
  isAnswered.value = true
  
  // Record result in sessionStorage
  const isCorrect = correctAnswers.value.every(a => filledBlanks.value.includes(a))
  const storedResults = JSON.parse(sessionStorage.getItem('clozeResults') || '[]')
  storedResults.push({
    cloze_test_id: currentQuestion.value.id,
    sentence: currentQuestion.value.sentence,
    selected_answer1: filledBlanks.value[0],
    selected_answer2: filledBlanks.value[1],
    correct_answer1: correctAnswers.value[0],
    correct_answer2: correctAnswers.value[1],
    is_correct: isCorrect
  })
  sessionStorage.setItem('clozeResults', JSON.stringify(storedResults))
}

const nextQuestion = () => {
  if (questionIndex.value < clozeQuestions.value.length - 1) {
    questionIndex.value++
    filledBlanks.value = [null, null]
    isAnswered.value = false
  } else {
    // Submit results and go to result page
    submitResults()
  }
}

const submitResults = async () => {
  const wordResults = JSON.parse(sessionStorage.getItem('wordResults') || '[]')
  const clozeResults = JSON.parse(sessionStorage.getItem('clozeResults') || '[]')
  const testData = JSON.parse(sessionStorage.getItem('testData') || '{}')
  
  const totalQuestions = wordResults.length + clozeResults.length
  const correctCount =
    wordResults.filter(r => r.is_correct).length +
    clozeResults.filter(r => r.is_correct).length
  
  // Build wrong questions list
  const wrongQuestions = []
  
  // Add wrong word questions
  wordResults.filter(r => !r.is_correct).forEach(r => {
    wrongQuestions.push({
      question_type: 'word',
      question_id: r.word_set_id,
      main_word: r.main_word,
      selected_answer: r.selected_word,
      correct_answer: r.correct_word
    })
  })
  
  // Add wrong cloze questions
  clozeResults.filter(r => !r.is_correct).forEach(r => {
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
      quiz_set_id: testData.quizSetId || 2,
      total_questions: totalQuestions,
      correct_answers: correctCount,
      word_results: wordResults,
      cloze_results: clozeResults,
      wrong_questions: wrongQuestions
    })
    
    // Store results for result page
    sessionStorage.setItem('testResults', JSON.stringify({
      total: totalQuestions,
      correct: correctCount,
      wordResults: wordResults,
      clozeResults: clozeResults,
      wrongQuestions: wrongQuestions
    }))
    
    router.push({ name: 'test-result' })
  } catch (e) {
    console.error(e)
    // Still navigate to results even if API fails
    sessionStorage.setItem('testResults', JSON.stringify({
      total: totalQuestions,
      correct: correctCount,
      wordResults: wordResults,
      clozeResults: clozeResults,
      wrongQuestions: wrongQuestions
    }))
    router.push({ name: 'test-result' })
  }
}

onMounted(() => {
  // Get test data from session storage
  const testData = sessionStorage.getItem('testData')
  if (!testData) {
    router.push({ name: 'home' })
    return
  }
  
  const data = JSON.parse(testData)
  wordQuestions.value = data.wordQuestions || []
  clozeQuestions.value = data.clozeQuestions || []
})
</script>
