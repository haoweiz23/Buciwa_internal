<template>
  <div class="min-h-screen bg-gradient-to-br from-mint-50 via-mint-100 to-mint-200 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold text-mint-700">管理后台登录</h1>
        <p class="text-gray-500 mt-2">请输入管理员账号密码</p>
      </div>
      
      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-medium mb-2">用户名</label>
          <input
            v-model="username"
            type="text"
            class="w-full px-4 py-3 rounded-xl border-2 border-gray-200
                   focus:border-mint-400 focus:outline-none
                   text-gray-700 placeholder-gray-400
                   transition-colors"
            placeholder="请输入用户名"
            :disabled="isLoading"
          />
        </div>
        
        <div class="mb-6">
          <label class="block text-gray-700 text-sm font-medium mb-2">密码</label>
          <input
            v-model="password"
            type="password"
            class="w-full px-4 py-3 rounded-xl border-2 border-gray-200
                   focus:border-mint-400 focus:outline-none
                   text-gray-700 placeholder-gray-400
                   transition-colors"
            placeholder="请输入密码"
            :disabled="isLoading"
          />
        </div>
        
        <p v-if="error" class="mb-4 text-red-500 text-sm text-center">
          {{ error }}
        </p>
        
        <button
          type="submit"
          :disabled="!username || !password || isLoading"
          class="w-full px-4 py-3 bg-mint-500 text-white rounded-xl
                 hover:bg-mint-600 disabled:bg-gray-300
                 disabled:cursor-not-allowed
                 transition-colors font-medium
                 flex items-center justify-center gap-2"
        >
          <span v-if="!isLoading">登录</span>
          <span v-else class="flex items-center gap-2">
            <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            登录中...
          </span>
        </button>
      </form>
      
      <div class="mt-6 text-center">
        <router-link to="/" class="text-mint-600 hover:text-mint-700 text-sm">
          返回用户首页
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authApi } from '../../api'

const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (!username.value || !password.value) return
  
  isLoading.value = true
  error.value = ''
  
  try {
    const result = await authApi.login(username.value, password.value)
    
    // Save token and user info
    localStorage.setItem('token', result.access_token)
    localStorage.setItem('username', result.username)
    localStorage.setItem('role', result.role)
    
    // Redirect to admin or original destination
    const redirect = route.query.redirect || '/admin'
    router.push(redirect)
  } catch (e) {
    if (e.response?.status === 401) {
      error.value = '用户名或密码错误'
    } else {
      error.value = '登录失败，请重试'
    }
    console.error(e)
  } finally {
    isLoading.value = false
  }
}
</script>
