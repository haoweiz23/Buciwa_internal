<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-800">题集管理</h1>
      <button
        @click="showCreateModal = true"
        class="px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors"
      >
        + 新建题集
      </button>
    </div>
    
    <!-- Loading -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="inline-block w-8 h-8 border-4 border-gray-200 border-t-indigo-500 rounded-full animate-spin"></div>
      <p class="text-gray-500 mt-2">加载中...</p>
    </div>
    
    <!-- Empty -->
    <div v-else-if="quizSets.length === 0" class="text-center py-12 bg-white rounded-xl">
      <div class="text-6xl mb-4">📚</div>
      <p class="text-gray-500">还没有题集</p>
    </div>
    
    <!-- List -->
    <div v-else class="space-y-4">
      <div
        v-for="qs in quizSets"
        :key="qs.id"
        class="bg-white rounded-xl shadow overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
        @click="goToDetail(qs.id)"
      >
        <div class="p-4 flex items-center justify-between">
          <div class="flex items-center">
            <div
              :class="[
                'w-3 h-3 rounded-full mr-3',
                qs.is_active ? 'bg-green-500' : 'bg-gray-300'
              ]"
            ></div>
            <div>
              <h3 class="font-bold text-gray-800">{{ qs.name }}</h3>
              <p class="text-gray-400 text-xs mt-1">
                {{ qs.word_count }} 道单选 · {{ qs.cloze_count }} 道完形填空
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button
              v-if="!qs.is_active"
              @click.stop="activateQuizSet(qs.id)"
              class="px-3 py-1 bg-green-100 text-green-600 rounded hover:bg-green-200 text-sm"
            >
              激活
            </button>
            <span v-else class="px-3 py-1 bg-green-500 text-white rounded text-sm">
              当前激活
            </span>
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
        <h2 class="text-xl font-bold text-gray-800 mb-4">创建新题集</h2>
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-medium mb-2">题集名称</label>
          <input
            v-model="newQuizSetName"
            type="text"
            class="w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-indigo-400 focus:outline-none"
            placeholder="输入题集名称..."
          />
        </div>
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-medium mb-2">描述（可选）</label>
          <textarea
            v-model="newQuizSetDesc"
            rows="3"
            class="w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-indigo-400 focus:outline-none resize-none"
            placeholder="输入题集描述..."
          ></textarea>
        </div>
        <div class="flex gap-3">
          <button
            @click="showCreateModal = false"
            class="flex-1 px-4 py-3 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
          >
            取消
          </button>
          <button
            @click="createQuizSet"
            :disabled="!newQuizSetName.trim()"
            class="flex-1 px-4 py-3 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 disabled:bg-gray-300 transition-colors"
          >
            创建
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { quizSetApi } from '../../api'

const router = useRouter()

const quizSets = ref([])
const isLoading = ref(false)
const showCreateModal = ref(false)
const newQuizSetName = ref('')
const newQuizSetDesc = ref('')

const fetchQuizSets = async () => {
  isLoading.value = true
  try {
    quizSets.value = await quizSetApi.list()
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const createQuizSet = async () => {
  if (!newQuizSetName.value.trim()) return
  
  try {
    const result = await quizSetApi.create({
      name: newQuizSetName.value.trim(),
      description: newQuizSetDesc.value.trim() || null
    })
    showCreateModal.value = false
    newQuizSetName.value = ''
    newQuizSetDesc.value = ''
    await fetchQuizSets()
    router.push({ name: 'admin-quiz-set-detail', params: { id: result.id } })
  } catch (e) {
    console.error(e)
  }
}

const activateQuizSet = async (id) => {
  try {
    await quizSetApi.activate(id)
    await fetchQuizSets()
  } catch (e) {
    console.error(e)
  }
}

const goToDetail = (id) => {
  router.push({ name: 'admin-quiz-set-detail', params: { id } })
}

onMounted(() => {
  fetchQuizSets()
})
</script>
