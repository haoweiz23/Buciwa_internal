<template>
  <div
    class="bg-white rounded-xl sm:rounded-2xl shadow-soft p-3 sm:p-4 card-hover cursor-pointer
           flex items-center gap-3 sm:gap-4 relative group
           active:scale-[0.98] touch-manipulation"
    @click="$emit('click')"
  >
    <!-- Thumbnail -->
    <div class="w-14 h-14 sm:w-16 sm:h-16 md:w-20 md:h-20 rounded-lg sm:rounded-xl overflow-hidden flex-shrink-0
                bg-gradient-to-br from-macaron-pink to-macaron-lavender">
      <img
        v-if="wordSet.main_word_image"
        :src="wordSet.main_word_image"
        :alt="wordSet.main_word"
        class="w-full h-full object-cover"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-xl sm:text-2xl">
        📷
      </div>
    </div>

    <!-- Word Info -->
    <div class="flex-1 min-w-0">
      <h3 class="text-base sm:text-lg md:text-xl font-bold text-gray-800 truncate">
        {{ wordSet.main_word }}
      </h3>
      <p class="text-xs sm:text-sm text-gray-500 mt-0.5 sm:mt-1">
        {{ formatDate(wordSet.created_at) }}
      </p>
    </div>

    <!-- Arrow Icon -->
    <div class="text-mint-400 group-hover:text-mint-600 transition-colors flex-shrink-0">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="sm:w-6 sm:h-6">
        <path d="M9 18l6-6-6-6"/>
      </svg>
    </div>

    <!-- Delete Button -->
    <button
      @click.stop="handleDelete"
      class="absolute top-1.5 right-1.5 sm:top-2 sm:right-2 p-1.5 sm:p-2 rounded-full
             opacity-60 sm:opacity-0 sm:group-hover:opacity-100
             bg-red-50 text-red-400 hover:bg-red-100 hover:text-red-600
             active:scale-90 touch-manipulation
             transition-all"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="sm:w-4 sm:h-4">
        <path d="M3 6h18"/>
        <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/>
        <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  wordSet: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['click', 'delete'])

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const handleDelete = () => {
  if (confirm(`确定删除 "${props.wordSet.main_word}" 吗？`)) {
    emit('delete', props.wordSet.id)
  }
}
</script>
