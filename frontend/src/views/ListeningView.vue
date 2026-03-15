<template>
  <div class="min-h-screen p-3 sm:p-4 md:p-8">
    <!-- Header -->
    <header class="max-w-4xl mx-auto mb-6 sm:mb-8">
      <div class="flex items-center justify-between">
        <button
          @click="goBack"
          class="px-4 py-2 text-mint-600 hover:text-mint-700 flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          返回
        </button>
        <h1 class="text-xl sm:text-2xl font-bold text-mint-700">听力练习</h1>
        <div class="w-16"></div>
      </div>
    </header>

    <!-- Input Section -->
    <div class="max-w-2xl mx-auto mb-6 md:mb-8 px-2 sm:px-0">
      <div class="bg-white rounded-2xl shadow-soft p-4 sm:p-6">
        <div class="space-y-4">
          <textarea
            v-model="sceneDescription"
            placeholder="输入场景描述，例如：一个人在公园里跑步..."
            rows="3"
            class="w-full px-4 py-3 rounded-xl border-2 border-mint-200
                   focus:border-mint-400 focus:outline-none
                   text-gray-700 placeholder-gray-400
                   transition-colors text-base resize-none"
            :disabled="isGenerating"
          ></textarea>
          <button
            @click="generateExercise"
            :disabled="!sceneDescription.trim() || isGenerating"
            class="w-full px-6 py-3 bg-mint-500 text-white rounded-xl
                   hover:bg-mint-600 disabled:bg-gray-300
                   disabled:cursor-not-allowed
                   transition-colors font-medium
                   flex items-center justify-center gap-2"
          >
            <span v-if="!isGenerating">生成练习</span>
            <span v-else class="flex items-center gap-2">
              <svg class="w-5 h-5 spinner" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              生成中...
            </span>
          </button>
        </div>
        <p v-if="error" class="mt-3 text-red-500 text-sm text-center">
          {{ error }}
        </p>
      </div>
    </div>

    <!-- Result Section -->
    <div v-if="exercise" class="max-w-2xl mx-auto px-2 sm:px-0">
      <!-- Image -->
      <div v-if="exercise.image_local_path" class="mb-6">
        <img
          :src="exercise.image_local_path"
          alt="Listening exercise image"
          class="w-full rounded-2xl shadow-soft"
        />
      </div>

      <!-- Audio Player -->
      <div v-if="exercise.audio_local_path" class="bg-white rounded-2xl shadow-soft p-6 mb-6">
        <h3 class="text-lg font-semibold text-mint-700 mb-4">听力音频</h3>
        <div class="flex flex-col items-center gap-4">
          <audio
            ref="audioPlayer"
            :src="exercise.audio_local_path"
            @ended="onAudioEnded"
            class="hidden"
          ></audio>
          
          <!-- Play/Pause Button -->
          <button
            @click="togglePlay"
            class="w-20 h-20 rounded-full bg-mint-500 text-white
                   hover:bg-mint-600 transition-colors
                   flex items-center justify-center shadow-lg"
          >
            <svg v-if="!isPlaying" class="w-10 h-10 ml-1" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z"/>
            </svg>
            <svg v-else class="w-10 h-10" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
            </svg>
          </button>

          <!-- Loop Toggle -->
          <div class="flex items-center gap-2">
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                v-model="isLooping"
                class="w-4 h-4 text-mint-500 rounded border-gray-300
                       focus:ring-mint-500"
              />
              <span class="text-gray-600">循环播放</span>
            </label>
          </div>

          <!-- Progress Bar -->
          <div class="w-full">
            <div class="flex justify-between text-sm text-gray-500 mb-1">
              <span>{{ formatTime(currentTime) }}</span>
              <span>{{ formatTime(duration) }}</span>
            </div>
            <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                class="h-full bg-mint-500 transition-all duration-100"
                :style="{ width: `${progress}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Transcript -->
      <div class="bg-white rounded-2xl shadow-soft p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-mint-700">听力文本</h3>
          <button
            @click="showTranscript = !showTranscript"
            class="text-mint-600 hover:text-mint-700 text-sm"
          >
            {{ showTranscript ? '隐藏文本' : '显示文本' }}
          </button>
        </div>
        <p v-if="showTranscript" class="text-gray-700 leading-relaxed">
          {{ exercise.generated_text }}
        </p>
        <p v-else class="text-gray-400 italic">
          点击"显示文本"查看听力内容
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { listeningExerciseApi } from '../api'

const router = useRouter()
const route = useRoute()

// State
const sceneDescription = ref('')
const isGenerating = ref(false)
const isLoading = ref(false)
const error = ref('')
const exercise = ref(null)
const audioPlayer = ref(null)
const isPlaying = ref(false)
const isLooping = ref(true)
const currentTime = ref(0)
const duration = ref(0)
const showTranscript = ref(false)

// Computed
const progress = ref(0)

// Methods
const generateExercise = async () => {
  if (!sceneDescription.value.trim()) return
  
  isGenerating.value = true
  error.value = ''
  exercise.value = null
  isPlaying.value = false
  currentTime.value = 0
  duration.value = 0
  progress.value = 0
  showTranscript.value = false
  
  try {
    const result = await listeningExerciseApi.generate(sceneDescription.value.trim())
    exercise.value = result
  } catch (e) {
    error.value = '生成练习失败，请重试。'
    console.error(e)
  } finally {
    isGenerating.value = false
  }
}

const loadExercise = async (id) => {
  isLoading.value = true
  error.value = ''
  try {
    exercise.value = await listeningExerciseApi.get(id)
  } catch (e) {
    error.value = '加载练习失败，请重试。'
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const togglePlay = () => {
  if (!audioPlayer.value) return
  
  if (isPlaying.value) {
    audioPlayer.value.pause()
    isPlaying.value = false
  } else {
    audioPlayer.value.play()
    isPlaying.value = true
  }
}

const onAudioEnded = () => {
  if (isLooping.value && audioPlayer.value) {
    audioPlayer.value.currentTime = 0
    audioPlayer.value.play()
  } else {
    isPlaying.value = false
  }
}

const updateProgress = () => {
  if (!audioPlayer.value) return
  
  currentTime.value = audioPlayer.value.currentTime
  duration.value = audioPlayer.value.duration || 0
  
  if (duration.value > 0) {
    progress.value = (currentTime.value / duration.value) * 100
  }
}

const formatTime = (time) => {
  if (!time || isNaN(time)) return '0:00'
  
  const minutes = Math.floor(time / 60)
  const seconds = Math.floor(time % 60)
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
}

const goBack = () => {
  router.push({ name: 'listening-list' })
}

// Lifecycle
onMounted(async () => {
  const id = route.params.id
  if (id) {
    // Load existing exercise
    await loadExercise(id)
  }
  
  if (audioPlayer.value) {
    audioPlayer.value.addEventListener('timeupdate', updateProgress)
    audioPlayer.value.addEventListener('loadedmetadata', () => {
      duration.value = audioPlayer.value.duration
    })
  }
})

onUnmounted(() => {
  if (audioPlayer.value) {
    audioPlayer.value.removeEventListener('timeupdate', updateProgress)
  }
})

// Watch for audio player ref changes
watch(audioPlayer, (newPlayer) => {
  if (newPlayer) {
    newPlayer.addEventListener('timeupdate', updateProgress)
    newPlayer.addEventListener('loadedmetadata', () => {
      duration.value = newPlayer.duration
    })
  }
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
</style>
