<script setup lang="ts">
/**
 * AppSidebar — боковая навигация.
 * Пункты меню «Администрирование» показываются только роли Admin.
 */
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  HomeIcon,
  MagnifyingGlassIcon,
  Cog6ToothIcon,
  UsersIcon,
  AdjustmentsHorizontalIcon,
} from '@heroicons/vue/24/outline'

const { t } = useI18n()
const route = useRoute()
const authStore = useAuthStore()

/** Базовые пункты меню — доступны всем авторизованным */
const baseLinks = [
  { to: '/dashboard', icon: HomeIcon, labelKey: 'nav.dashboard' },
  { to: '/search/new', icon: MagnifyingGlassIcon, labelKey: 'nav.newSearch' },
  { to: '/settings', icon: Cog6ToothIcon, labelKey: 'nav.settings' },
]

/** Пункты администрирования — только для Admin */
const adminLinks = [
  { to: '/admin/users', icon: UsersIcon, labelKey: 'admin.users' },
  { to: '/admin/settings', icon: AdjustmentsHorizontalIcon, labelKey: 'admin.globalSettings' },
]

/** Подсветить активный пункт меню */
const isActive = (path: string) =>
  path === '/dashboard'
    ? route.path === '/dashboard'
    : route.path.startsWith(path)
</script>

<template>
  <aside class="w-64 bg-white border-r border-gray-200 flex flex-col">
    <!-- Логотип / заголовок -->
    <div class="h-16 flex items-center px-6 border-b border-gray-200">
      <span class="text-xl font-bold text-indigo-600">LeadGen</span>
    </div>

    <!-- Основная навигация -->
    <nav class="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
      <RouterLink
        v-for="link in baseLinks"
        :key="link.to"
        :to="link.to"
        class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
        :class="isActive(link.to)
          ? 'bg-indigo-50 text-indigo-700'
          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'"
      >
        <component :is="link.icon" class="w-5 h-5 flex-shrink-0" />
        {{ t(link.labelKey) }}
      </RouterLink>

      <!-- Блок Администрирование (только Admin) -->
      <template v-if="authStore.isAdmin">
        <div class="pt-4 pb-1">
          <p class="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider">
            {{ t('nav.admin') }}
          </p>
        </div>
        <RouterLink
          v-for="link in adminLinks"
          :key="link.to"
          :to="link.to"
          class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
          :class="isActive(link.to)
            ? 'bg-indigo-50 text-indigo-700'
            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'"
        >
          <component :is="link.icon" class="w-5 h-5 flex-shrink-0" />
          {{ t(link.labelKey) }}
        </RouterLink>
      </template>
    </nav>
  </aside>
</template>
