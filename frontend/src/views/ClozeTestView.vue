<template>
  <div class="min-h-screen p-3 sm:p-4 md:p-8">
    <!-- Header -->
    <header class="max-w-4xl mx-auto mb-6 sm:mb-8">
      <div class="flex items-center justify-between">
        <button
          @click="goBack"
          class="px-4 py-2 text-mint-600 hover:text-mint-700 flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          返回
        </button>
        <h1 class="text-xl sm:text-2xl font-bold text-mint-700">完形填空</h1>
        <div class="w-16"></div>
      </div>
    </header>

    <!-- Input Section -->
    <div class="max-w-2xl mx-auto mb-6 md:mb-8 px-2 sm:px-0">
      <div class="bg-white rounded-2xl shadow-soft p-4 sm:p-6">
        <div class="space-y-4">
          <div class="flex flex-col sm:flex-row gap-3">
            <input
              v-model="word1"
              type="text"
              placeholder="输入第一个英文单词..."
              class="flex-1 px-4 py-3 rounded-xl border-2 border-mint-200
                     focus:border-mint-400 focus:outline-none
                     text-gray-700 placeholder-gray-400
                     transition-colors text-base"
              :disabled="isGenerating"
            />
            <input
              v-model="word2"
              type="text"
              placeholder="输入第二个英文单词..."
              class="flex-1 px-4 py-3 rounded-xl border-2 border-mint-200
                     focus:border-mint-400 focus:outline-none
                     text-gray-700 placeholder-gray-400
                     transition-colors text-base"
              :disabled="isGenerating"
            />
          </div>
          <button
            @click="generateClozeTest"
            :disabled="!word1.trim() || !word2.trim() || isGenerating"
            class="w-full px-6 py-3 bg-mint-500 text-white rounded-xl
                   hover:bg-mint-600 disabled:bg-gray-300
                   disabled:cursor-not-allowed
                   transition-colors font-medium
                   flex items-center justify-center gap-2"
          >
            <span v-if="!isGenerating">生成题目</span>
            <span v-else class="flex items-center gap-2">
              <svg class="w-5 h-5 spinner" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              生成中...
            </span>
          </button>
        </div>
        <p v-if="error" class="mt-3 text-red-500 text-sm text-center">
          {{ error }}
        </p>
      </div>
    </div>

    <!-- Result Section -->
    <div v-if="clozeTest" class="max-w-2xl mx-auto px-2 sm:px-0">
      <!-- Image -->
      <div v-if="clozeTest.image_local_path" class="mb-6">
        <img
          :src="clozeTest.image_local_path"
          alt="Cloze test image"
          class="w-full rounded-2xl shadow-soft"
        />
      </div>

      <!-- Sentence -->
      <div class="bg-white rounded-2xl shadow-soft p-6 mb-6">
        <h3 class="text-lg font-semibold text-mint-700 mb-4">题目</h3>
        <p class="text-xl text-gray-800 leading-relaxed">
          <template v-for="(part, index) in sentenceParts" :key="index">
            <span v-if="part.type === 'text'">{{ part.content }}</span>
            <span
              v-else
              class="inline-block min-w-[100px] px-3 py-1 mx-1 rounded-lg border-2 border-dashed cursor-pointer transition-all"
              :class="filledWords[part.blankIndex] 
                ? 'bg-mint-100 border-mint-400 text-mint-700' 
                : 'border-gray-300 text-gray-400'"
              @click="clearBlank(part.blankIndex)"
            >
              {{ filledWords[part.blankIndex] || `___${part.blankIndex + 1}___` }}
            </span>
          </template>
        </p>
      </div>

      <!-- Word Cards -->
      <div class="bg-white rounded-2xl shadow-soft p-6">
        <h3 class="text-lg font-semibold text-mint-700 mb-4">选择单词填空</h3>
        <div class="flex flex-wrap gap-3">
          <button
            v-for="(word, index) in availableWords"
            :key="index"
            @click="selectWord(word, index)"
            :disabled="isWordUsed(index)"
            class="px-6 py-3 rounded-xl font-medium transition-all"
            :class="isWordUsed(index)
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
              : 'bg-mint-500 text-white hover:bg-mint-600 shadow-soft hover:shadow-md'"
          >
            {{ word }}
          </button>
        </div>
      </div>

      <!-- Check Answer -->
      <div class="mt-6 text-center">
        <button
          v-if="isAllFilled"
          @click="checkAnswer"
          class="px-8 py-3 bg-amber-500 text-white rounded-xl
                 hover:bg-amber-600 transition-colors font-medium"
        >
          查看答案
        </button>
      </div>

      <!-- Answer -->
      <div v-if="showAnswer" class="mt-6 bg-mint-50 rounded-2xl p-6">
        <h3 class="text-lg font-semibold text-mint-700 mb-2">正确答案</h3>
        <p class="text-gray-700 mb-4">{{ clozeTest.sentence_with_answers }}</p>
        <!-- Word Meanings -->
        <div v-if="clozeTest.word1_meaning || clozeTest.word2_meaning" class="mt-4 pt-4 border-t border-mint-200">
          <h4 class="text-md font-semibold text-mint-600 mb-3">单词释义</h4>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div v-if="clozeTest.word1_meaning" class="flex items-center gap-2 bg-white px-4 py-3 rounded-xl">
              <span class="font-medium text-mint-700">{{ clozeTest.word1 }}</span>
              <span class="text-gray-400">-</span>
              <span class="text-gray-600">{{ clozeTest.word1_meaning }}</span>
            </div>
            <div v-if="clozeTest.word2_meaning" class="flex items-center gap-2 bg-white px-4 py-3 rounded-xl">
              <span class="font-medium text-mint-700">{{ clozeTest.word2 }}</span>
              <span class="text-gray-400">-</span>
              <span class="text-gray-600">{{ clozeTest.word2_meaning }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { clozeTestApi } from '../api'

const router = useRouter()
const route = useRoute()

// State
const word1 = ref('')
const word2 = ref('')
const isGenerating = ref(false)
const isLoading = ref(false)
const error = ref('')
const clozeTest = ref(null)
const filledWords = ref({})
const showAnswer = ref(false)

// Computed
const availableWords = computed(() => {
  if (!clozeTest.value) return []
  // Shuffle the words
  const words = [clozeTest.value.word1, clozeTest.value.word2]
  return words.sort(() => Math.random() - 0.5)
})

const sentenceParts = computed(() => {
  if (!clozeTest.value) return []
  
  const sentence = clozeTest.value.sentence
  const parts = []
  let lastIndex = 0
  let blankIndex = 0
  
  // Match ___1___ and ___2___ patterns
  const regex = /___(\d)___/g
  let match
  
  while ((match = regex.exec(sentence)) !== null) {
    // Add text before the blank
    if (match.index > lastIndex) {
      parts.push({
        type: 'text',
        content: sentence.slice(lastIndex, match.index)
      })
    }
    // Add the blank
    parts.push({
      type: 'blank',
      blankIndex: parseInt(match[1]) - 1
    })
    blankIndex++
    lastIndex = match.index + match[0].length
  }
  
  // Add remaining text
  if (lastIndex < sentence.length) {
    parts.push({
      type: 'text',
      content: sentence.slice(lastIndex)
    })
  }
  
  return parts
})

const isAllFilled = computed(() => {
  if (!clozeTest.value) return false
  return filledWords.value[0] && filledWords.value[1]
})

// Methods
const usedWordIndices = ref(new Set())

const isWordUsed = (index) => {
  return usedWordIndices.value.has(index)
}

const selectWord = (word, index) => {
  if (isWordUsed(index)) return
  
  // Find the first empty blank
  if (!filledWords.value[0]) {
    filledWords.value[0] = word
    usedWordIndices.value.add(index)
  } else if (!filledWords.value[1]) {
    filledWords.value[1] = word
    usedWordIndices.value.add(index)
  }
}

const clearBlank = (blankIndex) => {
  const word = filledWords.value[blankIndex]
  if (word) {
    // Find the index of this word in availableWords and remove from used set
    const wordIndex = availableWords.value.findIndex((w, i) => w === word && usedWordIndices.value.has(i))
    if (wordIndex !== -1) {
      usedWordIndices.value.delete(wordIndex)
    }
    filledWords.value[blankIndex] = null
    showAnswer.value = false
  }
}

const generateClozeTest = async () => {
  if (!word1.value.trim() || !word2.value.trim()) return
  
  isGenerating.value = true
  error.value = ''
  clozeTest.value = null
  filledWords.value = {}
  usedWordIndices.value = new Set()
  showAnswer.value = false
  
  try {
    const result = await clozeTestApi.generate(word1.value.trim(), word2.value.trim())
    clozeTest.value = result
  } catch (e) {
    error.value = '生成题目失败，请重试。'
    console.error(e)
  } finally {
    isGenerating.value = false
  }
}

const loadClozeTest = async (id) => {
  isLoading.value = true
  error.value = ''
  try {
    clozeTest.value = await clozeTestApi.get(id)
  } catch (e) {
    error.value = '加载题目失败，请重试。'
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const checkAnswer = () => {
  showAnswer.value = true
}

const goBack = () => {
  router.push({ name: 'cloze-list' })
}

// Lifecycle
onMounted(async () => {
  const id = route.params.id
  if (id) {
    // Load existing test
    await loadClozeTest(id)
  }
})
</script>

<style scoped>
.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
