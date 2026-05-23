/**
 * Сервис лидов.
 * GET /api/leads/, GET/PATCH /api/leads/{id}
 */
import api from './api'
import type { Lead, LeadStatus } from '@/types'

/** Получить список лидов (опционально фильтр по search_id) */
export const getLeads = async (searchId?: number): Promise<Lead[]> => {
  const params = searchId !== undefined ? { search_id: searchId } : {}
  const { data } = await api.get<Lead[]>('/leads/', { params })
  return data
}

/** Получить лид по ID */
export const getLead = async (id: number): Promise<Lead> => {
  const { data } = await api.get<Lead>(`/leads/${id}`)
  return data
}

/** Обновить статус лида */
export const updateStatus = async (id: number, status: LeadStatus): Promise<Lead> => {
  const { data } = await api.patch<Lead>(`/leads/${id}/status`, { status })
  return data
}
