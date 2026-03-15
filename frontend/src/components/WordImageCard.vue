<template>
  <div
    class="relative rounded-xl sm:rounded-2xl overflow-hidden shadow-card
           bg-white transition-all"
    :class="cardColorClass"
  >
    <!-- Image Container -->
    <div class="aspect-square relative overflow-hidden">
      <!-- Loading State -->
      <div
        v-if="isRegenerating"
        class="absolute inset-0 flex flex-col items-center justify-center
               bg-gradient-to-br from-gray-100 to-gray-200 z-10"
      >
        <div class="w-8 h-8 sm:w-10 sm:h-10 border-4 border-mint-200 border-t-mint-500 rounded-full spinner"></div>
        <p class="text-mint-600 mt-2 text-xs sm:text-sm">生成中...</p>
      </div>

      <!-- Image -->
      <img
        v-if="word.image_local_path || word.image_url"
        :src="word.image_local_path || word.image_url"
        :alt="word.word"
        class="w-full h-full object-cover transition-transform hover:scale-105"
        :class="{ 'opacity-50': isRegenerating }"
      />
      
      <!-- Placeholder -->
      <div
        v-else
        class="w-full h-full flex items-center justify-center
               bg-gradient-to-br from-macaron-pink/30 to-macaron-lavender/30"
      >
        <span class="text-3xl sm:text-4xl">🖼️</span>
      </div>

      <!-- Refresh Button -->
      <button
        @click="$emit('regenerate', word.id)"
        :disabled="isRegenerating"
        class="absolute top-2 right-2 sm:top-3 sm:right-3 p-1.5 sm:p-2 rounded-full
               bg-white/80 backdrop-blur-sm shadow-soft
               hover:bg-white hover:shadow-md
               active:scale-90 touch-manipulation
               disabled:opacity-50 disabled:cursor-not-allowed
               transition-all refresh-btn"
        title="重新生成图片"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          :class="{ 'spinner': isRegenerating }"
          class="text-gray-600 sm:w-[18px] sm:h-[18px]"
        >
          <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
          <path d="M3 3v5h5"/>
          <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/>
          <path d="M16 16h5v5"/>
        </svg>
      </button>
    </div>

    <!-- Word Label -->
    <div class="p-2 sm:p-3 md:p-4">
      <div class="flex items-center justify-between gap-1">
        <div class="flex-1 min-w-0">
          <h3 class="text-base sm:text-lg md:text-xl font-bold text-gray-800 truncate">
            {{ word.word }}
          </h3>
          <p v-if="word.meaning" class="text-xs sm:text-sm text-gray-500 mt-0.5 sm:mt-1 line-clamp-2">
            {{ word.meaning }}
          </p>
        </div>
        <span
          class="text-[10px] sm:text-xs px-1.5 sm:px-2 py-0.5 sm:py-1 rounded-full flex-shrink-0"
          :class="typeBadgeClass"
        >
          {{ typeLabel }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps, defineEmits } from 'vue'

const props = defineProps({
  word: {
    type: Object,
    required: true
  },
  isRegenerating: {
    type: Boolean,
    default: false
  }
})

defineEmits(['regenerate'])

// Word type labels
const typeLabels = {
  main: '主词',
  similar: '形近词',
  synonym: '无关词',
  antonym: '无关词'
}

// Computed
const typeLabel = computed(() => typeLabels[props.word.word_type] || props.word.word_type)

const cardColorClass = computed(() => {
  const colors = {
    main: 'border-t-4 border-t-macaron-mint',
    similar: 'border-t-4 border-t-macaron-pink',
    synonym: 'border-t-4 border-t-macaron-blue',
    antonym: 'border-t-4 border-t-macaron-lavender'
  }
  return colors[props.word.word_type] || ''
})

const typeBadgeClass = computed(() => {
  const classes = {
    main: 'bg-macaron-mint/30 text-green-700',
    similar: 'bg-macaron-pink/30 text-pink-700',
    synonym: 'bg-macaron-blue/30 text-blue-700',
    antonym: 'bg-macaron-lavender/30 text-purple-700'
  }
  return classes[props.word.word_type] || 'bg-gray-100 text-gray-700'
})
</script>
