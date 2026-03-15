<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold text-gray-800 mb-6">测验结果管理</h1>
    
    <!-- Results List -->
    <div v-if="results.length > 0" class="space-y-4">
      <div 
        v-for="result in results" 
        :key="result.id"
        class="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow"
      >
        <div class="flex justify-between items-start">
          <div>
            <h3 class="font-medium text-gray-800">{{ result.quiz_set_name }}</h3>
            <p class="text-sm text-gray-500 mt-1">
              {{ formatDate(result.created_at) }}
            </p>
          </div>
          <div class="text-right">
            <div class="text-2xl font-bold" :class="getScoreColor(result.score_percentage)">
              {{ result.score_percentage.toFixed(0) }}%
            </div>
            <p class="text-sm text-gray-500">
              {{ result.correct_answers }} / {{ result.total_questions }} 正确
            </p>
          </div>
        </div>
        
        <!-- Expand button -->
        <button 
          @click="toggleExpand(result.id)"
          class="mt-3 text-sm text-mint-600 hover:text-mint-700"
        >
          {{ expandedId === result.id ? '收起详情' : '查看详情' }}
        </button>
        
        <!-- Expanded details -->
        <div v-if="expandedId === result.id" class="mt-4 border-t pt-4">
          <!-- Wrong Questions Summary -->
          <div v-if="getWrongQuestions(result).length > 0" class="mb-4 p-4 bg-red-50 rounded-lg border border-red-200">
            <h4 class="font-medium text-red-700 mb-3 flex items-center">
              <span class="mr-2">📝</span>
              错题列表 ({{ getWrongQuestions(result).length }}题)
            </h4>
            <div class="space-y-3">
              <div
                v-for="(question, index) in getWrongQuestions(result)"
                :key="index"
                class="p-3 bg-white rounded border"
                :class="question.question_type === 'word' ? 'border-blue-200' : 'border-green-200'"
              >
                <div class="flex items-center gap-2 mb-2">
                  <span
                    class="px-2 py-0.5 rounded text-xs font-medium"
                    :class="question.question_type === 'word' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'"
                  >
                    {{ question.question_type === 'word' ? '单选题' : '完形填空' }}
                  </span>
                  <span class="font-medium text-gray-800">
                    {{ question.main_word || question.sentence?.substring(0, 30) + '...' }}
                  </span>
                </div>
                <div class="flex gap-6 text-sm">
                  <div>
                    <span class="text-gray-500">用户答案：</span>
                    <span class="text-red-600 font-medium">{{ question.selected_answer }}</span>
                  </div>
                  <div>
                    <span class="text-gray-500">正确答案：</span>
                    <span class="text-green-600 font-medium">{{ question.correct_answer }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Word Results -->
          <div v-if="getWordResults(result).length > 0">
            <h4 class="font-medium text-gray-700 mb-2">单选题结果</h4>
            <div class="space-y-2">
              <div
                v-for="(word, index) in getWordResults(result)"
                :key="index"
                class="flex items-center justify-between p-2 rounded"
                :class="word.is_correct ? 'bg-green-50' : 'bg-red-50'"
              >
                <div>
                  <span class="font-medium">{{ word.main_word }}</span>
                  <span class="text-sm text-gray-500 ml-2">
                    选择: {{ word.selected_word }}
                  </span>
                  <span v-if="!word.is_correct && word.correct_word" class="text-sm text-green-600 ml-2">
                    正确答案: {{ word.correct_word }}
                  </span>
                </div>
                <span :class="word.is_correct ? 'text-green-500' : 'text-red-500'">
                  {{ word.is_correct ? '✓' : '✗' }}
                </span>
              </div>
            </div>
          </div>
          
          <!-- Cloze Results -->
          <div v-if="getClozeResults(result).length > 0" class="mt-4">
            <h4 class="font-medium text-gray-700 mb-2">完形填空结果</h4>
            <div class="space-y-2">
              <div
                v-for="(cloze, index) in getClozeResults(result)"
                :key="index"
                class="p-2 rounded"
                :class="cloze.is_correct ? 'bg-green-50' : 'bg-red-50'"
              >
                <div class="flex items-center justify-between">
                  <div class="flex-1">
                    <p v-if="cloze.sentence" class="text-sm text-gray-600 mb-1">{{ cloze.sentence?.substring(0, 50) }}...</p>
                    <div class="flex gap-4 text-sm">
                      <span>
                        填空1:
                        <span :class="cloze.selected_answer1 === cloze.correct_answer1 ? 'text-green-600' : 'text-red-600'">
                          {{ cloze.selected_answer1 }}
                        </span>
                        <span v-if="cloze.selected_answer1 !== cloze.correct_answer1 && cloze.correct_answer1" class="text-green-600">
                          (正确: {{ cloze.correct_answer1 }})
                        </span>
                      </span>
                      <span>
                        填空2:
                        <span :class="cloze.selected_answer2 === cloze.correct_answer2 ? 'text-green-600' : 'text-red-600'">
                          {{ cloze.selected_answer2 }}
                        </span>
                        <span v-if="cloze.selected_answer2 !== cloze.correct_answer2 && cloze.correct_answer2" class="text-green-600">
                          (正确: {{ cloze.correct_answer2 }})
                        </span>
                      </span>
                    </div>
                  </div>
                  <span :class="cloze.is_correct ? 'text-green-500' : 'text-red-500'">
                    {{ cloze.is_correct ? '✓' : '✗' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Empty State -->
    <div v-else class="text-center py-12">
      <p class="text-gray-500">暂无测验结果</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { testApi } from '../../api'

const results = ref([])
const expandedId = ref(null)

const fetchResults = async () => {
  try {
    const data = await testApi.getResults()
    results.value = data
  } catch (e) {
    console.error('Failed to fetch results:', e)
  }
}

const toggleExpand = (id) => {
  expandedId.value = expandedId.value === id ? null : id
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getScoreColor = (percentage) => {
  if (percentage >= 80) return 'text-green-500'
  if (percentage >= 60) return 'text-yellow-500'
  return 'text-red-500'
}

const getWordResults = (result) => {
  if (!result.word_results) return []
  try {
    return typeof result.word_results === 'string' 
      ? JSON.parse(result.word_results) 
      : result.word_results
  } catch {
    return []
  }
}

const getClozeResults = (result) => {
  if (!result.cloze_results) return []
  try {
    return typeof result.cloze_results === 'string'
      ? JSON.parse(result.cloze_results)
      : result.cloze_results
  } catch {
    return []
  }
}

const getWrongQuestions = (result) => {
  if (!result.wrong_questions) return []
  try {
    return typeof result.wrong_questions === 'string'
      ? JSON.parse(result.wrong_questions)
      : result.wrong_questions
  } catch {
    return []
  }
}

onMounted(() => {
  fetchResults()
})
</script>
