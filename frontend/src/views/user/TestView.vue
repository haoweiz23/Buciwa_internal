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
        <span>单选题: {{ wordTypeCount }}</span>
        <span>完形填空: {{ clozeTypeCount }}</span>
        <span>听力题: {{ listeningTypeCount }}</span>
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
                  class="w-full h-full object-contain"
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
        <div v-else-if="currentType === 'cloze'" class="bg-white rounded-2xl shadow-lg p-6">
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
          <div class="w-full bg-gray-100 rounded-lg mb-4 overflow-hidden">
            <img
              v-if="currentQuestion.image_local_path"
              :src="currentQuestion.image_local_path"
              alt="Question"
              class="w-full h-auto object-contain"
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
                        ? (isBlankCorrect(0) ? 'border-green-500 bg-green-50 text-green-700' : 'border-red-500 bg-red-50 text-red-700')
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
                        ? (isBlankCorrect(1) ? 'border-green-500 bg-green-50 text-green-700' : 'border-red-500 bg-red-50 text-red-700')
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
                        ? (isBlankCorrect(0) ? 'border-green-500 bg-green-50 text-green-700' : 'border-red-500 bg-red-50 text-red-700')
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
                        ? (isBlankCorrect(1) ? 'border-green-500 bg-green-50 text-green-700' : 'border-red-500 bg-red-50 text-red-700')
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
                <span class="text-xs text-gray-400 mr-1">空1:</span>
                <span class="font-medium text-green-700">{{ correctAnswerForBlank[0] }}</span>
                <span class="text-sm text-gray-500 ml-2">{{ getWordMeaning(correctAnswerForBlank[0]) }}</span>
              </div>
              <div class="flex-1 p-2 bg-green-50 rounded border border-green-200">
                <span class="text-xs text-gray-400 mr-1">空2:</span>
                <span class="font-medium text-green-700">{{ correctAnswerForBlank[1] }}</span>
                <span class="text-sm text-gray-500 ml-2">{{ getWordMeaning(correctAnswerForBlank[1]) }}</span>
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
        
        <!-- Listening Question -->
        <div v-else-if="currentType === 'listening'" class="bg-white rounded-2xl shadow-lg p-6">
          <!-- Image -->
          <div class="w-full bg-gray-100 rounded-lg mb-4 overflow-hidden">
            <img
              v-if="currentQuestion.image_local_path"
              :src="currentQuestion.image_local_path"
              alt="Listening exercise image"
              class="w-full h-auto object-contain"
            />
          </div>
          
          <!-- Scene Description -->
          <div class="text-center mb-6">
            <h3 class="text-lg font-semibold text-gray-700">{{ currentQuestion.scene_description }}</h3>
          </div>
          
          <!-- Audio Player -->
          <div v-if="currentQuestion.audio_local_path" class="bg-gray-50 rounded-xl p-6 mb-6">
            <h4 class="text-sm font-medium text-gray-600 mb-4 text-center">听力音频</h4>
            <div class="flex flex-col items-center gap-4">
              <audio
                :ref="el => audioPlayerRefs[currentIndex] = el"
                :src="currentQuestion.audio_local_path"
                @ended="onAudioEnded"
                class="hidden"
              ></audio>
              
              <!-- Play/Pause Button -->
              <button
                @click="toggleAudio"
                class="w-20 h-20 rounded-full bg-purple-500 text-white
                       hover:bg-purple-600 transition-colors
                       flex items-center justify-center shadow-lg"
              >
                <svg v-if="!isPlaying" class="w-10 h-10 ml-1" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z"/>
                </svg>
                <svg v-else class="w-10 h-10" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                </svg>
              </button>

              <!-- Loop Toggle -->
              <div class="flex items-center gap-2">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    v-model="isLooping"
                    class="w-4 h-4 text-purple-500 rounded border-gray-300
                           focus:ring-purple-500"
                  />
                  <span class="text-gray-600 text-sm">循环播放</span>
                </label>
              </div>

              <!-- Progress Bar -->
              <div class="w-full">
                <div class="flex justify-between text-sm text-gray-500 mb-1">
                  <span>{{ formatTime(currentTime) }}</span>
                  <span>{{ formatTime(duration) }}</span>
                </div>
                <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    class="h-full bg-purple-500 transition-all duration-100"
                    :style="{ width: `${progress}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Transcript Toggle -->
          <div class="bg-gray-50 rounded-xl p-4 mb-6">
            <div class="flex items-center justify-between">
              <h4 class="text-sm font-medium text-gray-600">听力文本</h4>
              <button
                @click="showTranscript = !showTranscript"
                class="text-purple-600 hover:text-purple-700 text-sm"
              >
                {{ showTranscript ? '隐藏文本' : '显示文本' }}
              </button>
            </div>
            <p v-if="showTranscript" class="text-gray-700 leading-relaxed mt-3">
              {{ currentQuestion.generated_text }}
            </p>
            <p v-else class="text-gray-400 italic mt-3 text-sm">
              点击"显示文本"查看听力内容
            </p>
          </div>
          
          <div class="flex justify-center">
            <button
              @click="markListeningDone"
              class="px-6 py-3 bg-purple-500 text-white rounded-xl hover:bg-purple-600 font-medium"
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { testApi } from '../../api'

