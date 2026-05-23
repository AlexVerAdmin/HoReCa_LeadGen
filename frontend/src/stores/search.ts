/**
 * Search store — список поисков, текущий поиск, лиды, polling статуса.
 * Polling каждые 3 сек до статуса completed/failed.
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as searchService from '@/services/searchService'
import * as leadService from '@/services/leadService'
import type { Search, Lead, SearchCreate } from '@/types'

// Статусы, при которых поиск ещё выполняется
const RUNNING_STATUSES = new Set<string>(['pending', 'in_progress'])

export const useSearchStore = defineStore('search', () => {
  // ─── State ───────────────────────────────────────────────────────────────
  const searches = ref<Search[]>([])
  const currentSearch = ref<Search | null>(null)
  const leads = ref<Lead[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Хранилище активных polling-таймеров: searchId → intervalId
  const _pollingTimers = new Map<number, ReturnType<typeof setInterval>>()

  // ─── Actions ─────────────────────────────────────────────────────────────

  /** Загрузить список всех поисков пользователя */
  const loadSearches = async () => {
    loading.value = true
    error.value = null
    try {
      searches.value = await searchService.getSearches()
    } catch {
      error.value = 'Ошибка загрузки поисков'
    } finally {
      loading.value = false
    }
  }

  /** Загрузить конкретный поиск по ID */
  const loadSearch = async (id: number) => {
    currentSearch.value = await searchService.getSearch(id)
  }

  /**
   * Создать новый поиск и добавить в список.
   * Polling запускается автоматически если статус — pending/in_progress.
   */
  const startSearch = async (payload: SearchCreate) => {
    loading.value = true
    try {
      const newSearch = await searchService.createSearch(payload)
      searches.value.unshift(newSearch)
      if (RUNNING_STATUSES.has(newSearch.status)) {
        pollSearchStatus(newSearch.id)
      }
      return newSearch
    } finally {
      loading.value = false
    }
  }

  /**
   * Polling статуса поиска каждые 3 сек.
   * Останавливается при completed/failed, обновляет запись в searches[].
   */
  const pollSearchStatus = (id: number) => {
    // не запускаем дублирующий таймер
    if (_pollingTimers.has(id)) return

    const timer = setInterval(async () => {
      try {
        const updated = await searchService.getSearch(id)
        // Обновляем currentSearch если он совпадает
        if (currentSearch.value?.id === id) {
          currentSearch.value = updated
        }
        // Обновляем запись в общем списке
        const idx = searches.value.findIndex(s => s.id === id)
        if (idx !== -1) searches.value[idx] = updated

        if (!RUNNING_STATUSES.has(updated.status)) {
          clearInterval(timer)
          _pollingTimers.delete(id)
        }
      } catch {
        clearInterval(timer)
        _pollingTimers.delete(id)
      }
    }, 3000)

    _pollingTimers.set(id, timer)
  }

  /** Удалить поиск */
  const removeSearch = async (id: number) => {
    await searchService.deleteSearch(id)
    searches.value = searches.value.filter(s => s.id !== id)
  }

  /** Загрузить лиды для поиска */
  const loadLeads = async (searchId: number) => {
    loading.value = true
    try {
      leads.value = await leadService.getLeads(searchId)
    } finally {
      loading.value = false
    }
  }

  return {
    searches,
    currentSearch,
    leads,
    loading,
    error,
    loadSearches,
    loadSearch,
    startSearch,
    pollSearchStatus,
    removeSearch,
    loadLeads,
  }
})
