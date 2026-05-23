import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import 'leaflet/dist/leaflet.css'
import './assets/main.css'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'

import en from './locales/en.json'
import de from './locales/de.json'
import ru from './locales/ru.json'

// Инициализация i18n — locale берётся из localStorage или дефолт ru
const i18n = createI18n({
  legacy: false,           // Composition API режим (locale.value вместо $i18n.locale)
  locale: localStorage.getItem('locale') ?? 'ru',
  fallbackLocale: 'en',
  messages: { en, de, ru },
})

;(async () => {
  const app = createApp(App)
  app.use(createPinia())
  app.use(router)
  app.use(i18n)

  // Восстанавливаем сессию по токену из localStorage ДО монтирования,
  // чтобы router guard видел корректный isAuthenticated при первом рендере
  const authStore = useAuthStore()
  await authStore.init()

  app.mount('#app')
})()
