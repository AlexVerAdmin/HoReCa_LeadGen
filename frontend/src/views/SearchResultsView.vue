<script setup lang="ts">
/**
 * SearchResultsView — результаты поиска с polling статуса и таблицей лидов.
 * Слот для modal генерации КП (открывается из LeadsTable).
 */
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ArrowLeftIcon } from '@heroicons/vue/24/outline'
import { useSearchStore } from '@/stores/search'
import StatusBadge from '@/components/common/StatusBadge.vue'
import LeadsTable from '@/components/leads/LeadsTable.vue'
import ProposalGenerateModal from '@/components/proposals/ProposalGenerateModal.vue'
import type { Lead } from '@/types'

const route  = useRoute()
const router = useRouter()
const { t }  = useI18n()
const searchStore = useSearchStore()

const searchId = computed(() => Number(route.params.id))
const error    = ref<string | null>(null)

// ID лида для modal генерации КП (передаётся в F12-modal)
const proposalLeadId = ref<number | null>(null)

// ─── Загрузка данных ──────────────────────────────────────────────────────
onMounted(async () => {
  try {
    await searchStore.loadSearch(searchId.value)
    await searchStore.loadLeads(searchId.value)
    // Запустить polling если поиск ещё выполняется
    if (searchStore.currentSearch?.status === 'in_progress' ||
        searchStore.currentSearch?.status === 'pending') {
      searchStore.pollSearchStatus(searchId.value)
    }
  } catch {
    error.value = t('common.error')
  }
})

// Когда поиск завершается, загрузить лиды ещё раз (могли появиться)
watch(() => searchStore.currentSearch?.status, async (status) => {
  if (status === 'completed') {
    await searchStore.loadLeads(searchId.value)
  }
})

// ─── Обновление лида в store после смены статуса ─────────────────────────
const onStatusUpdated = (updated: Lead) => {
  const idx = searchStore.leads.findIndex(l => l.id === updated.id)
  if (idx !== -1) searchStore.leads[idx] = updated
}

// ─── Форматирование ───────────────────────────────────────────────────────
const formatDate = (iso: string) =>
  new Date(iso).toLocaleString(undefined, {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
const radiusKm = (m: number) => (m / 1000).toFixed(1)
</script>

<template>
  <div class="space-y-6">
    <!-- Навигация назад -->
    <button
      class="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-800 transition-colors"
      @click="router.back()"
    >
      <ArrowLeftIcon class="w-4 h-4" />
      {{ t('nav.dashboard') }}
    </button>

    <!-- Ошибка -->
    <div v-if="error" class="px-4 py-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
      {{ error }}
    </div>

    <!-- Параметры поиска -->
    <div v-if="searchStore.currentSearch" class="bg-white rounded-xl border border-gray-200 p-5">
      <div class="flex items-start justify-between mb-3">
        <h3 class="text-sm font-semibold text-gray-700 uppercase tracking-wide">
          {{ t('search.params') }}
        </h3>
        <StatusBadge :status="searchStore.currentSearch.status" />
      </div>

      <dl class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
        <div>
          <dt class="text-xs text-gray-400">{{ t('search.date') }}</dt>
          <dd class="text-gray-800">{{ formatDate(searchStore.currentSearch.created_at) }}</dd>
        </div>
        <div>
          <dt class="text-xs text-gray-400">{{ t('search.radius') }}</dt>
          <dd class="text-gray-800">{{ radiusKm(searchStore.currentSearch.radius) }} км</dd>
        </div>
        <div>
          <dt class="text-xs text-gray-400">{{ t('search.types') }}</dt>
          <dd class="text-gray-800">{{ searchStore.currentSearch.place_types.join(', ') }}</dd>
        </div>
        <div>
          <dt class="text-xs text-gray-400">{{ t('search.found') }} / {{ t('search.qualified') }}</dt>
          <dd class="text-gray-800 font-medium">
            {{ searchStore.currentSearch.total_found }} / {{ searchStore.currentSearch.qualified_count }}
          </dd>
        </div>
      </dl>

      <!-- Прогресс-индикатор -->
      <div
        v-if="searchStore.currentSearch.status === 'in_progress' || searchStore.currentSearch.status === 'pending'"
        class="mt-4 flex items-center gap-2 text-sm text-indigo-600"
      >
        <svg class="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
        </svg>
        {{ t('common.loading') }}
      </div>
    </div>

    <!-- Загрузка -->
    <div v-if="searchStore.loading" class="text-center py-8 text-gray-400 text-sm">
      {{ t('common.loading') }}
    </div>

    <!-- Таблица лидов -->
    <div v-else>
      <h3 class="text-base font-semibold text-gray-800 mb-3">
        {{ t('leads.title') }}
        <span class="text-gray-400 font-normal ml-1">({{ searchStore.leads.length }})</span>
      </h3>
      <LeadsTable
        :leads="searchStore.leads"
        @generate-proposal="proposalLeadId = $event"
        @status-updated="onStatusUpdated"
      />
    </div>

    <!-- Modal генерации КП -->
    <ProposalGenerateModal
      v-model:lead-id="proposalLeadId"
    />
  </div>
</template>
