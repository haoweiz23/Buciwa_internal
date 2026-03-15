import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000, // 2 minutes timeout for image generation
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
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
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// Word Set API
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

// Word API
export const wordApi = {
  // Regenerate image for a specific word
  regenerateImage: (wordId) => api.post(`/words/${wordId}/regenerate-image`)
}

// Cloze Test API
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

// Listening Exercise API
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

export default api
