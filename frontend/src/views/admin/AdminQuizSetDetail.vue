<template>
  <div class="p-6">
    <div class="flex items-center mb-6">
      <button @click="goBack" class="mr-4 text-gray-500 hover:text-gray-700">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <div class="flex-1">
        <h1 class="text-2xl font-bold text-gray-800">{{ quizSet?.name || '加载中...' }}</h1>
        <p v-if="quizSet?.description" class="text-gray-500 text-sm mt-1">{{ quizSet.description }}</p>
      </div>
      <div class="flex items-center gap-2">
        <span
          :class="[
            'px-3 py-1 rounded text-sm font-medium',
            quizSet?.is_active ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-500'
          ]"
        >
          {{ quizSet?.is_active ? '已激活' : '未激活' }}
        </span>
        <button
          v-if="!quizSet?.is_active"
          @click="activateQuizSet"
          class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
        >
          激活题集
        </button>
      </div>
    </div>
    
    <!-- Loading -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="inline-block w-8 h-8 border-4 border-gray-200 border-t-indigo-500 rounded-full animate-spin"></div>
    </div>
    
    <!-- Content -->
    <div v-else-if="quizSet" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Word Items -->
      <div class="bg-white rounded-xl shadow p-4">
        <div class="flex items-center justify-between mb-4">
          <h2 class="font-bold text-gray-800">单选题 ({{ quizSet.word_set_items.length }})</h2>
          <button
            @click="showAddWordModal = true"
            class="px-3 py-1 bg-blue-100 text-blue-600 rounded hover:bg-blue-200 text-sm"
          >
            + 添加
          </button>
        </div>
        <div v-if="quizSet.word_set_items.length === 0" class="text-center py-8 text-gray-400">
          暂无单选题
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="item in quizSet.word_set_items"
            :key="item.id"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div class="flex items-center">
              <span class="text-gray-400 text-sm mr-3">{{ item.order + 1 }}.</span>
              <span class="font-medium text-gray-800">{{ item.word_set.main_word }}</span>
            </div>
            <button
              @click="removeWordItem(item.id)"
              class="text-red-500 hover:text-red-600 text-sm"
            >
              移除
            </button>
          </div>
        </div>
      </div>
      
      <!-- Cloze Items -->
      <div class="bg-white rounded-xl shadow p-4">
        <div class="flex items-center justify-between mb-4">
          <h2 class="font-bold text-gray-800">完形填空 ({{ quizSet.cloze_items.length }})</h2>
          <button
            @click="showAddClozeModal = true"
            class="px-3 py-1 bg-green-100 text-green-600 rounded hover:bg-green-200 text-sm"
          >
            + 添加
          </button>
        </div>
        <div v-if="quizSet.cloze_items.length === 0" class="text-center py-8 text-gray-400">
          暂无完形填空题
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="item in quizSet.cloze_items"
            :key="item.id"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div class="flex items-center">
              <span class="text-gray-400 text-sm mr-3">{{ item.order + 1 }}.</span>
              <span class="font-medium text-gray-800">{{ item.cloze_test.word1 }} / {{ item.cloze_test.word2 }}</span>
            </div>
            <button
              @click="removeClozeItem(item.id)"
              class="text-red-500 hover:text-red-600 text-sm"
            >
              移除
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Add Word Modal -->
    <div
      v-if="showAddWordModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showAddWordModal = false"
    >
      <div class="bg-white rounded-xl p-6 w-full max-w-lg max-h-[80vh] overflow-auto">
        <h2 class="text-xl font-bold text-gray-800 mb-4">添加单选题</h2>
        <div class="space-y-2">
          <div
            v-for="ws in availableWordSets"
            :key="ws.id"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <span class="font-medium text-gray-800">{{ ws.main_word }}</span>
            <button
              @click="addWordItem(ws.id)"
              class="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
            >
              添加
            </button>
          </div>
        </div>
        <button
          @click="showAddWordModal = false"
          class="mt-4 w-full px-4 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200"
        >
          关闭
        </button>
      </div>
    </div>
    
    <!-- Add Cloze Modal -->
    <div
      v-if="showAddClozeModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showAddClozeModal = false"
    >
      <div class="bg-white rounded-xl p-6 w-full max-w-lg max-h-[80vh] overflow-auto">
        <h2 class="text-xl font-bold text-gray-800 mb-4">添加完形填空题</h2>
        <div class="space-y-2">
          <div
            v-for="ct in availableClozeTests"
            :key="ct.id"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div>
              <span class="font-medium text-gray-800">{{ ct.word1 }} / {{ ct.word2 }}</span>
              <p class="text-gray-400 text-xs mt-1 line-clamp-1">{{ ct.sentence }}</p>
            </div>
            <button
              @click="addClozeItem(ct.id)"
              class="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 text-sm"
            >
              添加
            </button>
          </div>
        </div>
        <button
          @click="showAddClozeModal = false"
          class="mt-4 w-full px-4 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200"
        >
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { quizSetApi, wordSetApi, clozeTestApi } from '../../api'

const router = useRouter()
const route = useRoute()

const quizSet = ref(null)
const isLoading = ref(false)
const showAddWordModal = ref(false)
const showAddClozeModal = ref(false)
const allWordSets = ref([])
const allClozeTests = ref([])

const availableWordSets = computed(() => {
  if (!quizSet.value) return []
  const addedIds = new Set(quizSet.value.word_set_items.map(i => i.word_set_id))
  return allWordSets.value.filter(ws => !addedIds.has(ws.id))
})

const availableClozeTests = computed(() => {
  if (!quizSet.value) return []
  const addedIds = new Set(quizSet.value.cloze_items.map(i => i.cloze_test_id))
  return allClozeTests.value.filter(ct => !addedIds.has(ct.id))
})

const fetchQuizSet = async () => {
  isLoading.value = true
  try {
    quizSet.value = await quizSetApi.get(route.params.id)
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const fetchAllItems = async () => {
  try {
    const [words, clozes] = await Promise.all([
      wordSetApi.list(),
      clozeTestApi.list()
    ])
    allWordSets.value = words
    allClozeTests.value = clozes
  } catch (e) {
    console.error(e)
  }
}

const activateQuizSet = async () => {
  try {
    await quizSetApi.activate(quizSet.value.id)
    await fetchQuizSet()
  } catch (e) {
    console.error(e)
  }
}

const addWordItem = async (wordSetId) => {
  try {
    await quizSetApi.addWord(quizSet.value.id, wordSetId)
    await fetchQuizSet()
  } catch (e) {
    console.error(e)
  }
}

const removeWordItem = async (itemId) => {
  try {
    await quizSetApi.removeWord(quizSet.value.id, itemId)
    await fetchQuizSet()
  } catch (e) {
    console.error(e)
  }
}

const addClozeItem = async (clozeTestId) => {
  try {
    await quizSetApi.addCloze(quizSet.value.id, clozeTestId)
    await fetchQuizSet()
  } catch (e) {
    console.error(e)
  }
}

const removeClozeItem = async (itemId) => {
  try {
    await quizSetApi.removeCloze(quizSet.value.id, itemId)
    await fetchQuizSet()
  } catch (e) {
    console.error(e)
  }
}

const goBack = () => {
  router.push({ name: 'admin-quiz-sets' })
}

onMounted(() => {
  fetchQuizSet()
  fetchAllItems()
})
</script>
