<template>
  <div class="min-h-screen p-3 sm:p-4 md:p-8">
    <!-- Header -->
    <header class="max-w-4xl mx-auto mb-6 sm:mb-8">
      <div class="flex items-center justify-between">
        <button
          @click="goHome"
          class="px-4 py-2 text-mint-600 hover:text-mint-700 flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          返回首页
        </button>
        <h1 class="text-xl sm:text-2xl font-bold text-mint-700">单词记忆列表</h1>
        <button
          @click="goToCreate"
          class="px-4 py-2 bg-mint-500 text-white rounded-lg
                 hover:bg-mint-600 transition-colors text-sm font-medium"
        >
          + 新建
        </button>
      </div>
    </header>

    <!-- Content -->
    <div class="max-w-4xl mx-auto">
      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="inline-block w-8 h-8 border-4 border-mint-200 border-t-mint-500 rounded-full spinner"></div>
        <p class="text-mint-600 mt-2">加载中...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="wordSets.length === 0" class="text-center py-12">
        <div class="text-6xl mb-4">📚</div>
        <p class="text-mint-600 text-lg mb-4">还没有单词题目</p>
        <button
          @click="goToCreate"
          class="px-6 py-3 bg-mint-500 text-white rounded-xl
                 hover:bg-mint-600 transition-colors font-medium"
        >
          创建第一个题目
        </button>
      </div>

      <!-- List -->
      <div v-else class="space-y-4">
        <div
          v-for="wordSet in wordSets"
          :key="wordSet.id"
          class="bg-white rounded-2xl shadow-soft overflow-hidden
                 hover:shadow-md transition-shadow cursor-pointer"
          @click="goToDetail(wordSet.id)"
        >
          <div class="flex">
            <!-- Thumbnail -->
            <div class="w-32 h-32 flex-shrink-0 bg-gray-100">
              <img
                v-if="wordSet.main_word_image"
                :src="wordSet.main_word_image"
                alt="Thumbnail"
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>

            <!-- Content -->
            <div class="flex-1 p-4">
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <h3 class="text-lg font-bold text-gray-800 mb-1">
                    {{ wordSet.main_word }}
                  </h3>
                  <p class="text-gray-400 text-xs">
                    {{ formatDate(wordSet.created_at) }}
                  </p>
                </div>
                <button
                  @click.stop="deleteWordSet(wordSet.id)"
                  class="p-2 text-gray-400 hover:text-red-500 transition-colors"
                  title="删除"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showCreateModal = false"
    >
      <div class="bg-white rounded-2xl p-6 w-full max-w-md">
        <h2 class="text-xl font-bold text-mint-700 mb-4">创建新单词题目</h2>
        <div class="flex gap-2 mb-4">
          <input
            v-model="newWord"
            type="text"
            placeholder="输入单词..."
            class="flex-1 px-4 py-3 rounded-xl border-2 border-mint-200
                   focus:border-mint-400 focus:outline-none
                   text-gray-700 placeholder-gray-400
                   transition-colors"
            @keyup.enter="generateWord"
            :disabled="isGenerating"
          />
          <button
            @click="rollDice"
            :disabled="isRolling || isGenerating"
            class="px-4 py-3 bg-amber-500 text-white rounded-xl
                   hover:bg-amber-600 disabled:bg-gray-300
                   disabled:cursor-not-allowed
                   transition-colors font-medium
                   flex items-center justify-center"
            title="随机单词"
          >
            <svg v-if="!isRolling" class="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm0-4c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm0-4c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm4 8c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm0-4c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm0-4c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zM8 17c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm0-4c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm0-4c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1z"/>
            </svg>
            <svg v-else class="w-6 h-6 spinner" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm0-4c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm0-4c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm4 8c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm0-4c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm0-4c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zM8 17c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm0-4c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm0-4c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1z"/>
            </svg>
          </button>
        </div>
        <p v-if="error" class="mb-4 text-red-500 text-sm text-center">
          {{ error }}
        </p>
        <div class="flex gap-3">
          <button
            @click="showCreateModal = false"
            class="flex-1 px-4 py-3 bg-gray-100 text-gray-600 rounded-xl
                   hover:bg-gray-200 transition-colors font-medium"
          >
            取消
          </button>
          <button
            @click="generateWord"
            :disabled="!newWord.trim() || isGenerating"
            class="flex-1 px-4 py-3 bg-mint-500 text-white rounded-xl
                   hover:bg-mint-600 disabled:bg-gray-300
                   disabled:cursor-not-allowed
                   transition-colors font-medium
                   flex items-center justify-center gap-2"
          >
            <span v-if="!isGenerating">生成</span>
            <span v-else class="flex items-center gap-2">
              <svg class="w-5 h-5 spinner" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              生成中
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { wordSetApi } from '../api'

const router = useRouter()

// State
const wordSets = ref([])
const isLoading = ref(false)
const error = ref('')
const showCreateModal = ref(false)
const newWord = ref('')
const isGenerating = ref(false)
const isRolling = ref(false)

// Methods
const fetchWordSets = async () => {
  isLoading.value = true
  error.value = ''
  try {
    wordSets.value = await wordSetApi.list()
  } catch (e) {
    error.value = '加载题目失败，请重试。'
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const deleteWordSet = async (id) => {
  if (!confirm('确定要删除这个题目吗？')) return
  
  try {
    await wordSetApi.delete(id)
    wordSets.value = wordSets.value.filter(ws => ws.id !== id)
  } catch (e) {
    error.value = '删除题目失败。'
    console.error(e)
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const goHome = () => {
  router.push({ name: 'list' })
}

const goToCreate = () => {
  showCreateModal.value = true
}

const goToDetail = (id) => {
  router.push({ name: 'detail', params: { id } })
}

const rollDice = async () => {
  isRolling.value = true
  error.value = ''
  try {
    const result = await wordSetApi.getRandomWord()
    newWord.value = result.word
  } catch (e) {
    error.value = '获取随机单词失败，请重试。'
    console.error(e)
  } finally {
    isRolling.value = false
  }
}

const generateWord = async () => {
  if (!newWord.value.trim()) return
  
  isGenerating.value = true
  error.value = ''
  
  try {
    const result = await wordSetApi.generate(newWord.value.trim())
    showCreateModal.value = false
    newWord.value = ''
    // Refresh the list and go to detail
    await fetchWordSets()
    router.push({ name: 'detail', params: { id: result.id } })
  } catch (e) {
    error.value = '生成单词失败，请重试。'
    console.error(e)
  } finally {
    isGenerating.value = false
  }
}

// Lifecycle
onMounted(() => {
  fetchWordSets()
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
