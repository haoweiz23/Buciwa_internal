<template>
  <div class="p-6">
    <div class="flex items-center mb-6">
      <button @click="goBack" class="mr-4 text-gray-500 hover:text-gray-700">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <h1 class="text-2xl font-bold text-gray-800">{{ wordSet?.main_word || '加载中...' }}</h1>
    </div>
    
    <!-- Loading -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="inline-block w-8 h-8 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin"></div>
    </div>
    
    <!-- Content -->
    <div v-else-if="wordSet" class="grid grid-cols-2 gap-6">
      <div
        v-for="word in wordSet.words"
        :key="word.id"
        class="bg-white rounded-xl shadow overflow-hidden"
      >
        <div class="aspect-square bg-gray-100 relative">
          <img
            v-if="word.image_local_path"
            :src="word.image_local_path"
            :alt="word.word"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
            <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <span
            :class="[
              'absolute top-2 left-2 px-2 py-1 rounded text-xs font-bold',
              word.word_type === 'main' ? 'bg-blue-500 text-white' : '',
              word.word_type === 'similar' ? 'bg-amber-500 text-white' : '',
              word.word_type === 'synonym' ? 'bg-green-500 text-white' : '',
              word.word_type === 'antonym' ? 'bg-red-500 text-white' : ''
            ]"
          >
            {{ getTypeLabel(word.word_type) }}
          </span>
        </div>
        <div class="p-4">
          <h3 class="text-lg font-bold text-gray-800">{{ word.word }}</h3>
          <p class="text-gray-500 text-sm mt-1">{{ word.meaning }}</p>
          <button
            @click="regenerateImage(word)"
            :disabled="word.isRegenerating"
            class="mt-3 w-full px-3 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 disabled:bg-gray-50 text-sm"
          >
            {{ word.isRegenerating ? '重新生成中...' : '重新生成图片' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Actions -->
    <div v-if="wordSet" class="mt-6 flex gap-4">
      <button
        @click="regenerateAll"
        :disabled="isRegeneratingAll"
        class="px-4 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 disabled:bg-gray-300"
      >
        {{ isRegeneratingAll ? '重新生成中...' : '重新生成所有' }}
      </button>
      <button
        @click="deleteWordSet"
        class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
      >
        删除
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { wordSetApi, wordApi } from '../../api'

const router = useRouter()
const route = useRoute()

const wordSet = ref(null)
const isLoading = ref(false)
const isRegeneratingAll = ref(false)

const fetchWordSet = async () => {
  isLoading.value = true
  try {
    wordSet.value = await wordSetApi.get(route.params.id)
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const getTypeLabel = (type) => {
  const labels = {
    main: 'A 主词',
    similar: 'B 形近词',
    synonym: 'C 近义词',
    antonym: 'D 反义词'
  }
  return labels[type] || type
}

const regenerateImage = async (word) => {
  word.isRegenerating = true
  try {
    const result = await wordApi.regenerateImage(word.id)
    // Update the word with new image
    const index = wordSet.value.words.findIndex(w => w.id === word.id)
    if (index !== -1) {
      wordSet.value.words[index] = { ...wordSet.value.words[index], ...result }
    }
  } catch (e) {
    console.error(e)
  } finally {
    word.isRegenerating = false
  }
}

const regenerateAll = async () => {
  if (!confirm('确定要重新生成所有选项吗？')) return
  isRegeneratingAll.value = true
  try {
    wordSet.value = await wordSetApi.regenerate(wordSet.value.id)
  } catch (e) {
    console.error(e)
  } finally {
    isRegeneratingAll.value = false
  }
}

const deleteWordSet = async () => {
  if (!confirm('确定要删除这个题目吗？')) return
  try {
    await wordSetApi.delete(wordSet.value.id)
    router.push({ name: 'admin-words' })
  } catch (e) {
    console.error(e)
  }
}

const goBack = () => {
  router.push({ name: 'admin-words' })
}

onMounted(() => {
  fetchWordSet()
})
</script>
