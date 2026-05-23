<script setup lang="ts">
/**
 * LanguageSwitcher — кнопки переключения языка интерфейса (RU / EN / DE).
 * Меняет locale в ui store и применяет к глобальному vue-i18n.
 */
import { useI18n } from 'vue-i18n'
import { useUiStore } from '@/stores/ui'

const { locale } = useI18n()
const uiStore = useUiStore()

const langs = ['ru', 'en', 'de'] as const

const switchLang = (lang: string) => {
  locale.value = lang         // применяем к vue-i18n сразу
  uiStore.setLocale(lang)     // сохраняем в store + localStorage
}
</script>

<template>
  <div class="flex items-center gap-1">
    <button
      v-for="lang in langs"
      :key="lang"
      class="px-2 py-1 text-xs font-medium rounded transition-colors uppercase"
      :class="locale === lang
        ? 'bg-indigo-600 text-white'
        : 'text-gray-500 hover:bg-gray-100'"
      @click="switchLang(lang)"
    >
      {{ lang }}
    </button>
  </div>
</template>
