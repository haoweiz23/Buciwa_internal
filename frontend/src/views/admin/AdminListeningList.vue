<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-800">听力管理</h1>
      <router-link
        to="/admin/listening/create"
        class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors"
      >
        + 新建题目
      </router-link>
    </div>
    
    <!-- Loading -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="inline-block w-8 h-8 border-4 border-gray-200 border-t-purple-500 rounded-full animate-spin"></div>
      <p class="text-gray-500 mt-2">加载中...</p>
    </div>
    
    <!-- Empty -->
    <div v-else-if="exercises.length === 0" class="text-center py-12 bg-white rounded-xl">
      <div class="text-6xl mb-4">🎧</div>
      <p class="text-gray-500">还没有听力练习</p>
    </div>
    
    <!-- List -->
    <div v-else class="space-y-4">
      <div
        v-for="exercise in exercises"
        :key="exercise.id"
        @click="goToDetail(exercise.id)"
        class="bg-white rounded-xl shadow overflow-hidden hover:shadow-md transition-shadow cursor-pointer relative group"
      >
        <div class="flex">
          <div class="w-32 h-32 flex-shrink-0 bg-gray-100">
            <img
              v-if="exercise.image_local_path"
              :src="exercise.image_local_path"
              alt="Thumbnail"
              class="w-full h-full object-cover"
            />
            <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
          <div class="flex-1 p-4">
            <h3 class="font-bold text-gray-800 text-sm line-clamp-2">{{ exercise.scene_description }}</h3>
            <p class="text-gray-400 text-xs mt-2">{{ formatDate(exercise.created_at) }}</p>
          </div>
        </div>
        <!-- Delete Button -->
        <button
          @click.stop="deleteExercise(exercise.id)"
          class="absolute top-2 right-2 p-1.5 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 hover:bg-red-600 transition-all shadow-lg"
          title="删除"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listeningExerciseApi } from '../../api'

const router = useRouter()

const exercises = ref([])
const isLoading = ref(false)

const fetchExercises = async () => {
  isLoading.value = true
  try {
    exercises.value = await listeningExerciseApi.list()
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const goToDetail = (id) => {
  router.push({ name: 'admin-listening-detail', params: { id } })
}

const deleteExercise = async (id) => {
  if (!confirm('确定要删除这道听力题吗？此操作不可撤销。')) return
  try {
    await listeningExerciseApi.delete(id)
    await fetchExercises()
  } catch (e) {
    console.error(e)
    alert('删除失败')
  }
}

onMounted(() => {
  fetchExercises()
})
</script>
