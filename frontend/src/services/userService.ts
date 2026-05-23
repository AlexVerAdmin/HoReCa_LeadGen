/**
 * Сервис профиля и настроек текущего пользователя.
 * GET/PUT /api/users/me, GET/PUT /api/users/me/settings
 */
import api from './api'
import type { User, UserSettings, UserSettingsUpdate } from '@/types'

/** Получить профиль текущего пользователя */
export const getMe = async (): Promise<User> => {
  const { data } = await api.get<User>('/users/me')
  return data
}

/** Обновить username текущего пользователя */
export const updateMe = async (username: string): Promise<User> => {
  const { data } = await api.put<User>('/users/me', null, { params: { username } })
  return data
}

/** Получить настройки пользователя */
export const getSettings = async (): Promise<UserSettings> => {
  const { data } = await api.get<UserSettings>('/users/me/settings')
  return data
}

/** Обновить настройки пользователя */
export const updateSettings = async (payload: UserSettingsUpdate): Promise<UserSettings> => {
  const { data } = await api.put<UserSettings>('/users/me/settings', payload)
  return data
}
