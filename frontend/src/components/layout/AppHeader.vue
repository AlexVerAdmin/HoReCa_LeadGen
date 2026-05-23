<script setup lang="ts">
/**
 * AppHeader — верхняя панель навигации.
 * Показывает заголовок текущей страницы, LanguageSwitcher, имя пользователя и кнопку выхода.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { ArrowRightOnRectangleIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'
import LanguageSwitcher from '@/components/common/LanguageSwitcher.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

/** Заголовок страницы из meta.title — i18n ключ */
const pageTitle = computed(() => {
  const key = route.meta?.title as string
  return key ? t(key) : ''
})

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 flex-shrink-0">
    <!-- Заголовок текущей страницы -->
    <h1 class="text-lg font-semibold text-gray-800">{{ pageTitle }}</h1>

    <!-- Правая часть: язык + пользователь + выход -->
    <div class="flex items-center gap-4">
      <LanguageSwitcher />

      <!-- Имя пользователя -->
      <span class="text-sm text-gray-600">
        {{ authStore.user?.username ?? authStore.user?.email }}
      </span>

      <!-- Кнопка выхода -->
      <button
        class="flex items-center gap-1 text-sm text-gray-500 hover:text-red-600 transition-colors"
        @click="logout"
      >
        <ArrowRightOnRectangleIcon class="w-5 h-5" />
        {{ t('nav.logout') }}
      </button>
    </div>
  </header>
</template>
