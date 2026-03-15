<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center">
        <button @click="goBack" class="mr-4 text-gray-500 hover:text-gray-700">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h1 class="text-2xl font-bold text-gray-800">完形填空详情</h1>
      </div>
      <!-- Language Toggle -->
      <div class="flex items-center gap-2">
        <span class="text-gray-600 text-sm">语言:</span>
        <button
          @click="language = 'zh'"
          :class="[
            'px-3 py-1 rounded-lg text-sm font-medium transition-colors',
            language === 'zh' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          ]"
        >
          中文
        </button>
        <button
          @click="language = 'en'"
          :class="[
            'px-3 py-1 rounded-lg text-sm font-medium transition-colors',
            language === 'en' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          ]"
        >
          English
        </button>
      </div>
    </div>
    
    <!-- Loading -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="inline-block w-8 h-8 border-4 border-gray-200 border-t-green-500 rounded-full animate-spin"></div>
    </div>
    
    <!-- Content -->
    <div v-else-if="clozeTest" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Image -->
      <div class="bg-white rounded-xl shadow overflow-hidden">
        <div class="aspect-video bg-gray-100">
          <img
            v-if="clozeTest.image_local_path"
            :src="clozeTest.image_local_path"
            alt="Question Image"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
            <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
      </div>
      
      <!-- Question Info -->
      <div class="bg-white rounded-xl shadow p-6">
        <h2 class="text-lg font-bold text-gray-800 mb-4">题目信息</h2>
        
        <!-- Sentence -->
        <div class="mb-6">
          <h3 class="text-sm font-medium text-gray-500 mb-2">
            {{ language === 'zh' ? '句子（带空格）' : 'Sentence (with blanks)' }}
          </h3>
          <p class="text-gray-800 text-lg p-4 bg-gray-50 rounded-lg">
            {{ currentSentence }}
          </p>
        </div>
        
        <!-- Answer -->
        <div class="mb-6">
          <h3 class="text-sm font-medium text-gray-500 mb-2">
            {{ language === 'zh' ? '答案' : 'Answer' }}
          </h3>
          <p class="text-gray-800 p-4 bg-green-50 rounded-lg">
            {{ currentAnswer }}
          </p>
        </div>
        
        <!-- Options -->
        <div class="mb-6">
          <h3 class="text-sm font-medium text-gray-500 mb-2">选项</h3>
          <div class="grid grid-cols-2 gap-2">
            <div
              v-for="option in options"
              :key="option.word"
              class="p-3 rounded-lg border-2"
              :class="[
                option.isCorrect ? 'border-green-500 bg-green-50' : 'border-gray-200'
              ]"
            >
              <span class="font-bold text-gray-800">{{ option.word }}</span>
              <span class="text-gray-500 text-sm ml-2">{{ option.meaning }}</span>
              <span v-if="option.isCorrect" class="text-green-500 text-xs ml-1">✓ 正确</span>
              <span v-else-if="option.isDistractor" class="text-gray-400 text-xs ml-1">干扰项</span>
            </div>
          </div>
        </div>
        
        <!-- Actions -->
        <div class="flex gap-3">
          <button
            @click="deleteTest"
            class="flex-1 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
          >
            删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { clozeTestApi } from '../../api'

const router = useRouter()
const route = useRoute()

const clozeTest = ref(null)
const isLoading = ref(false)
const language = ref('zh') // 'zh' or 'en'

const currentSentence = computed(() => {
  if (!clozeTest.value) return ''
  return language.value === 'zh' ? clozeTest.value.sentence : (clozeTest.value.sentence_en || clozeTest.value.sentence)
})

const currentAnswer = computed(() => {
  if (!clozeTest.value) return ''
  return language.value === 'zh' ? clozeTest.value.sentence_with_answers : (clozeTest.value.sentence_with_answers_en || clozeTest.value.sentence_with_answers)
})

const options = computed(() => {
  if (!clozeTest.value) return []
  return [
    { word: clozeTest.value.word1, meaning: clozeTest.value.word1_meaning, isCorrect: true, isDistractor: false },
    { word: clozeTest.value.word2, meaning: clozeTest.value.word2_meaning, isCorrect: true, isDistractor: false },
    { word: clozeTest.value.distractor1, meaning: clozeTest.value.distractor1_meaning, isCorrect: false, isDistractor: true },
    { word: clozeTest.value.distractor2, meaning: clozeTest.value.distractor2_meaning, isCorrect: false, isDistractor: true }
  ].filter(opt => opt.word) // Filter out empty options
})

const fetchClozeTest = async () => {
  isLoading.value = true
  try {
    clozeTest.value = await clozeTestApi.get(route.params.id)
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const deleteTest = async () => {
  if (!confirm('确定要删除这个题目吗？')) return
  try {
    await clozeTestApi.delete(clozeTest.value.id)
    router.push({ name: 'admin-cloze' })
  } catch (e) {
    console.error(e)
  }
}

const goBack = () => {
  router.push({ name: 'admin-cloze' })
}

onMounted(() => {
  fetchClozeTest()
})
</script>
