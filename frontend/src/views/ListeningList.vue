<template>
  <div class="min-h-screen p-3 sm:p-4 md:p-8">
    <!-- Header -->
    <header class="max-w-4xl mx-auto mb-6 sm:mb-8">
      <div class="flex items-center justify-between">
        <button
          @click="goHome"
          class="px-4 py-2 text-mint-600 hover:text-mint-700 flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          返回首页
        </button>
        <h1 class="text-xl sm:text-2xl font-bold text-mint-700">听力练习列表</h1>
        <button
          @click="goToCreate"
          class="px-4 py-2 bg-mint-500 text-white rounded-lg
                 hover:bg-mint-600 transition-colors text-sm font-medium"
        >
          + 新建
        </button>
      </div>
    </header>

    <!-- Content -->
    <div class="max-w-4xl mx-auto">
      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="inline-block w-8 h-8 border-4 border-mint-200 border-t-mint-500 rounded-full spinner"></div>
        <p class="text-mint-600 mt-2">加载中...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="exercises.length === 0" class="text-center py-12">
        <div class="text-6xl mb-4">🎧</div>
        <p class="text-mint-600 text-lg mb-4">还没有听力练习</p>
        <button
          @click="goToCreate"
          class="px-6 py-3 bg-mint-500 text-white rounded-xl
                 hover:bg-mint-600 transition-colors font-medium"
        >
          创建第一个练习
        </button>
      </div>

      <!-- List -->
      <div v-else class="space-y-4">
        <div
          v-for="exercise in exercises"
          :key="exercise.id"
          class="bg-white rounded-2xl shadow-soft overflow-hidden
                 hover:shadow-md transition-shadow cursor-pointer"
          @click="goToExercise(exercise.id)"
        >
          <div class="flex">
            <!-- Thumbnail -->
            <div class="w-32 h-32 flex-shrink-0 bg-gray-100">
              <img
                v-if="exercise.image_local_path"
                :src="exercise.image_local_path"
                alt="Thumbnail"
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>

            <!-- Content -->
            <div class="flex-1 p-4">
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <p class="text-gray-800 font-medium mb-2 line-clamp-2">
                    {{ exercise.scene_description }}
                  </p>
                  <p v-if="exercise.generated_text" class="text-gray-500 text-sm line-clamp-2 mb-2">
                    {{ exercise.generated_text }}
                  </p>
                  <div class="flex items-center gap-3">
                    <span v-if="exercise.audio_local_path" class="flex items-center gap-1 text-mint-600 text-xs">
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
                      </svg>
                      有音频
                    </span>
                    <p class="text-gray-400 text-xs">
                      {{ formatDate(exercise.created_at) }}
                    </p>
                  </div>
                </div>
                <button
                  @click.stop="deleteExercise(exercise.id)"
                  class="p-2 text-gray-400 hover:text-red-500 transition-colors"
                  title="删除"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listeningExerciseApi } from '../api'

const router = useRouter()

// State
const exercises = ref([])
const isLoading = ref(false)
const error = ref('')

// Methods
const fetchExercises = async () => {
  isLoading.value = true
  error.value = ''
  try {
    exercises.value = await listeningExerciseApi.list()
  } catch (e) {
    error.value = '加载练习失败，请重试。'
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const deleteExercise = async (id) => {
  if (!confirm('确定要删除这个练习吗？')) return
  
  try {
    await listeningExerciseApi.delete(id)
    exercises.value = exercises.value.filter(e => e.id !== id)
  } catch (e) {
    error.value = '删除练习失败。'
    console.error(e)
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const goHome = () => {
  router.push({ name: 'list' })
}

const goToCreate = () => {
  router.push({ name: 'listening-test' })
}

const goToExercise = (id) => {
  router.push({ name: 'listening-test-detail', params: { id } })
}

// Lifecycle
onMounted(() => {
  fetchExercises()
})
</script>

<style scoped>
.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
