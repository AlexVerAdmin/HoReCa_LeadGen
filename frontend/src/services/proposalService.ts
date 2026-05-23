/**
 * Сервис коммерческих предложений.
 * POST/GET /api/proposals/, GET/PATCH /api/proposals/{id}, GET /api/proposals/{id}/pdf
 */
import api from './api'
import type { Proposal, ProposalCreate, ProposalStatus } from '@/types'

/** Создать КП для лида */
export const createProposal = async (payload: ProposalCreate): Promise<Proposal> => {
  const { data } = await api.post<Proposal>('/proposals/', payload)
  return data
}

/** Получить список КП текущего пользователя */
export const getProposals = async (): Promise<Proposal[]> => {
  const { data } = await api.get<Proposal[]>('/proposals/')
  return data
}

/** Получить КП по ID */
export const getProposal = async (id: number): Promise<Proposal> => {
  const { data } = await api.get<Proposal>(`/proposals/${id}`)
  return data
}

/**
 * Скачать PDF КП.
 * Возвращает Blob — вызывающий код создаёт ObjectURL и триггерит скачивание.
 */
export const downloadPdf = async (id: number): Promise<Blob> => {
  const { data } = await api.get<Blob>(`/proposals/${id}/pdf`, { responseType: 'blob' })
  return data
}

/** Обновить статус КП */
export const updateStatus = async (id: number, status: ProposalStatus): Promise<Proposal> => {
  const { data } = await api.patch<Proposal>(`/proposals/${id}/status`, { status })
  return data
}

/** Получить КП для конкретного лида (фильтрация на клиенте) */
export const getByLead = async (leadId: number): Promise<Proposal[]> => {
  const all = await getProposals()
  return all.filter(p => p.lead_id === leadId)
}