const router = useRouter()

const activeTest = ref(null)
const wordQuestions = ref([])
const clozeQuestions = ref([])
const orderedQuestions = ref([])  // 新增：统一排序的题目列表
const currentIndex = ref(0)
const language = ref('zh')

const selectedOption = ref(null)
const filledBlanks = ref([null, null])
const isAnswered = ref(false)
const results = ref({ word: [], cloze: [], listening: [] })

// Store shuffled options per question index to maintain consistency
const shuffledWordOptionsCache = ref({})
const shuffledClozeOptionsCache = ref({})

// Audio player state for listening questions
const audioPlayerRefs = ref({})
const isPlaying = ref(false)
const isLooping = ref(true)
const currentTime = ref(0)
const duration = ref(0)
const progress = ref(0)
const showTranscript = ref(false)

const totalQuestions = computed(() => orderedQuestions.value.length)

const wordTypeCount = computed(() => orderedQuestions.value.filter(q => q.type === 'word').length)
const clozeTypeCount = computed(() => orderedQuestions.value.filter(q => q.type === 'cloze').length)
const listeningTypeCount = computed(() => orderedQuestions.value.filter(q => q.type === 'listening').length)

const currentType = computed(() => {
  const question = orderedQuestions.value[currentIndex.value]
  return question ? question.type : null
})

const currentQuestion = computed(() => {
  const question = orderedQuestions.value[currentIndex.value]
  if (!question) return null
  
  if (question.type === 'word') {
    return question.fullData
  } else if (question.type === 'cloze') {
    return question.fullData
  } else if (question.type === 'listening') {
    return question.fullData
  }
  return null
})

// Fisher-Yates shuffle algorithm for better randomization
const shuffleArray = (array) => {
  const shuffled = [...array]
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
  }
  return shuffled
}

const shuffledOptions = computed(() => {
  if (!currentQuestion.value || currentType.value !== 'word') return []
  
  const idx = currentIndex.value
  // Return cached shuffled options if available
  if (shuffledWordOptionsCache.value[idx]) {
    return shuffledWordOptionsCache.value[idx]
  }
  
  // Create and cache shuffled options
  const options = shuffleArray([...currentQuestion.value.words])
  shuffledWordOptionsCache.value[idx] = options
  return options
})

const shuffledClozeOptionsWithMeanings = computed(() => {
  if (!currentQuestion.value || currentType.value !== 'cloze') return []
  
  const idx = currentIndex.value
  // Return cached shuffled options if available
  if (shuffledClozeOptionsCache.value[idx]) {
    return shuffledClozeOptionsCache.value[idx]
  }
  
  // Create and cache shuffled options
  const options = [
    { word: currentQuestion.value.word1, meaning: currentQuestion.value.word1_meaning },
    { word: currentQuestion.value.word2, meaning: currentQuestion.value.word2_meaning },
    { word: currentQuestion.value.distractor1, meaning: currentQuestion.value.distractor1_meaning },
    { word: currentQuestion.value.distractor2, meaning: currentQuestion.value.distractor2_meaning }
  ].filter(o => o.word)
  
  const shuffled = shuffleArray(options)
  shuffledClozeOptionsCache.value[idx] = shuffled
  return shuffled
})

const correctAnswer = computed(() => {
  if (!currentQuestion.value || currentType.value !== 'word') return null
  return currentQuestion.value.words.find(w => w.word_type === 'main')?.word
})

const correctAnswers = computed(() => {
  if (!currentQuestion.value || currentType.value !== 'cloze') return []
  return [currentQuestion.value.word1, currentQuestion.value.word2]
})

