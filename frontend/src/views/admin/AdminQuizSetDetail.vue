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
    <div v-else-if="quizSet" class="space-y-6">
      <!-- Unified Question List with Drag and Drop -->
      <div class="bg-white rounded-xl shadow p-4">
        <div class="flex items-center justify-between mb-4">
          <h2 class="font-bold text-gray-800">题目列表 ({{ allQuestions.length }})</h2>
          <div class="flex gap-2">
            <button
              @click="showAddQuestionMenu = true"
              class="px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors text-sm"
            >
              + 新建题目
            </button>
          </div>
        </div>
        
        <div v-if="allQuestions.length === 0" class="text-center py-8 text-gray-400">
          暂无题目，点击"新建题目"添加
        </div>
        
        <div v-else class="space-y-2">
          <div
            v-for="(question, index) in allQuestions"
            :key="`${question.type}-${question.id}`"
            draggable="true"
            @dragstart="handleDragStart($event, index)"
            @dragover.prevent="handleDragOver($event, index)"
            @drop="handleDrop($event, index)"
            @dragend="handleDragEnd"
            :class="[
              'flex items-center justify-between p-3 rounded-lg transition-colors',
              draggedIndex === index ? 'bg-indigo-100 border-2 border-indigo-300' : 'bg-gray-50 hover:bg-gray-100'
            ]"
          >
            <div class="flex items-center flex-1">
              <!-- Drag Handle -->
              <div class="cursor-move mr-3 text-gray-400 hover:text-gray-600">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
                </svg>
              </div>
              <!-- Order Number -->
              <span class="text-gray-400 text-sm mr-3 w-6">{{ index + 1 }}.</span>
              <!-- Type Badge -->
              <span
                :class="[
                  'px-2 py-1 rounded text-xs font-medium mr-3',
                  question.type === 'word' ? 'bg-blue-100 text-blue-600' :
                  question.type === 'cloze' ? 'bg-green-100 text-green-600' :
                  'bg-purple-100 text-purple-600'
                ]"
              >
                {{ question.type === 'word' ? '单选' : question.type === 'cloze' ? '完形' : '听力' }}
              </span>
              <!-- Question Content -->
              <span class="font-medium text-gray-800">{{ question.title }}</span>
            </div>
            <div class="flex items-center gap-2">
              <!-- Move Up/Down -->
              <button
                @click="moveQuestion(index, -1)"
                :disabled="index === 0"
                class="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                </svg>
              </button>
              <button
                @click="moveQuestion(index, 1)"
                :disabled="index === allQuestions.length - 1"
                class="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              <!-- Remove -->
              <button
                @click="removeQuestion(question)"
                class="text-red-500 hover:text-red-600 text-sm ml-2"
              >
                移除
              </button>
            </div>
          </div>
        </div>
        
        <!-- Save Order Button -->
        <div v-if="hasOrderChanged" class="mt-4 flex justify-end">
          <button
            @click="saveOrder"
            class="px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors text-sm"
          >
            保存排序
          </button>
        </div>
      </div>
      
      <!-- Summary Cards -->
      <div class="grid grid-cols-3 gap-4">
        <div class="bg-blue-50 rounded-xl p-4 text-center">
          <div class="text-2xl font-bold text-blue-600">{{ quizSet.word_set_items.length }}</div>
          <div class="text-sm text-blue-500">单选题</div>
        </div>
        <div class="bg-green-50 rounded-xl p-4 text-center">
          <div class="text-2xl font-bold text-green-600">{{ quizSet.cloze_items.length }}</div>
          <div class="text-sm text-green-500">完形填空</div>
        </div>
        <div class="bg-purple-50 rounded-xl p-4 text-center">
          <div class="text-2xl font-bold text-purple-600">{{ quizSet.listening_items.length }}</div>
          <div class="text-sm text-purple-500">听力题</div>
        </div>
      </div>
    </div>
    
    <!-- Add Question Menu Modal -->
    <div
      v-if="showAddQuestionMenu"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showAddQuestionMenu = false"
    >
      <div class="bg-white rounded-xl p-6 w-full max-w-md">
        <h2 class="text-xl font-bold text-gray-800 mb-4">选择题目类型</h2>
        <div class="space-y-3">
          <button
            @click="openAddModal('word')"
            class="w-full p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors text-left"
          >
            <div class="font-medium text-blue-800">单选题</div>
            <div class="text-sm text-blue-500">从现有单词集中选择</div>
          </button>
          <button
            @click="openAddModal('cloze')"
            class="w-full p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors text-left"
          >
            <div class="font-medium text-green-800">完形填空</div>
            <div class="text-sm text-green-500">从现有完形填空中选择</div>
          </button>
          <button
            @click="openAddModal('listening')"
            class="w-full p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors text-left"
          >
            <div class="font-medium text-purple-800">听力题</div>
            <div class="text-sm text-purple-500">从现有听力练习中选择</div>
          </button>
          <hr class="my-3">
          <button
            @click="goToCreateQuestion('word')"
            class="w-full p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-left"
          >
            <div class="font-medium text-gray-800">+ 手动创建单选题</div>
            <div class="text-sm text-gray-500">自行上传单词和图片</div>
          </button>
          <button
            @click="goToCreateQuestion('cloze')"
            class="w-full p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-left"
          >
            <div class="font-medium text-gray-800">+ 手动创建完形填空</div>
            <div class="text-sm text-gray-500">自行上传句子和图片</div>
          </button>
        </div>
        <button
          @click="showAddQuestionMenu = false"
          class="mt-4 w-full px-4 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200"
        >
          取消
        </button>
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
    
    <!-- Add Listening Modal -->
    <div
      v-if="showAddListeningModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showAddListeningModal = false"
    >
      <div class="bg-white rounded-xl p-6 w-full max-w-lg max-h-[80vh] overflow-auto">
        <h2 class="text-xl font-bold text-gray-800 mb-4">添加听力题</h2>
        <div class="space-y-2">
          <div
            v-for="le in availableListeningExercises"
            :key="le.id"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div class="flex items-center">
              <div class="w-12 h-12 flex-shrink-0 bg-gray-200 rounded mr-3 overflow-hidden">
                <img
                  v-if="le.image_local_path"
                  :src="le.image_local_path"
                  class="w-full h-full object-cover"
                />
              </div>
              <div>
                <p class="font-medium text-gray-800 line-clamp-1">{{ le.scene_description }}</p>
                <p class="text-gray-400 text-xs mt-1">{{ formatDate(le.created_at) }}</p>
              </div>
            </div>
            <button
              @click="addListeningItem(le.id)"
              class="px-3 py-1 bg-purple-500 text-white rounded hover:bg-purple-600 text-sm"
            >
              添加
            </button>
          </div>
        </div>
        <button
          @click="showAddListeningModal = false"
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
import { quizSetApi, wordSetApi, clozeTestApi, listeningExerciseApi } from '../../api'

