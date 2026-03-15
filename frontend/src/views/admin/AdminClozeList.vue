<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-800">完形填空管理</h1>
      <router-link
        to="/admin/cloze/create"
        class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
      >
        + 新建题目
      </router-link>
    </div>
    
    <!-- Loading -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="inline-block w-8 h-8 border-4 border-gray-200 border-t-green-500 rounded-full animate-spin"></div>
      <p class="text-gray-500 mt-2">加载中...</p>
    </div>
    
    <!-- Empty -->
    <div v-else-if="clozeTests.length === 0" class="text-center py-12 bg-white rounded-xl">
      <div class="text-6xl mb-4">✏️</div>
      <p class="text-gray-500">还没有完形填空题</p>
    </div>
    
    <!-- List -->
    <div v-else class="space-y-4">
      <div
        v-for="test in clozeTests"
        :key="test.id"
        class="bg-white rounded-xl shadow overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
        @click="goToDetail(test.id)"
      >
        <div class="flex">
          <div class="w-32 h-32 flex-shrink-0 bg-gray-100">
            <img
              v-if="test.image_local_path"
              :src="test.image_local_path"
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
            <div class="flex items-start justify-between">
              <div>
                <h3 class="font-bold text-gray-800">{{ test.word1 }} / {{ test.word2 }}</h3>
                <p class="text-gray-500 text-sm mt-1 line-clamp-2">{{ test.sentence }}</p>
                <p class="text-gray-400 text-xs mt-2">{{ formatDate(test.created_at) }}</p>
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
import { clozeTestApi } from '../../api'

const router = useRouter()

const clozeTests = ref([])
const isLoading = ref(false)

const fetchClozeTests = async () => {
  isLoading.value = true
  try {
    clozeTests.value = await clozeTestApi.list()
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const goToDetail = (id) => {
  router.push({ name: 'admin-cloze-detail', params: { id } })
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchClozeTests()
})
</script>
