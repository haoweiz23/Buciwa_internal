<template>
  <div class="min-h-screen p-3 sm:p-4 md:p-8">
    <!-- Header -->
    <header class="max-w-4xl mx-auto mb-4 sm:mb-6">
      <div class="flex items-center justify-between">
        <!-- Back Button -->
        <button
          @click="goBack"
          class="flex items-center gap-1 sm:gap-2 px-2 sm:px-4 py-2 rounded-xl
                 bg-white shadow-soft text-mint-600
                 hover:bg-mint-50 transition-colors
                 active:scale-95 touch-manipulation"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 12H5"/>
            <path d="M12 19l-7-7 7-7"/>
          </svg>
          <span class="hidden sm:inline">返回</span>
        </button>

        <!-- Title -->
        <h1 class="text-lg sm:text-xl md:text-2xl font-bold text-mint-700 text-center flex-1 px-2 truncate">
          {{ wordSet?.main_word || '加载中...' }}
        </h1>

        <!-- Placeholder for symmetry -->
        <div class="w-10 sm:w-20 md:w-24"></div>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex flex-col items-center justify-center py-20">
      <div class="w-12 h-12 border-4 border-mint-200 border-t-mint-500 rounded-full spinner"></div>
      <p class="text-mint-600 mt-4">加载单词详情中...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-20">
      <div class="text-6xl mb-4">😕</div>
      <p class="text-red-500">{{ error }}</p>
      <button
        @click="fetchWordSet"
        class="mt-4 px-6 py-2 bg-mint-500 text-white rounded-xl
               hover:bg-mint-600 transition-colors"
      >
        重试
      </button>
    </div>

    <!-- Word Grid -->
    <div v-else-if="wordSet" class="max-w-4xl mx-auto px-1 sm:px-0">
      <!-- 2x2 Grid - responsive -->
      <div class="grid grid-cols-2 gap-2 sm:gap-4 md:gap-6">
        <WordImageCard
          v-for="word in sortedWords"
          :key="word.id"
          :word="word"
          :isRegenerating="regeneratingImages[word.id]"
          @regenerate="regenerateImage"
        />
      </div>

      <!-- Regenerate All Button -->
      <div class="flex justify-center mt-6 sm:mt-8">
        <button
          @click="regenerateAll"
          :disabled="isRegeneratingAll"
          class="flex items-center gap-2 px-4 sm:px-6 py-2.5 sm:py-3
                 bg-gradient-to-r from-mint-400 to-mint-500
                 text-white rounded-xl sm:rounded-2xl shadow-card
                 hover:from-mint-500 hover:to-mint-600
                 disabled:opacity-50 disabled:cursor-not-allowed
                 transition-all active:scale-95 touch-manipulation
                 text-sm sm:text-base"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            :class="{ 'spinner': isRegeneratingAll }"
            class="sm:w-5 sm:h-5"
          >
            <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
            <path d="M3 3v5h5"/>
            <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/>
            <path d="M16 16h5v5"/>
          </svg>
          <span v-if="!isRegeneratingAll">重新生成全部</span>
          <span v-else>生成中...</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { wordSetApi, wordApi } from '../api'
import WordImageCard from '../components/WordImageCard.vue'

const router = useRouter()
const route = useRoute()

// State
const wordSet = ref(null)
const isLoading = ref(true)
const error = ref('')
const regeneratingImages = ref({})
const isRegeneratingAll = ref(false)

// Word type order for display
const wordTypeOrder = ['main', 'similar', 'synonym', 'antonym']

// Computed
const sortedWords = computed(() => {
  if (!wordSet.value?.words) return []
  
  return [...wordSet.value.words].sort((a, b) => {
    return wordTypeOrder.indexOf(a.word_type) - wordTypeOrder.indexOf(b.word_type)
  })
})

// Methods
const fetchWordSet = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    wordSet.value = await wordSetApi.get(route.params.id)
  } catch (e) {
    error.value = '加载单词详情失败。'
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const goBack = () => {
  router.push({ name: 'list' })
}

const regenerateImage = async (wordId) => {
  regeneratingImages.value[wordId] = true
  
  try {
    const updatedWord = await wordApi.regenerateImage(wordId)
    
    // Update the word in the local state
    const index = wordSet.value.words.findIndex(w => w.id === wordId)
    if (index !== -1) {
      wordSet.value.words[index] = updatedWord
    }
  } catch (e) {
    console.error('Failed to regenerate image:', e)
    alert('重新生成图片失败，请重试。')
  } finally {
    regeneratingImages.value[wordId] = false
  }
}

const regenerateAll = async () => {
  isRegeneratingAll.value = true
  
  try {
    const result = await wordSetApi.regenerate(wordSet.value.id)
    wordSet.value = result
  } catch (e) {
    console.error('Failed to regenerate all:', e)
    alert('重新生成单词失败，请重试。')
  } finally {
    isRegeneratingAll.value = false
  }
}

// Lifecycle
onMounted(() => {
  fetchWordSet()
})
</script>