const router = useRouter()
const route = useRoute()

const quizSet = ref(null)
const isLoading = ref(false)
const showAddQuestionMenu = ref(false)
const showAddWordModal = ref(false)
const showAddClozeModal = ref(false)
const showAddListeningModal = ref(false)
const allWordSets = ref([])
const allClozeTests = ref([])
const allListeningExercises = ref([])
const localQuestions = ref([])
const hasOrderChanged = ref(false)
const draggedIndex = ref(null)

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

const availableListeningExercises = computed(() => {
  if (!quizSet.value) return []
  const addedIds = new Set(quizSet.value.listening_items.map(i => i.listening_exercise_id))
  return allListeningExercises.value.filter(le => !addedIds.has(le.id))
})

const allQuestions = computed(() => {
  if (!quizSet.value) return []
  
  const questions = []
  
  // Add word questions
  for (const item of quizSet.value.word_set_items) {
    questions.push({
      id: item.id,
      itemId: item.id,
      type: 'word',
      order: item.order,
      title: item.word_set.main_word,
      refId: item.word_set_id
    })
  }
  
  // Add cloze questions
  for (const item of quizSet.value.cloze_items) {
    questions.push({
      id: item.id,
      itemId: item.id,
      type: 'cloze',
      order: item.order,
      title: `${item.cloze_test.word1} / ${item.cloze_test.word2}`,
      refId: item.cloze_test_id
    })
  }
  
  // Add listening questions
  for (const item of quizSet.value.listening_items) {
    questions.push({
      id: item.id,
      itemId: item.id,
      type: 'listening',
      order: item.order,
      title: item.listening_exercise.scene_description,
      refId: item.listening_exercise_id
    })
  }
  
  // Sort by order
  return questions.sort((a, b) => a.order - b.order)
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
    const [words, clozes, listenings] = await Promise.all([
      wordSetApi.list(),
      clozeTestApi.list(),
      listeningExerciseApi.list()
    ])
    allWordSets.value = words
    allClozeTests.value = clozes
    allListeningExercises.value = listenings
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

const openAddModal = (type) => {
  showAddQuestionMenu.value = false
  if (type === 'word') {
    showAddWordModal.value = true
  } else if (type === 'cloze') {
    showAddClozeModal.value = true
  } else if (type === 'listening') {
    showAddListeningModal.value = true
  }
}

const goToCreateQuestion = (type) => {
  showAddQuestionMenu.value = false
  if (type === 'word') {
    router.push({ name: 'admin-word-manual-create', query: { quizSetId: quizSet.value.id } })
  } else if (type === 'cloze') {
    router.push({ name: 'admin-cloze-manual-create', query: { quizSetId: quizSet.value.id } })
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

const addListeningItem = async (listeningExerciseId) => {
  try {
    await quizSetApi.addListening(quizSet.value.id, listeningExerciseId)
    await fetchQuizSet()
  } catch (e) {
    console.error(e)
  }
}

const removeListeningItem = async (itemId) => {
  try {
    await quizSetApi.removeListening(quizSet.value.id, itemId)
    await fetchQuizSet()
  } catch (e) {
    console.error(e)
  }
}

const moveQuestion = (index, direction) => {
  const newIndex = index + direction
  if (newIndex < 0 || newIndex >= allQuestions.value.length) return
  
  // Swap orders
  const questions = [...allQuestions.value]
  const temp = questions[index].order
  questions[index].order = questions[newIndex].order
  questions[newIndex].order = temp
  
  // Update in quizSet
  const q1 = questions[index]
  const q2 = questions[newIndex]
  
  if (q1.type === 'word') {
    const item = quizSet.value.word_set_items.find(i => i.id === q1.itemId)
    if (item) item.order = q1.order
  } else if (q1.type === 'cloze') {
    const item = quizSet.value.cloze_items.find(i => i.id === q1.itemId)
    if (item) item.order = q1.order
  } else if (q1.type === 'listening') {
    const item = quizSet.value.listening_items.find(i => i.id === q1.itemId)
    if (item) item.order = q1.order
  }
  
  if (q2.type === 'word') {
    const item = quizSet.value.word_set_items.find(i => i.id === q2.itemId)
    if (item) item.order = q2.order
  } else if (q2.type === 'cloze') {
    const item = quizSet.value.cloze_items.find(i => i.id === q2.itemId)
    if (item) item.order = q2.order
  } else if (q2.type === 'listening') {
    const item = quizSet.value.listening_items.find(i => i.id === q2.itemId)
    if (item) item.order = q2.order
  }
  
  hasOrderChanged.value = true
}

// Drag and drop handlers
const handleDragStart = (event, index) => {
  draggedIndex.value = index
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', index.toString())
}

const handleDragOver = (event, index) => {
  event.preventDefault()
  event.dataTransfer.dropEffect = 'move'
}

const handleDrop = (event, targetIndex) => {
  event.preventDefault()
  const sourceIndex = draggedIndex.value
  
  if (sourceIndex === null || sourceIndex === targetIndex) {
    return
  }
  
  // Reorder questions by moving the source item to the target position
  const questions = [...allQuestions.value]
  const [movedItem] = questions.splice(sourceIndex, 1)
  questions.splice(targetIndex, 0, movedItem)
  
  // Update order values based on new positions
  questions.forEach((q, idx) => {
    q.order = idx
    
    // Update in quizSet
    if (q.type === 'word') {
      const item = quizSet.value.word_set_items.find(i => i.id === q.itemId)
      if (item) item.order = q.order
    } else if (q.type === 'cloze') {
      const item = quizSet.value.cloze_items.find(i => i.id === q.itemId)
      if (item) item.order = q.order
    } else if (q.type === 'listening') {
      const item = quizSet.value.listening_items.find(i => i.id === q.itemId)
      if (item) item.order = q.order
    }
  })
  
  hasOrderChanged.value = true
}

const handleDragEnd = () => {
  draggedIndex.value = null
}

const removeQuestion = async (question) => {
  if (question.type === 'word') {
    await removeWordItem(question.itemId)
  } else if (question.type === 'cloze') {
    await removeClozeItem(question.itemId)
  } else if (question.type === 'listening') {
    await removeListeningItem(question.itemId)
  }
}

const saveOrder = async () => {
  try {
    const wordItems = quizSet.value.word_set_items.map(i => ({ id: i.id, order: i.order }))
    const clozeItems = quizSet.value.cloze_items.map(i => ({ id: i.id, order: i.order }))
    const listeningItems = quizSet.value.listening_items.map(i => ({ id: i.id, order: i.order }))
    
    await quizSetApi.reorder(quizSet.value.id, wordItems, clozeItems, listeningItems)
    hasOrderChanged.value = false
    await fetchQuizSet()
  } catch (e) {
    console.error(e)
    alert('保存排序失败')
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const goBack = () => {
  router.push({ name: 'admin-quiz-sets' })
}

onMounted(() => {
  fetchQuizSet()
  fetchAllItems()
})
</script>
