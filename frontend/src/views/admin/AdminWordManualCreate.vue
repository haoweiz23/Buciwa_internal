<template>
  <div class="p-6">
    <div class="flex items-center mb-6">
      <button @click="goBack" class="mr-4 text-gray-500 hover:text-gray-700">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <div>
        <h1 class="text-2xl font-bold text-gray-800">手动创建单选题</h1>
        <p v-if="quizSetId" class="text-sm text-gray-500 mt-1">创建后将自动添加到当前题集</p>
      </div>
    </div>
    
    <div class="bg-white rounded-xl shadow p-6 max-w-4xl">
      <!-- Main Word -->
      <div class="mb-6">
        <label class="block text-gray-700 text-sm font-medium mb-2">主单词 *</label>
        <input
          v-model="mainWord.word"
          type="text"
          class="w-full px-4 py-2 rounded-lg border-2 border-gray-200 focus:border-blue-400 focus:outline-none"
          placeholder="输入主单词，例如：apple"
        />
      </div>
      
      <!-- Words Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <!-- Similar Word -->
        <div class="p-4 bg-gray-50 rounded-lg">
          <h3 class="font-medium text-gray-700 mb-3">形近词</h3>
          <input
            v-model="similarWord.word"
            type="text"
            class="w-full px-4 py-2 rounded-lg border-2 border-gray-200 focus:border-blue-400 focus:outline-none mb-2"
            placeholder="形近词"
          />
          <input
            v-model="similarWord.meaning"
            type="text"
            class="w-full px-4 py-2 rounded-lg border-2 border-gray-200 focus:border-blue-400 focus:outline-none"
            placeholder="中文释义"
          />
        </div>
        
        <!-- Synonym Word -->
        <div class="p-4 bg-gray-50 rounded-lg">
          <h3 class="font-medium text-gray-700 mb-3">近义词</h3>
          <input
            v-model="synonymWord.word"
            type="text"
            class="w-full px-4 py-2 rounded-lg border-2 border-gray-200 focus:border-blue-400 focus:outline-none mb-2"
            placeholder="近义词"
          />
          <input
            v-model="synonymWord.meaning"
            type="text"
            class="w-full px-4 py-2 rounded-lg border-2 border-gray-200 focus:border-blue-400 focus:outline-none"
            placeholder="中文释义"
          />
        </div>
        
        <!-- Antonym Word -->
        <div class="p-4 bg-gray-50 rounded-lg">
          <h3 class="font-medium text-gray-700 mb-3">反义词</h3>
          <input
            v-model="antonymWord.word"
            type="text"
            class="w-full px-4 py-2 rounded-lg border-2 border-gray-200 focus:border-blue-400 focus:outline-none mb-2"
            placeholder="反义词"
          />
          <input
            v-model="antonymWord.meaning"
            type="text"
            class="w-full px-4 py-2 rounded-lg border-2 border-gray-200 focus:border-blue-400 focus:outline-none"
            placeholder="中文释义"
          />
        </div>
        
        <!-- Main Word Meaning -->
        <div class="p-4 bg-blue-50 rounded-lg">
          <h3 class="font-medium text-blue-700 mb-3">主单词释义</h3>
          <input
            v-model="mainWord.meaning"
            type="text"
            class="w-full px-4 py-2 rounded-lg border-2 border-blue-200 focus:border-blue-400 focus:outline-none"
            placeholder="主单词的中文释义"
          />
        </div>
      </div>
      
      <!-- Image Upload Section -->
      <div class="mb-6">
        <h3 class="font-medium text-gray-700 mb-3">图片上传（可选）</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div v-for="(wordInfo, index) in allWords" :key="index" class="text-center">
            <div
              class="w-full aspect-square rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center cursor-pointer hover:border-blue-400 transition-colors overflow-hidden bg-gray-50"
              @click="triggerImageUpload(index)"
            >
              <img
                v-if="wordInfo.imagePreview"
                :src="wordInfo.imagePreview"
                class="w-full h-full object-cover"
              />
              <div v-else class="text-gray-400 text-center p-2">
                <svg class="w-8 h-8 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span class="text-xs">{{ wordInfo.label }}</span>
              </div>
            </div>
            <p class="text-xs text-gray-500 mt-1">{{ wordInfo.label }}</p>
            <input
              :ref="el => fileInputs[index] = el"
              type="file"
              accept="image/*"
              class="hidden"
              @change="(e) => handleImageUpload(e, index)"
            />
          </div>
        </div>
      </div>
      
      <p v-if="error" class="mb-4 text-red-500 text-sm text-center">{{ error }}</p>
      
      <div class="flex gap-4">
        <button
          @click="goBack"
          class="flex-1 px-4 py-3 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
        >
          取消
        </button>
        <button
          @click="create"
          :disabled="!mainWord.word.trim() || isCreating"
          class="flex-1 px-4 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 transition-colors"
        >
          {{ isCreating ? '创建中...' : '创建' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { wordSetApi, quizSetApi } from '../../api'

const router = useRouter()
const route = useRoute()

// Get quizSetId from query params if available
const quizSetId = computed(() => route.query.quizSetId ? parseInt(route.query.quizSetId) : null)

const mainWord = reactive({ word: '', meaning: '', image: null, imagePreview: null })
const similarWord = reactive({ word: '', meaning: '', image: null, imagePreview: null })
const synonymWord = reactive({ word: '', meaning: '', image: null, imagePreview: null })
const antonymWord = reactive({ word: '', meaning: '', image: null, imagePreview: null })

const fileInputs = ref([])
const isCreating = ref(false)
const error = ref('')

const allWords = computed(() => [
  { ...mainWord, label: '主单词' },
  { ...similarWord, label: '形近词' },
  { ...synonymWord, label: '近义词' },
  { ...antonymWord, label: '反义词' }
])

const triggerImageUpload = (index) => {
  fileInputs.value[index]?.click()
}

const handleImageUpload = (event, index) => {
  const file = event.target.files[0]
  if (!file) return
  
  const words = [mainWord, similarWord, synonymWord, antonymWord]
  words[index].image = file
  
  // Create preview
  const reader = new FileReader()
  reader.onload = (e) => {
    words[index].imagePreview = e.target.result
  }
  reader.readAsDataURL(file)
}

const create = async () => {
  if (!mainWord.word.trim()) {
    error.value = '请输入主单词'
    return
  }
  
  isCreating.value = true
  error.value = ''
  
  try {
    // Create form data for file upload
    const formData = new FormData()
    formData.append('main_word', mainWord.word.trim())
    formData.append('main_word_meaning', mainWord.meaning.trim())
    formData.append('similar_word', similarWord.word.trim())
    formData.append('similar_word_meaning', similarWord.meaning.trim())
    formData.append('synonym_word', synonymWord.word.trim())
    formData.append('synonym_word_meaning', synonymWord.meaning.trim())
    formData.append('antonym_word', antonymWord.word.trim())
    formData.append('antonym_word_meaning', antonymWord.meaning.trim())
    
    if (mainWord.image) formData.append('main_word_image', mainWord.image)
    if (similarWord.image) formData.append('similar_word_image', similarWord.image)
    if (synonymWord.image) formData.append('synonym_word_image', synonymWord.image)
    if (antonymWord.image) formData.append('antonym_word_image', antonymWord.image)
    
    const createdWordSet = await wordSetApi.createManual(formData)
    
    // If quizSetId is provided, add the word set to the quiz set
    if (quizSetId.value && createdWordSet.id) {
      try {
        await quizSetApi.addWord(quizSetId.value, createdWordSet.id)
      } catch (e) {
        console.error('Failed to add word set to quiz set:', e)
        // Still navigate back even if adding fails
      }
    }
    
    // Navigate back to quiz set or word list
    if (quizSetId.value) {
      router.push({ name: 'admin-quiz-set-detail', params: { id: quizSetId.value } })
    } else {
      router.push({ name: 'admin-words' })
    }
  } catch (e) {
    console.error(e)
    error.value = '创建失败，请重试'
  } finally {
    isCreating.value = false
  }
}

const goBack = () => {
  if (quizSetId.value) {
    router.push({ name: 'admin-quiz-set-detail', params: { id: quizSetId.value } })
  } else {
    router.push({ name: 'admin-words' })
  }
}
</script>
