<script setup lang="ts">
/**
 * SearchForm — форма параметров нового поиска.
 * Радиус (км), типы заведений, опциональная строка поиска.
 * Предзаполняется из настроек пользователя.
 */
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { UserSettings, SearchCreate } from '@/types'

interface Coords { lat: number; lng: number }

const props = defineProps<{
  coords: Coords | null
  defaultSettings: UserSettings | null
}>()

const emit = defineEmits<{
  (e: 'submit', payload: SearchCreate): void
}>()

const { t } = useI18n()

// ─── Доступные типы заведений ─────────────────────────────────────────────
const PLACE_TYPES = [
  { value: 'restaurant', label: 'Restaurant' },
  { value: 'cafe',       label: 'Café' },
  { value: 'bar',        label: 'Bar' },
  { value: 'bakery',     label: 'Bäckerei / Bakery' },
  { value: 'night_club', label: 'Night Club' },
  { value: 'hotel',      label: 'Hotel' },
]

// ─── State ────────────────────────────────────────────────────────────────
const radiusKm   = ref(1)
const placeTypes = ref<string[]>(['restaurant', 'cafe'])
const queryStr   = ref('')

// Предзаполнить из настроек пользователя при появлении
watch(() => props.defaultSettings, (s) => {
  if (!s) return
  radiusKm.value   = s.default_radius / 1000
  placeTypes.value = [...s.default_place_types]
}, { immediate: true })

// ─── Submit ───────────────────────────────────────────────────────────────
const onSubmit = () => {
  if (!props.coords) return

  const payload: SearchCreate = {
    latitude:     props.coords.lat,
    longitude:    props.coords.lng,
    radius:       Math.round(radiusKm.value * 1000),
    place_types:  placeTypes.value,
    query_string: queryStr.value.trim() || null,
  }
  emit('submit', payload)
}
</script>

<template>
  <form class="flex flex-col gap-5" @submit.prevent="onSubmit">
    <!-- Радиус -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        {{ t('search.radius') }}
      </label>
      <input
        v-model.number="radiusKm"
        type="number"
        min="0.1"
        max="50"
        step="0.1"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
      />
    </div>

    <!-- Типы заведений -->
    <div>
      <p class="text-sm font-medium text-gray-700 mb-2">{{ t('search.types') }}</p>
      <div class="grid grid-cols-2 gap-y-2">
        <label
          v-for="pt in PLACE_TYPES"
          :key="pt.value"
          class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer"
        >
          <input
            v-model="placeTypes"
            type="checkbox"
            :value="pt.value"
            class="accent-indigo-600"
          />
          {{ pt.label }}
        </label>
      </div>
    </div>

    <!-- Поиск по названию (опционально) -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">
        {{ t('search.byName') }}
        <span class="text-gray-400 font-normal ml-1">({{ t('common.cancel').toLowerCase().startsWith('о') ? 'необязательно' : 'optional' }})</span>
      </label>
      <input
        v-model="queryStr"
        type="text"
        :placeholder="t('search.byName') + '...'"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
      />
    </div>

    <!-- Уведомление если координаты не выбраны -->
    <p v-if="!coords" class="text-sm text-amber-600">
      Выберите точку на карте
    </p>

    <!-- Кнопка запуска -->
    <button
      type="submit"
      :disabled="!coords || placeTypes.length === 0"
      class="px-4 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
    >
      {{ t('search.start') }}
    </button>
  </form>
</template>
