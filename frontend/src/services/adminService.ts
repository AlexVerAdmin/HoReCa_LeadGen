/**
 * Сервис административных функций.
 * Доступен только пользователям с ролью 'admin'.
 * GET/POST/PUT/DELETE /api/admin/users/, GET /api/admin/searches/, GET/PUT /api/admin/settings/
 */
import api from './api'
import type { UserAdmin, UserAdminCreate, UserAdminUpdate, Search, GlobalSettings } from '@/types'

// ─── Пользователи ───────────────────────────────────────────────────────────

/** Получить список всех пользователей */
export const getUsers = async (): Promise<UserAdmin[]> => {
  const { data } = await api.get<UserAdmin[]>('/admin/users/')
  return data
}

/** Создать нового пользователя */
export const createUser = async (payload: UserAdminCreate): Promise<UserAdmin> => {
  const { data } = await api.post<UserAdmin>('/admin/users/', payload)
  return data
}

/** Обновить данные пользователя */
export const updateUser = async (id: number, payload: UserAdminUpdate): Promise<UserAdmin> => {
  const { data } = await api.put<UserAdmin>(`/admin/users/${id}`, payload)
  return data
}

/** Удалить пользователя */
export const deleteUser = async (id: number): Promise<void> => {
  await api.delete(`/admin/users/${id}`)
}

// ─── Поиски ─────────────────────────────────────────────────────────────────

/** Получить все поиски (все пользователи) */
export const getSearches = async (): Promise<Search[]> => {
  const { data } = await api.get<Search[]>('/admin/searches/')
  return data
}

// ─── Глобальные настройки ───────────────────────────────────────────────────

/** Получить список глобальных настроек */
export const getSettings = async (): Promise<GlobalSettings[]> => {
  const { data } = await api.get<GlobalSettings[]>('/admin/settings/')
  return data
}

/** Обновить значение глобальной настройки по ключу */
export const updateSetting = async (key: string, value: string): Promise<GlobalSettings> => {
  const { data } = await api.put<GlobalSettings>(`/admin/settings/${key}`, { value })
  return data
}