// Parse the sentence_with_answers to determine which word goes in which blank position
const correctAnswerForBlank = computed(() => {
  if (!currentQuestion.value || currentType.value !== 'cloze') return [null, null]
  
  const sentenceWithAnswers = currentQuestion.value.sentence_with_answers || ''
  const sentence = currentQuestion.value.sentence || ''
  const word1 = currentQuestion.value.word1
  const word2 = currentQuestion.value.word2
  
  // Split sentence by ___ to find the parts
  const parts = sentence.split('___')
  if (parts.length < 3) return [word1, word2] // fallback to original order
  
  // The middle part is the text between the two blanks
  const middlePart = parts[1]
  
  // In sentence_with_answers, find where the middle part appears
  const middleIndexInAnswer = sentenceWithAnswers.indexOf(middlePart)
  
  // Determine which word comes before the middle part (first blank) and which comes after (second blank)
  if (middleIndexInAnswer >= 0) {
    const beforeMiddle = sentenceWithAnswers.substring(0, middleIndexInAnswer)
    const afterMiddle = sentenceWithAnswers.substring(middleIndexInAnswer + middlePart.length)
    
    // Check which word is in which section
    const blank1Answer = beforeMiddle.includes(word1) ? word1 : (beforeMiddle.includes(word2) ? word2 : null)
    const blank2Answer = afterMiddle.includes(word1) ? word1 : (afterMiddle.includes(word2) ? word2 : null)
    
    // If we found both answers, return them
    if (blank1Answer && blank2Answer) {
      return [blank1Answer, blank2Answer]
    }
  }
  
  // Alternative approach: find word positions in sentence_with_answers
  // and compare with middle part position
  const word1Index = sentenceWithAnswers.indexOf(word1)
  const word2Index = sentenceWithAnswers.indexOf(word2)
  const midIdx = sentenceWithAnswers.indexOf(middlePart)
  
  if (word1Index >= 0 && word2Index >= 0 && midIdx >= 0) {
    // Word before middle part is blank 1, word after is blank 2
    if (word1Index < midIdx && word2Index > midIdx) {
      return [word1, word2]
    } else if (word2Index < midIdx && word1Index > midIdx) {
      return [word2, word1]
    }
  }
  
  // Fallback: use original order
  return [word1, word2]
})

// Check if a specific blank has the correct answer for that position
const isBlankCorrect = (blankIndex) => {
  if (!filledBlanks.value[blankIndex]) return false
  return filledBlanks.value[blankIndex] === correctAnswerForBlank.value[blankIndex]
}

// Get the meaning for a word
const getWordMeaning = (word) => {
  if (!currentQuestion.value || !word) return ''
  if (word === currentQuestion.value.word1) return currentQuestion.value.word1_meaning || ''
  if (word === currentQuestion.value.word2) return currentQuestion.value.word2_meaning || ''
  if (word === currentQuestion.value.distractor1) return currentQuestion.value.distractor1_meaning || ''
  if (word === currentQuestion.value.distractor2) return currentQuestion.value.distractor2_meaning || ''
  return ''
}

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
    
    // 使用统一排序的题目列表
    if (result.ordered_questions && result.ordered_questions.length > 0) {
      // Fetch full details for each ordered question
      const questionsWithDetails = await Promise.all(
        result.ordered_questions.map(async (q) => {
          let fullData = null
          if (q.type === 'word') {
            fullData = await fetch(`/api/word-sets/${q.item_id}`).then(r => r.json())
          } else if (q.type === 'cloze') {
            fullData = await fetch(`/api/cloze-tests/${q.item_id}`).then(r => r.json())
          } else if (q.type === 'listening') {
            fullData = await fetch(`/api/listening-exercises/${q.item_id}`).then(r => r.json())
          }
          return {
            ...q,
            fullData
          }
        })
      )
      orderedQuestions.value = questionsWithDetails
    } else {
      // Fallback: 使用旧的逻辑（先单选再完形）
      const wordDetails = await Promise.all(
        wordQuestions.value.map(wq => fetch(`/api/word-sets/${wq.id}`).then(r => r.json()))
      )
      wordQuestions.value = wordDetails
      
      const clozeDetails = await Promise.all(
        clozeQuestions.value.map(cq => fetch(`/api/cloze-tests/${cq.id}`).then(r => r.json()))
      )
      clozeQuestions.value = clozeDetails
      
      // 构建orderedQuestions作为回退
      const fallbackOrder = []
      wordDetails.forEach((wq, idx) => {
        fallbackOrder.push({ type: 'word', order: idx, item_id: wq.id, fullData: wq })
      })
      clozeDetails.forEach((cq, idx) => {
        fallbackOrder.push({ type: 'cloze', order: wordDetails.length + idx, item_id: cq.id, fullData: cq })
      })
      orderedQuestions.value = fallbackOrder
    }
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
  
  // Use position-aware verification: each blank must have the correct word for that position
  const isCorrect = isBlankCorrect(0) && isBlankCorrect(1)
  
  results.value.cloze.push({
    cloze_test_id: currentQuestion.value.id,
    sentence: currentQuestion.value.sentence,
    selected_answer1: filledBlanks.value[0],
    selected_answer2: filledBlanks.value[1],
    correct_answer1: correctAnswerForBlank.value[0],
    correct_answer2: correctAnswerForBlank.value[1],
    is_correct: isCorrect
  })
}

