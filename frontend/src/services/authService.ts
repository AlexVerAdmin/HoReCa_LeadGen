/**
 * Сервис аутентификации: логин и обновление токена.
 * POST /api/auth/login, POST /api/auth/refresh
 */
import axios from 'axios'
import type { Token } from '@/types'

/** Вход в систему — возвращает пару JWT токенов */
export const login = async (email: string, password: string): Promise<Token> => {
  const { data } = await axios.post<Token>('/api/auth/login', { email, password })
  return data
}

/** Обновление access_token по refresh_token */
export const refresh = async (refresh_token: string): Promise<Token> => {
  const { data } = await axios.post<Token>('/api/auth/refresh', { refresh_token })
  return data
}
