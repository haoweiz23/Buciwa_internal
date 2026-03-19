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
        class="bg-white rounded-xl shadow overflow-hidden hover:shadow-md transition-shadow cursor-pointer relative group"
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
        <!-- Delete Button -->
        <button
          @click.stop="deleteWordSet(ws.id)"
          class="absolute top-2 right-2 p-1.5 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 hover:bg-red-600 transition-all shadow-lg"
          title="删除"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
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
        
        <div class="flex flex-col gap-3">
          <button
            @click="generateWord"
            :disabled="!newWord.trim() || isGenerating"
            class="w-full px-4 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 transition-colors"
          >
            {{ isGenerating ? '生成中...' : 'AI 生成' }}
          </button>
          
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-200"></div>
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-2 bg-white text-gray-500">或者</span>
            </div>
          </div>
          
          <button
            @click="goToManualCreate"
            class="w-full px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors border-2 border-gray-200"
          >
            手动创建（自行上传单词和图片）
          </button>
          
          <button
            @click="showCreateModal = false"
            class="w-full px-4 py-2 text-gray-500 hover:text-gray-700 transition-colors text-sm"
          >
            取消
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

const goToManualCreate = () => {
  showCreateModal.value = false
  router.push({ name: 'admin-word-manual-create' })
}

const deleteWordSet = async (id) => {
  if (!confirm('确定要删除这道单选题吗？此操作不可撤销。')) return
  try {
    await wordSetApi.delete(id)
    await fetchWordSets()
  } catch (e) {
    console.error(e)
    alert('删除失败')
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchWordSets()
})
</script>