const nextQuestion = () => {
  // Stop audio when moving to next question
  stopAudio()
  
  if (currentIndex.value < totalQuestions.value - 1) {
    currentIndex.value++
    selectedOption.value = null
    filledBlanks.value = [null, null]
    isAnswered.value = false
    showTranscript.value = false
    currentTime.value = 0
    duration.value = 0
    progress.value = 0
  } else {
    // Submit results
    submitResults()
  }
}

// Audio player methods for listening questions
const toggleAudio = () => {
  const audioPlayer = audioPlayerRefs.value[currentIndex.value]
  if (!audioPlayer) return
  
  if (isPlaying.value) {
    audioPlayer.pause()
    isPlaying.value = false
  } else {
    audioPlayer.play()
    isPlaying.value = true
  }
}

const stopAudio = () => {
  const audioPlayer = audioPlayerRefs.value[currentIndex.value]
  if (audioPlayer) {
    audioPlayer.pause()
    audioPlayer.currentTime = 0
    isPlaying.value = false
  }
}

const onAudioEnded = () => {
  if (isLooping.value) {
    const audioPlayer = audioPlayerRefs.value[currentIndex.value]
    if (audioPlayer) {
      audioPlayer.currentTime = 0
      audioPlayer.play()
    }
  } else {
    isPlaying.value = false
  }
}

const updateProgress = () => {
  const audioPlayer = audioPlayerRefs.value[currentIndex.value]
  if (!audioPlayer) return
  
  currentTime.value = audioPlayer.currentTime
  duration.value = audioPlayer.duration || 0
  
  if (duration.value > 0) {
    progress.value = (currentTime.value / duration.value) * 100
  }
}

const formatTime = (time) => {
  if (!time || isNaN(time)) return '0:00'
  
  const minutes = Math.floor(time / 60)
  const seconds = Math.floor(time % 60)
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
}

const markListeningDone = () => {
  // Record listening exercise completion
  results.value.listening.push({
    listening_exercise_id: currentQuestion.value.id,
    scene_description: currentQuestion.value.scene_description,
    completed: true
  })
  
  nextQuestion()
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
      listening_results: results.value.listening,
      wrong_questions: wrongQuestions
    })
    
    // Store results for result page
    sessionStorage.setItem('testResults', JSON.stringify({
      total: totalQuestions.value,
      correct: correctCount,
      wordResults: results.value.word,
      clozeResults: results.value.cloze,
      listeningResults: results.value.listening,
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

// Watch for audio player ref changes to add event listeners
watch(currentIndex, (newIdx) => {
  // Reset audio state when question changes
  isPlaying.value = false
  currentTime.value = 0
  duration.value = 0
  progress.value = 0
  showTranscript.value = false
  
  // Setup event listeners for new audio player
  setTimeout(() => {
    const audioPlayer = audioPlayerRefs.value[newIdx]
    if (audioPlayer) {
      audioPlayer.addEventListener('timeupdate', updateProgress)
      audioPlayer.addEventListener('loadedmetadata', () => {
        duration.value = audioPlayer.duration
      })
    }
  }, 100)
})

onMounted(() => {
  fetchActiveTest()
})

onUnmounted(() => {
  // Clean up audio event listeners
  Object.values(audioPlayerRefs.value).forEach(audioPlayer => {
    if (audioPlayer) {
      audioPlayer.pause()
      audioPlayer.removeEventListener('timeupdate', updateProgress)
    }
  })
})
</script>
