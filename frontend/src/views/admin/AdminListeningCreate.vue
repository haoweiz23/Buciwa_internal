<template>
  <div class="p-6">
    <div class="flex items-center mb-6">
      <button @click="goBack" class="mr-4 text-gray-500 hover:text-gray-700">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <h1 class="text-2xl font-bold text-gray-800">创建听力练习</h1>
    </div>
    
    <div class="bg-white rounded-xl shadow p-6 max-w-2xl">
      <div class="mb-6">
        <label class="block text-gray-700 text-sm font-medium mb-2">场景描述</label>
        <textarea
          v-model="sceneDescription"
          rows="4"
          class="w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-purple-400 focus:outline-none resize-none"
          placeholder="描述一个场景，例如：一个人在海边散步..."
          :disabled="isGenerating"
        ></textarea>
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
          @click="generate"
          :disabled="!sceneDescription.trim() || isGenerating"
          class="flex-1 px-4 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:bg-gray-300 transition-colors"
        >
          {{ isGenerating ? '生成中...' : '生成练习' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { listeningExerciseApi } from '../../api'

const router = useRouter()

const sceneDescription = ref('')
const isGenerating = ref(false)
const error = ref('')

const generate = async () => {
  if (!sceneDescription.value.trim()) return
  
  isGenerating.value = true
  error.value = ''
  
  try {
    const result = await listeningExerciseApi.generate(sceneDescription.value.trim())
    router.push({ name: 'admin-listening' })
  } catch (e) {
    error.value = '生成失败，请重试'
    console.error(e)
  } finally {
    isGenerating.value = false
  }
}

const goBack = () => {
  router.push({ name: 'admin-listening' })
}
</script>
