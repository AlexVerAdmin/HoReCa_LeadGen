<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()

const email    = ref('')
const password = ref('')
const error    = ref('')
const loading  = ref(false)

const handleLogin = async () => {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(email.value, password.value)
    router.push('/dashboard')
  } catch {
    error.value = t('auth.invalidCredentials')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="w-full max-w-sm bg-white rounded-2xl shadow-md p-8">

      <!-- Логотип / заголовок -->
      <div class="mb-8 text-center">
        <h1 class="text-2xl font-bold text-gray-800">LeadGen Scout</h1>
        <p class="text-sm text-gray-500 mt-1">HoReCa Lead Management</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-5" novalidate>

        <!-- Email -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            {{ t('auth.email') }}
          </label>
          <input
            v-model="email"
            type="email"
            autocomplete="email"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm
                   focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
                   disabled:bg-gray-100"
            :disabled="loading"
          />
        </div>

        <!-- Password -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            {{ t('auth.password') }}
          </label>
          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm
                   focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
                   disabled:bg-gray-100"
            :disabled="loading"
          />
        </div>

        <!-- Ошибка -->
        <p v-if="error" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
          {{ error }}
        </p>

        <!-- Кнопка -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full py-2 px-4 bg-indigo-600 text-white text-sm font-medium rounded-lg
                 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500
                 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
        >
          <span v-if="loading">{{ t('common.loading') }}</span>
          <span v-else>{{ t('auth.loginBtn') }}</span>
        </button>

      </form>
    </div>
  </div>
</template>
