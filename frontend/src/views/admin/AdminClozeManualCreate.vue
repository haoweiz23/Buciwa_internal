<template>
  <div class="p-6">
    <div class="flex items-center mb-6">
      <button @click="goBack" class="mr-4 text-gray-500 hover:text-gray-700">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <div>
        <h1 class="text-2xl font-bold text-gray-800">手动创建完形填空</h1>
        <p v-if="quizSetId" class="text-sm text-gray-500 mt-1">创建后将自动添加到当前题集</p>
      </div>
    </div>
    
    <div class="bg-white rounded-xl shadow p-6 max-w-4xl">
      <!-- Main Words -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <label class="block text-gray-700 text-sm font-medium mb-2">单词1 *</label>
          <input
            v-model="word1"
            type="text"
            class="w-full px-4 py-2 rounded-lg border-2 border-gray-200 focus:border-green-400 focus:outline-none mb-2"
            placeholder="例如：happy"
          />
          <input
            v-model="word1Meaning"
            type="text"
            class="w-full px-4 py-2 rounded-lg border-2 border-gray-200 focus:border-green-400 focus:outline-none"
            placeholder="中文释义"
          />
        </div>
        
        <div>
          <label class="block text-gray-700 text-sm font-medium mb-2">单词2 *</label>
          <input
            v-model="word2"
            type="text"
            class="w-full px-4 py-2 rounded-lg border-2 border-gray-200 focus:border-green-400 focus:outline-none mb-2"
            placeholder="例如：sad"
          />
          <input
            v-model="word2Meaning"
            type="text"
            class="w-full px-4 py-2 rounded-lg border-2 border-gray-200 focus:border-green-400 focus:outline-none"
            placeholder="中文释义"
          />
        </div>
      </div>
      
      <!-- Distractors -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div class="p-4 bg-gray-50 rounded-lg">
          <h3 class="font-medium text-gray-700 mb-3">干扰选项1（可选）</h3>
          <input
            v-model="distractor1"
            type="text"
            class="w-full px-4 py-2 rounded-lg border-2 border-gray-200 focus:border-green-400 focus:outline-none mb-2"
            placeholder="干扰词"
          />
          <input
            v-model="distractor1Meaning"
            type="text"
            class="w-full px-4 py-2 rounded-lg border-2 border-gray-200 focus:border-green-400 focus:outline-none"
            placeholder="中文释义"
          />
        </div>
        
        <div class="p-4 bg-gray-50 rounded-lg">
          <h3 class="font-medium text-gray-700 mb-3">干扰选项2（可选）</h3>
          <input
            v-model="distractor2"
            type="text"
            class="w-full px-4 py-2 rounded-lg border-2 border-gray-200 focus:border-green-400 focus:outline-none mb-2"
            placeholder="干扰词"
          />
          <input
            v-model="distractor2Meaning"
            type="text"
            class="w-full px-4 py-2 rounded-lg border-2 border-gray-200 focus:border-green-400 focus:outline-none"
            placeholder="中文释义"
          />
        </div>
      </div>
      
      <!-- Sentences -->
      <div class="mb-6">
        <label class="block text-gray-700 text-sm font-medium mb-2">中文句子（用 ____ 表示空格）*</label>
        <textarea
          v-model="sentence"
          rows="3"
          class="w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-400 focus:outline-none resize-none"
          placeholder="例如：他感到非常____，因为今天是他____的一天。"
        ></textarea>
        <p class="text-xs text-gray-400 mt-1">使用 ____ 表示空格位置</p>
      </div>
      
      <div class="mb-6">
        <label class="block text-gray-700 text-sm font-medium mb-2">中文句子（带答案）*</label>
        <textarea
          v-model="sentenceWithAnswers"
          rows="3"
          class="w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-400 focus:outline-none resize-none"
          placeholder="例如：他感到非常开心，因为今天是他快乐的一天。"
        ></textarea>
      </div>
      
      <div class="mb-6">
        <label class="block text-gray-700 text-sm font-medium mb-2">英文句子（可选，用 ____ 表示空格）</label>
        <textarea
          v-model="sentenceEn"
          rows="3"
          class="w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-400 focus:outline-none resize-none"
          placeholder="例如：He feels very ____ because today is his ____ day."
        ></textarea>
      </div>
      
      <div class="mb-6">
        <label class="block text-gray-700 text-sm font-medium mb-2">英文句子（带答案，可选）</label>
        <textarea
          v-model="sentenceWithAnswersEn"
          rows="3"
          class="w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-green-400 focus:outline-none resize-none"
          placeholder="例如：He feels very happy because today is his joyful day."
        ></textarea>
      </div>
      
      <!-- Image Upload -->
      <div class="mb-6">
        <label class="block text-gray-700 text-sm font-medium mb-2">图片（可选）</label>
        <div
          class="w-full h-48 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center cursor-pointer hover:border-green-400 transition-colors overflow-hidden bg-gray-50"
          @click="triggerImageUpload"
        >
          <img
            v-if="imagePreview"
            :src="imagePreview"
            class="w-full h-full object-cover"
          />
          <div v-else class="text-gray-400 text-center">
            <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span>点击上传图片</span>
          </div>
        </div>
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          class="hidden"
          @change="handleImageUpload"
        />
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
          :disabled="!isFormValid || isCreating"
          class="flex-1 px-4 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-300 transition-colors"
        >
          {{ isCreating ? '创建中...' : '创建' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { clozeTestApi, quizSetApi } from '../../api'

const router = useRouter()
const route = useRoute()

// Get quizSetId from query params if available
const quizSetId = computed(() => route.query.quizSetId ? parseInt(route.query.quizSetId) : null)

const word1 = ref('')
const word2 = ref('')
const word1Meaning = ref('')
const word2Meaning = ref('')
const distractor1 = ref('')
const distractor2 = ref('')
const distractor1Meaning = ref('')
const distractor2Meaning = ref('')
const sentence = ref('')
const sentenceWithAnswers = ref('')
const sentenceEn = ref('')
const sentenceWithAnswersEn = ref('')
const imageFile = ref(null)
const imagePreview = ref(null)
const fileInput = ref(null)
const isCreating = ref(false)
const error = ref('')

const isFormValid = computed(() => {
  return word1.value.trim() && 
         word2.value.trim() && 
         sentence.value.trim() && 
         sentenceWithAnswers.value.trim()
})

const triggerImageUpload = () => {
  fileInput.value?.click()
}

const handleImageUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  imageFile.value = file
  
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

const create = async () => {
  if (!isFormValid.value) {
    error.value = '请填写必填项'
    return
  }
  
  isCreating.value = true
  error.value = ''
  
  try {
    const formData = new FormData()
    formData.append('word1', word1.value.trim())
    formData.append('word2', word2.value.trim())
    formData.append('word1_meaning', word1Meaning.value.trim())
    formData.append('word2_meaning', word2Meaning.value.trim())
    formData.append('distractor1', distractor1.value.trim())
    formData.append('distractor2', distractor2.value.trim())
    formData.append('distractor1_meaning', distractor1Meaning.value.trim())
    formData.append('distractor2_meaning', distractor2Meaning.value.trim())
    formData.append('sentence', sentence.value.trim())
    formData.append('sentence_with_answers', sentenceWithAnswers.value.trim())
    formData.append('sentence_en', sentenceEn.value.trim())
    formData.append('sentence_with_answers_en', sentenceWithAnswersEn.value.trim())
    
    if (imageFile.value) {
      formData.append('image', imageFile.value)
    }
    
    const createdCloze = await clozeTestApi.createManual(formData)
    
    // If quizSetId is provided, add the cloze to the quiz set
    if (quizSetId.value && createdCloze.id) {
      try {
        await quizSetApi.addCloze(quizSetId.value, createdCloze.id)
      } catch (e) {
        console.error('Failed to add cloze to quiz set:', e)
        // Still navigate back even if adding fails
      }
    }
    
    // Navigate back to quiz set or cloze list
    if (quizSetId.value) {
      router.push({ name: 'admin-quiz-set-detail', params: { id: quizSetId.value } })
    } else {
      router.push({ name: 'admin-cloze' })
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
    router.push({ name: 'admin-cloze' })
  }
}
</script>
