<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-800">单选题管理</h1>
      <button
        @click="showCreateModal = true"
        class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
      >
        + 新建题目
      </button>
    </div>
    
    <!-- Loading -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="inline-block w-8 h-8 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin"></div>
      <p class="text-gray-500 mt-2">加载中...</p>
    </div>
    
    <!-- Empty -->
    <div v-else-if="wordSets.length === 0" class="text-center py-12 bg-white rounded-xl">
      <div class="text-6xl mb-4">📝</div>
      <p class="text-gray-500">还没有单选题</p>
    </div>
    
    <!-- List -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="ws in wordSets"
        :key="ws.id"
        class="bg-white rounded-xl shadow overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
        @click="goToDetail(ws.id)"
      >
        <div class="flex">
          <div class="w-24 h-24 flex-shrink-0 bg-gray-100">
            <img
              v-if="ws.main_word_image"
              :src="ws.main_word_image"
              alt="Thumbnail"
              class="w-full h-full object-cover"
            />
            <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
          <div class="flex-1 p-3">
            <h3 class="font-bold text-gray-800">{{ ws.main_word }}</h3>
            <p class="text-gray-400 text-xs mt-1">{{ formatDate(ws.created_at) }}</p>
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
      <div class="bg-white rounded-xl p-6 w-full max-w-md">
        <h2 class="text-xl font-bold text-gray-800 mb-4">创建新单选题</h2>
        <div class="flex gap-2 mb-4">
          <input
            v-model="newWord"
            type="text"
            placeholder="输入单词..."
            class="flex-1 px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-blue-400 focus:outline-none"
            @keyup.enter="generateWord"
            :disabled="isGenerating"
          />
          <button
            @click="rollDice"
            :disabled="isRolling || isGenerating"
            class="px-4 py-3 bg-amber-500 text-white rounded-lg hover:bg-amber-600 disabled:bg-gray-300 transition-colors"
          >
            🎲
          </button>
        </div>
        <p v-if="error" class="mb-4 text-red-500 text-sm text-center">{{ error }}</p>
        <div class="flex gap-3">
          <button
            @click="showCreateModal = false"
            class="flex-1 px-4 py-3 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
          >
            取消
          </button>
          <button
            @click="generateWord"
            :disabled="!newWord.trim() || isGenerating"
            class="flex-1 px-4 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 transition-colors"
          >
            {{ isGenerating ? '生成中...' : '生成' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { wordSetApi } from '../../api'

const router = useRouter()

const wordSets = ref([])
const isLoading = ref(false)
const showCreateModal = ref(false)
const newWord = ref('')
const isGenerating = ref(false)
const isRolling = ref(false)
const error = ref('')

const fetchWordSets = async () => {
  isLoading.value = true
  try {
    wordSets.value = await wordSetApi.list()
  } catch (e) {
    error.value = '加载失败'
    console.error(e)
  } finally {
    isLoading.value = false
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
    await fetchWordSets()
    router.push({ name: 'admin-word-detail', params: { id: result.id } })
  } catch (e) {
    error.value = '生成失败，请重试'
    console.error(e)
  } finally {
    isGenerating.value = false
  }
}

const rollDice = async () => {
  isRolling.value = true
  try {
    const result = await wordSetApi.getRandomWord()
    newWord.value = result.word
  } catch (e) {
    console.error(e)
  } finally {
    isRolling.value = false
  }
}

const goToDetail = (id) => {
  router.push({ name: 'admin-word-detail', params: { id } })
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchWordSets()
})
</script>
