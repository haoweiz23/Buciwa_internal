<template>
  <div class="min-h-screen p-3 sm:p-4 md:p-8">
    <!-- Header -->
    <header class="max-w-4xl mx-auto mb-6 sm:mb-8">
      <div class="text-center">
        <h1 class="text-2xl sm:text-3xl md:text-4xl font-bold text-mint-700 mb-1 sm:mb-2">
          🌿 单词视觉记忆
        </h1>
        <p class="text-mint-600 text-xs sm:text-sm md:text-base">
          通过视觉记忆学习单词
        </p>
      </div>
    </header>

    <!-- Navigation Tabs -->
    <div class="max-w-4xl mx-auto mb-6">
      <div class="flex justify-center gap-2 sm:gap-4">
        <button
          @click="currentTab = 'words'"
          :class="currentTab === 'words' 
            ? 'bg-mint-500 text-white' 
            : 'bg-white text-mint-600 hover:bg-mint-50'"
          class="px-4 sm:px-6 py-2 sm:py-3 rounded-xl font-medium transition-colors text-sm sm:text-base"
        >
          📚 单词记忆
        </button>
        <button
          @click="currentTab = 'cloze'"
          :class="currentTab === 'cloze' 
            ? 'bg-mint-500 text-white' 
            : 'bg-white text-mint-600 hover:bg-mint-50'"
          class="px-4 sm:px-6 py-2 sm:py-3 rounded-xl font-medium transition-colors text-sm sm:text-base"
        >
          📝 完形填空
        </button>
        <button
          @click="currentTab = 'listening'"
          :class="currentTab === 'listening' 
            ? 'bg-mint-500 text-white' 
            : 'bg-white text-mint-600 hover:bg-mint-50'"
          class="px-4 sm:px-6 py-2 sm:py-3 rounded-xl font-medium transition-colors text-sm sm:text-base"
        >
          🎧 听力练习
        </button>
      </div>
    </div>

    <!-- Words Tab Content -->
    <div v-show="currentTab === 'words'" class="max-w-4xl mx-auto">
      <div class="text-center py-8">
        <div class="text-6xl mb-4">📚</div>
        <h2 class="text-xl font-semibold text-mint-700 mb-2">单词视觉记忆</h2>
        <p class="text-mint-600 mb-6">输入英文单词，生成视觉隔离的四选项练习</p>
        <div class="flex justify-center gap-4">
          <button
            @click="goToWordList"
            class="px-6 py-3 bg-white text-mint-600 rounded-xl
                   hover:bg-mint-50 transition-colors font-medium
                   border-2 border-mint-200"
          >
            查看题目列表
          </button>
          <button
            @click="goToWordCreate"
            class="px-6 py-3 bg-mint-500 text-white rounded-xl
                   hover:bg-mint-600 transition-colors font-medium"
          >
            创建新题目
          </button>
        </div>
      </div>
    </div>

    <!-- Cloze Tab Content -->
    <div v-show="currentTab === 'cloze'" class="max-w-4xl mx-auto">
      <div class="text-center py-8">
        <div class="text-6xl mb-4">📝</div>
        <h2 class="text-xl font-semibold text-mint-700 mb-2">完形填空练习</h2>
        <p class="text-mint-600 mb-6">输入两个英文单词，生成完形填空题目</p>
        <div class="flex justify-center gap-4">
          <button
            @click="goToClozeList"
            class="px-6 py-3 bg-white text-mint-600 rounded-xl
                   hover:bg-mint-50 transition-colors font-medium
                   border-2 border-mint-200"
          >
            查看题目列表
          </button>
          <button
            @click="goToClozeCreate"
            class="px-6 py-3 bg-mint-500 text-white rounded-xl
                   hover:bg-mint-600 transition-colors font-medium"
          >
            创建新题目
          </button>
        </div>
      </div>
    </div>

    <!-- Listening Tab Content -->
    <div v-show="currentTab === 'listening'" class="max-w-4xl mx-auto">
      <div class="text-center py-8">
        <div class="text-6xl mb-4">🎧</div>
        <h2 class="text-xl font-semibold text-mint-700 mb-2">听力练习</h2>
        <p class="text-mint-600 mb-6">输入场景描述，生成听力练习</p>
        <div class="flex justify-center gap-4">
          <button
            @click="goToListeningList"
            class="px-6 py-3 bg-white text-mint-600 rounded-xl
                   hover:bg-mint-50 transition-colors font-medium
                   border-2 border-mint-200"
          >
            查看练习列表
          </button>
          <button
            @click="goToListeningCreate"
            class="px-6 py-3 bg-mint-500 text-white rounded-xl
                   hover:bg-mint-600 transition-colors font-medium"
          >
            创建新练习
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// State
const currentTab = ref('words')

// Navigation methods
const goToWordList = () => {
  router.push({ name: 'word-list' })
}

const goToWordCreate = () => {
  router.push({ name: 'word-list' })
}

const goToClozeList = () => {
  router.push({ name: 'cloze-list' })
}

const goToClozeCreate = () => {
  router.push({ name: 'cloze-test' })
}

const goToListeningList = () => {
  router.push({ name: 'listening-list' })
}

const goToListeningCreate = () => {
  router.push({ name: 'listening-test' })
}
</script>
