/**
 * Auth store — токены, текущий пользователь, RBAC.
 * Хранит токены в localStorage, профиль в памяти.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authService from '@/services/authService'
import * as userService from '@/services/userService'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  // ─── State ───────────────────────────────────────────────────────────────
  const user = ref<User | null>(null)

  // ─── Getters ─────────────────────────────────────────────────────────────
  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  // ─── Actions ─────────────────────────────────────────────────────────────

  /** Загрузить профиль текущего пользователя с бэкенда */
  const fetchMe = async () => {
    user.value = await userService.getMe()
  }

  /**
   * Войти в систему: сохранить токены, загрузить профиль.
   * Бросает ошибку при неверных credentials (перехватывается в LoginView).
   */
  const login = async (email: string, password: string) => {
    const tokens = await authService.login(email, password)
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
    await fetchMe()
  }

  /** Выйти: очистить хранилище и обнулить state */
  const logout = () => {
    localStorage.clear()
    user.value = null
  }

  /**
   * Инициализация при старте приложения.
   * Если в localStorage есть токен — пробуем восстановить сессию.
   */
  const init = async () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        await fetchMe()
      } catch {
        // токен просрочен и refresh не помог — очищаем
        localStorage.clear()
        user.value = null
      }
    }
  }

  return { user, isAuthenticated, isAdmin, login, logout, fetchMe, init }
})
