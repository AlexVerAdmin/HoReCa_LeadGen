<script setup lang="ts">
/**
 * AppLayout — обёртка всех защищённых страниц.
 * Структура: sidebar слева + header сверху + контентная область со slot.
 */
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import { useUiStore } from '@/stores/ui'

const uiStore = useUiStore()
</script>

<template>
  <div class="flex h-screen bg-gray-50 overflow-hidden">
    <!-- Sidebar -->
    <AppSidebar />

    <!-- Основная колонка: header + контент -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <AppHeader />
      <main class="flex-1 overflow-y-auto p-6">
        <slot />
      </main>
    </div>
  </div>
</template>
