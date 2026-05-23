/**
 * Сервис поисков.
 * POST/GET/DELETE /api/searches/
 */
import api from './api'
import type { Search, SearchCreate } from '@/types'

/** Создать новый поиск (запускается фоном на бэкенде) */
export const createSearch = async (payload: SearchCreate): Promise<Search> => {
  const { data } = await api.post<Search>('/searches/', payload)
  return data
}

/** Получить список поисков текущего пользователя */
export const getSearches = async (): Promise<Search[]> => {
  const { data } = await api.get<Search[]>('/searches/')
  return data
}

/** Получить конкретный поиск по ID */
export const getSearch = async (id: number): Promise<Search> => {
  const { data } = await api.get<Search>(`/searches/${id}`)
  return data
}

/** Удалить поиск по ID */
export const deleteSearch = async (id: number): Promise<void> => {
  await api.delete(`/searches/${id}`)
}
