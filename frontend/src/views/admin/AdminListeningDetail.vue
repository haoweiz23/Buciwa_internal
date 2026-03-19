<template>
  <div class="p-6">
    <div class="flex items-center mb-6">
      <button @click="goBack" class="mr-4 text-gray-500 hover:text-gray-700">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <h1 class="text-2xl font-bold text-gray-800">听力详情</h1>
    </div>
    
    <!-- Loading -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="inline-block w-8 h-8 border-4 border-gray-200 border-t-purple-500 rounded-full animate-spin"></div>
    </div>
    
    <!-- Content -->
    <div v-else-if="exercise" class="space-y-6">
      <!-- Image and Info -->
      <div class="bg-white rounded-xl shadow overflow-hidden">
        <div class="md:flex">
          <div class="md:w-1/2">
            <img
              v-if="exercise.image_local_path"
              :src="exercise.image_local_path"
              alt="Scene"
              class="w-full h-64 md:h-full object-cover"
            />
            <div v-else class="w-full h-64 bg-gray-100 flex items-center justify-center">
              <span class="text-gray-400">暂无图片</span>
            </div>
          </div>
          <div class="md:w-1/2 p-6">
            <h2 class="text-lg font-bold text-gray-800 mb-4">场景描述</h2>
            <p class="text-gray-600 mb-6">{{ exercise.scene_description }}</p>
            
            <h2 class="text-lg font-bold text-gray-800 mb-4">生成文本</h2>
            <p class="text-gray-600 mb-6">{{ exercise.generated_text || '暂无' }}</p>
            
            <div class="flex items-center gap-4">
              <span class="text-sm text-gray-400">
                创建于 {{ formatDate(exercise.created_at) }}
              </span>
              <button
                @click="deleteExercise"
                class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Audio Player -->
      <div class="bg-white rounded-xl shadow p-6">
        <h2 class="text-lg font-bold text-gray-800 mb-4">🎧 音频</h2>
        <div v-if="exercise.audio_local_path" class="flex items-center gap-4">
          <audio :src="exercise.audio_local_path" controls class="w-full"></audio>
        </div>
        <div v-else class="text-gray-400 text-center py-4">
          暂无音频
        </div>
      </div>
    </div>
    
    <!-- Not Found -->
    <div v-else class="text-center py-12 bg-white rounded-xl">
      <div class="text-6xl mb-4">😕</div>
      <p class="text-gray-500">听力练习不存在</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { listeningExerciseApi } from '../../api'

const router = useRouter()
const route = useRoute()

const exercise = ref(null)
const isLoading = ref(false)

const fetchExercise = async () => {
  isLoading.value = true
  try {
    exercise.value = await listeningExerciseApi.get(route.params.id)
  } catch (e) {
    console.error(e)
    exercise.value = null
  } finally {
    isLoading.value = false
  }
}

const deleteExercise = async () => {
  if (!confirm('确定要删除这个听力练习吗？')) return
  
  try {
    await listeningExerciseApi.delete(exercise.value.id)
    router.push({ name: 'admin-listening' })
  } catch (e) {
    console.error(e)
    alert('删除失败')
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const goBack = () => {
  router.push({ name: 'admin-listening' })
}

onMounted(() => {
  fetchExercise()
})
</script>
