import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000, // 2 minutes timeout for image generation
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('role')
      if (window.location.pathname.startsWith('/admin')) {
        window.location.href = '/login'
      }
    }
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// ============== Auth API ==============
export const authApi = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  getMe: () => api.get('/auth/me')
}

// ============== Word Set API ==============
export const wordSetApi = {
  // Get all word sets
  list: () => api.get('/word-sets'),
  
  // Get a specific word set
  get: (id) => api.get(`/word-sets/${id}`),
  
  // Generate a new word set
  generate: (word) => api.post('/word-sets/generate', { word }),
  
  // Regenerate all words in a word set
  regenerate: (id) => api.post(`/word-sets/${id}/regenerate`),
  
  // Delete a word set
  delete: (id) => api.delete(`/word-sets/${id}`),
  
  // Get a random word for dice roll
  getRandomWord: () => api.get('/random-word')
}

// ============== Word API ==============
export const wordApi = {
  // Regenerate image for a specific word
  regenerateImage: (wordId) => api.post(`/words/${wordId}/regenerate-image`)
}

// ============== Cloze Test API ==============
export const clozeTestApi = {
  // Get all cloze tests
  list: () => api.get('/cloze-tests'),
  
  // Get a specific cloze test
  get: (id) => api.get(`/cloze-tests/${id}`),
  
  // Generate a new cloze test
  generate: (word1, word2) => api.post('/cloze-tests/generate', { word1, word2 }),
  
  // Delete a cloze test
  delete: (id) => api.delete(`/cloze-tests/${id}`)
}

// ============== Listening Exercise API ==============
export const listeningExerciseApi = {
  // Get all listening exercises
  list: () => api.get('/listening-exercises'),
  
  // Get a specific listening exercise
  get: (id) => api.get(`/listening-exercises/${id}`),
  
  // Generate a new listening exercise
  generate: (sceneDescription) => api.post('/listening-exercises/generate', { scene_description: sceneDescription }),
  
  // Delete a listening exercise
  delete: (id) => api.delete(`/listening-exercises/${id}`)
}

// ============== Quiz Set API ==============
export const quizSetApi = {
  // Get all quiz sets
  list: () => api.get('/quiz-sets'),
  
  // Get a specific quiz set
  get: (id) => api.get(`/quiz-sets/${id}`),
  
  // Create a new quiz set
  create: (data) => api.post('/quiz-sets', data),
  
  // Update a quiz set
  update: (id, data) => api.put(`/quiz-sets/${id}`, data),
  
  // Delete a quiz set
  delete: (id) => api.delete(`/quiz-sets/${id}`),
  
  // Activate a quiz set
  activate: (id) => api.post(`/quiz-sets/${id}/activate`),
  
  // Get active quiz set
  getActive: () => api.get('/quiz-sets/active'),
  
  // Add word set to quiz set
  addWord: (quizSetId, wordSetId, order) => 
    api.post(`/quiz-sets/${quizSetId}/words`, { word_set_id: wordSetId, order }),
  
  // Remove word from quiz set
  removeWord: (quizSetId, itemId) => 
    api.delete(`/quiz-sets/${quizSetId}/words/${itemId}`),
  
  // Add cloze test to quiz set
  addCloze: (quizSetId, clozeTestId, order) => 
    api.post(`/quiz-sets/${quizSetId}/cloze`, { cloze_test_id: clozeTestId, order }),
  
  // Remove cloze from quiz set
  removeCloze: (quizSetId, itemId) => 
    api.delete(`/quiz-sets/${quizSetId}/cloze/${itemId}`),
  
  // Reorder items
  reorder: (quizSetId, wordItems, clozeItems) => 
    api.put(`/quiz-sets/${quizSetId}/reorder`, { word_items: wordItems, cloze_items: clozeItems })
}

// ============== Test API ==============
export const testApi = {
  // Get active test
  getActive: () => api.get('/test/active'),
  
  // Submit test result
  submit: (data) => api.post('/test/submit', data),
  
  // Get all test results
  getResults: () => api.get('/test/results'),
  
  // Get a specific test result
  getResult: (id) => api.get(`/test/results/${id}`)
}

export default api
