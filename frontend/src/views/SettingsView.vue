<script setup lang="ts">
/**
 * SettingsView — настройки профиля пользователя.
 * Управляет username, языком интерфейса, языком КП, радиусом и типами заведений по умолчанию.
 * Смена ui_language применяется к i18n немедленно.
 */
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useUiStore } from '@/stores/ui'
import * as userService from '@/services/userService'
import type { UserSettingsUpdate } from '@/types'

const { t, locale } = useI18n()
const uiStore = useUiStore()

const LANGS       = ['ru', 'en', 'de'] as const
const PLACE_TYPES = [
  { value: 'restaurant', label: 'Restaurant' },
  { value: 'cafe',       label: 'Café' },
  { value: 'bar',        label: 'Bar' },
  { value: 'bakery',     label: 'Bäckerei / Bakery' },
  { value: 'night_club', label: 'Night Club' },
  { value: 'hotel',      label: 'Hotel' },
]

// ─── State ────────────────────────────────────────────────────────────────
const username         = ref('')
const uiLanguage       = ref('ru')
const proposalLanguage = ref('ru')
const defaultRadiusKm  = ref(1)
const defaultTypes     = ref<string[]>(['restaurant', 'cafe'])

const loading  = ref(true)
const saving   = ref(false)
const saved    = ref(false)
const error    = ref<string | null>(null)

// ─── Загрузка ─────────────────────────────────────────────────────────────
onMounted(async () => {
  try {
    const [user, settings] = await Promise.all([
      userService.getMe(),
      userService.getSettings(),
    ])
    username.value         = user.username
    uiLanguage.value       = settings.ui_language
    proposalLanguage.value = settings.proposal_language
    defaultRadiusKm.value  = settings.default_radius / 1000
    defaultTypes.value     = [...settings.default_place_types]
  } catch {
    error.value = t('common.error')
  } finally {
    loading.value = false
  }
})

// ─── Смена языка интерфейса — применяется немедленно ─────────────────────
const onUiLangChange = (lang: string) => {
  uiLanguage.value = lang
  locale.value     = lang   // реактивное обновление vue-i18n
  uiStore.setLocale(lang)
}

// ─── Сохранение ───────────────────────────────────────────────────────────
const save = async () => {
  saving.value = true
  error.value  = null
  saved.value  = false
  try {
    // Обновить username через PUT /users/me
    await userService.updateMe(username.value)

    // Обновить настройки через PUT /users/me/settings
    const payload: UserSettingsUpdate = {
      ui_language:       uiLanguage.value,
      proposal_language: proposalLanguage.value,
      default_radius:    Math.round(defaultRadiusKm.value * 1000),
      default_place_types: defaultTypes.value,
    }
    await userService.updateSettings(payload)
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch {
    error.value = t('common.error')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="max-w-xl">
    <h2 class="text-xl font-semibold text-gray-800 mb-6">{{ t('settings.title') }}</h2>

    <!-- Загрузка -->
    <div v-if="loading" class="text-center py-12 text-gray-400 text-sm">
      {{ t('common.loading') }}
    </div>

    <form v-else class="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100" @submit.prevent="save">

      <!-- Username -->
      <div class="px-5 py-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">
          {{ t('settings.username') }}
        </label>
        <input
          v-model="username"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
      </div>

      <!-- Язык интерфейса -->
      <div class="px-5 py-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          {{ t('settings.uiLang') }}
        </label>
        <div class="flex gap-2">
          <button
            v-for="lang in LANGS"
            :key="lang"
            type="button"
            class="px-4 py-2 text-sm font-medium rounded-lg border transition-colors uppercase"
            :class="uiLanguage === lang
              ? 'bg-indigo-600 text-white border-indigo-600'
              : 'text-gray-600 border-gray-300 hover:bg-gray-50'"
            @click="onUiLangChange(lang)"
          >
            {{ lang }}
          </button>
        </div>
      </div>

      <!-- Язык КП -->
      <div class="px-5 py-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          {{ t('settings.kpLang') }}
        </label>
        <div class="flex gap-2">
          <button
            v-for="lang in LANGS"
            :key="lang"
            type="button"
            class="px-4 py-2 text-sm font-medium rounded-lg border transition-colors uppercase"
            :class="proposalLanguage === lang
              ? 'bg-indigo-600 text-white border-indigo-600'
              : 'text-gray-600 border-gray-300 hover:bg-gray-50'"
            @click="proposalLanguage = lang"
          >
            {{ lang }}
          </button>
        </div>
      </div>

      <!-- Радиус по умолчанию -->
      <div class="px-5 py-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">
          {{ t('settings.defaultRadius') }}
        </label>
        <div class="flex items-center gap-2">
          <input
            v-model.number="defaultRadiusKm"
            type="number"
            min="0.1"
            max="50"
            step="0.1"
            class="w-32 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
          <span class="text-sm text-gray-500">км</span>
        </div>
      </div>

      <!-- Типы заведений по умолчанию -->
      <div class="px-5 py-4">
        <p class="text-sm font-medium text-gray-700 mb-2">{{ t('settings.defaultTypes') }}</p>
        <div class="grid grid-cols-2 gap-y-2">
          <label
            v-for="pt in PLACE_TYPES"
            :key="pt.value"
            class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer"
          >
            <input
              v-model="defaultTypes"
              type="checkbox"
              :value="pt.value"
              class="accent-indigo-600"
            />
            {{ pt.label }}
          </label>
        </div>
      </div>

      <!-- Footer: сообщения + кнопка -->
      <div class="px-5 py-4 flex items-center justify-between">
        <div>
          <p v-if="saved" class="text-sm text-green-600">✓ {{ t('settings.saved') }}</p>
          <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
        </div>
        <button
          type="submit"
          :disabled="saving"
          class="flex items-center gap-2 px-5 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          <svg v-if="saving" class="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
          </svg>
          {{ t('settings.save') }}
        </button>
      </div>
    </form>
  </div>
</template>
