<script setup lang="ts">
/**
 * DashboardView — история поисков пользователя.
 * Загружает список при монтировании, поддерживает удаление с подтверждением.
 */
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import { PlusIcon, EyeIcon, TrashIcon } from '@heroicons/vue/24/outline'
import { useSearchStore } from '@/stores/search'
import StatusBadge from '@/components/common/StatusBadge.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import type { Search } from '@/types'

const { t } = useI18n()
const searchStore = useSearchStore()

// ─── Подтверждение удаления ───────────────────────────────────────────────
const confirmOpen = ref(false)
const pendingDeleteId = ref<number | null>(null)

const requestDelete = (id: number) => {
  pendingDeleteId.value = id
  confirmOpen.value = true
}

const confirmDelete = async () => {
  if (pendingDeleteId.value !== null) {
    await searchStore.removeSearch(pendingDeleteId.value)
    pendingDeleteId.value = null
  }
}

// ─── Форматирование даты ──────────────────────────────────────────────────
const formatDate = (iso: string) =>
  new Date(iso).toLocaleString(undefined, {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })

/** Радиус в метрах → километры для отображения */
const radiusKm = (m: number) => (m / 1000).toFixed(1)

onMounted(() => searchStore.loadSearches())
</script>

<template>
  <div>
    <!-- Шапка страницы -->
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-semibold text-gray-800">{{ t('search.history') }}</h2>
      <RouterLink
        to="/search/new"
        class="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
      >
        <PlusIcon class="w-4 h-4" />
        {{ t('nav.newSearch') }}
      </RouterLink>
    </div>

    <!-- Ошибка загрузки -->
    <div v-if="searchStore.error" class="mb-4 px-4 py-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
      {{ searchStore.error }}
    </div>

    <!-- Индикатор загрузки -->
    <div v-if="searchStore.loading" class="text-center py-12 text-gray-400">
      {{ t('common.loading') }}
    </div>

    <!-- Пустой список -->
    <div
      v-else-if="searchStore.searches.length === 0"
      class="text-center py-12 text-gray-400"
    >
      <p>{{ t('search.history') }} пуста.</p>
      <RouterLink to="/search/new" class="text-indigo-600 hover:underline text-sm mt-2 inline-block">
        {{ t('nav.newSearch') }}
      </RouterLink>
    </div>

    <!-- Таблица поисков -->
    <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-gray-50 border-b border-gray-200 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            <th class="px-4 py-3">{{ t('search.date') }}</th>
            <th class="px-4 py-3">{{ t('search.types') }}</th>
            <th class="px-4 py-3">{{ t('search.radius') }}</th>
            <th class="px-4 py-3">{{ t('search.found') }} / {{ t('search.qualified') }}</th>
            <th class="px-4 py-3">{{ t('leads.status') }}</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="search in searchStore.searches"
            :key="search.id"
            class="hover:bg-gray-50 transition-colors"
          >
            <!-- Дата -->
            <td class="px-4 py-3 text-gray-700 whitespace-nowrap">
              {{ formatDate(search.created_at) }}
            </td>

            <!-- Типы заведений -->
            <td class="px-4 py-3">
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="pt in search.place_types"
                  :key="pt"
                  class="px-1.5 py-0.5 bg-gray-100 text-gray-600 text-xs rounded"
                >
                  {{ pt }}
                </span>
              </div>
            </td>

            <!-- Радиус -->
            <td class="px-4 py-3 text-gray-700 whitespace-nowrap">
              {{ radiusKm(search.radius) }} км
            </td>

            <!-- Найдено / Квалифицировано -->
            <td class="px-4 py-3 text-gray-700 whitespace-nowrap">
              {{ search.total_found }} / {{ search.qualified_count }}
            </td>

            <!-- Статус -->
            <td class="px-4 py-3">
              <StatusBadge :status="search.status" />
            </td>

            <!-- Действия -->
            <td class="px-4 py-3">
              <div class="flex items-center gap-2 justify-end">
                <RouterLink
                  :to="`/search/${search.id}`"
                  class="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                >
                  <EyeIcon class="w-3.5 h-3.5" />
                  {{ t('search.view') }}
                </RouterLink>
                <button
                  class="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
                  @click="requestDelete(search.id)"
                >
                  <TrashIcon class="w-3.5 h-3.5" />
                  {{ t('common.delete') }}
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Диалог подтверждения удаления -->
    <ConfirmDialog
      v-model:open="confirmOpen"
      :message="t('search.delete') + '?'"
      @confirm="confirmDelete"
    />
  </div>
</template>
