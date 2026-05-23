<script setup lang="ts">
/**
 * App.vue — корневой компонент.
 * Защищённые страницы оборачиваются в AppLayout (sidebar + header).
 * Публичные страницы (Login) рендерятся напрямую.
 */
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppLayout from '@/components/layout/AppLayout.vue'

const authStore = useAuthStore()
</script>

<template>
  <AppLayout v-if="authStore.isAuthenticated">
    <RouterView />
  </AppLayout>
  <RouterView v-else />
</template>
