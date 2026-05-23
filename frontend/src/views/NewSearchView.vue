<script setup lang="ts">
/**
 * NewSearchView — страница создания нового поиска.
 * Слева карта (MapPicker), справа форма параметров (SearchForm).
 * После запуска редиректит на дашборд.
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import MapPicker from '@/components/search/MapPicker.vue'
import SearchForm from '@/components/search/SearchForm.vue'
import { useSearchStore } from '@/stores/search'
import * as userService from '@/services/userService'
import type { UserSettings, SearchCreate } from '@/types'

interface Coords { lat: number; lng: number }

const { t } = useI18n()
const router = useRouter()
const searchStore = useSearchStore()

const coords       = ref<Coords | null>(null)
const radiusKm     = ref(1)
const userSettings = ref<UserSettings | null>(null)
const submitting   = ref(false)
const error        = ref<string | null>(null)

onMounted(async () => {
  try {
    userSettings.value = await userService.getSettings()
    if (userSettings.value) {
      radiusKm.value = userSettings.value.default_radius / 1000
    }
  } catch {
    // настройки недоступны — используем дефолты
  }
})

const onSubmit = async (payload: SearchCreate) => {
  submitting.value = true
  error.value = null
  try {
    await searchStore.startSearch(payload)
    router.push('/dashboard')
  } catch {
    error.value = t('common.error')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div>
    <h2 class="text-xl font-semibold text-gray-800 mb-6">{{ t('search.title') }}</h2>

    <p v-if="error" class="mb-4 px-4 py-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
      {{ error }}
    </p>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Карта -->
      <MapPicker
        v-model:coords="coords"
        :radius-km="radiusKm"
      />

      <!-- Форма параметров -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <SearchForm
          :coords="coords"
          :default-settings="userSettings"
          @submit="onSubmit"
        />
        <div v-if="submitting" class="mt-4 text-sm text-indigo-600 text-center">
          {{ t('common.loading') }}
        </div>
      </div>
    </div>
  </div>
</template>
