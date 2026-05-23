/**
 * UI store — язык интерфейса, управление sidebar.
 * Язык сохраняется в localStorage и применяется к vue-i18n.
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

export const useUiStore = defineStore('ui', () => {
  // ─── State ───────────────────────────────────────────────────────────────
  const locale = ref<string>(localStorage.getItem('locale') ?? 'ru')
  const sidebarOpen = ref(true)

  // ─── Actions ─────────────────────────────────────────────────────────────

  /**
   * Сменить язык интерфейса.
   * Обновляет vue-i18n locale реактивно и сохраняет в localStorage.
   */
  const setLocale = (lang: string) => {
    locale.value = lang
    localStorage.setItem('locale', lang)
    // Применяем к глобальному i18n (используем useI18n внутри действия)
    try {
      const { locale: i18nLocale } = useI18n()
      i18nLocale.value = lang
    } catch {
      // вне компонента — обновим через глобальный инстанс (см. LanguageSwitcher)
    }
  }

  const toggleSidebar = () => {
    sidebarOpen.value = !sidebarOpen.value
  }

  return { locale, sidebarOpen, setLocale, toggleSidebar }
})
