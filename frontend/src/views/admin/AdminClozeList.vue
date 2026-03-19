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
        class="bg-white rounded-xl shadow overflow-hidden hover:shadow-md transition-shadow cursor-pointer relative group"
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
        <!-- Delete Button -->
        <button
          @click.stop="deleteClozeTest(test.id)"
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

const deleteClozeTest = async (id) => {
  if (!confirm('确定要删除这道完形填空题吗？此操作不可撤销。')) return
  try {
    await clozeTestApi.delete(id)
    await fetchClozeTests()
  } catch (e) {
    console.error(e)
    alert('删除失败')
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchClozeTests()
})
</script>
