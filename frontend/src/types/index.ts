// ─── Роли и статусы (строго по enum-значениям бэкенда) ─────────────────────

/** Роль пользователя — значения lowercase, как в UserRole бэкенда */
export type UserRole = 'admin' | 'manager' | 'agent'

/** Статус лида в воронке */
export type LeadStatus = 'New' | 'Qualified' | 'Contacted' | 'Rejected'

/** Статус выполнения поиска — lowercase + underscore, как в SearchStatus бэкенда */
export type SearchStatus = 'pending' | 'in_progress' | 'completed' | 'failed'

/** Статус коммерческого предложения — lowercase, как в ProposalStatus бэкенда */
export type ProposalStatus = 'draft' | 'generated' | 'sent' | 'accepted' | 'rejected'

// ─── Пользователь ──────────────────────────────────────────────────────────

/** Данные пользователя (UserResponse) */
export interface User {
  id: number
  email: string
  username: string
  role: UserRole
  is_active: boolean
}

/** Расширенный пользователь для администратора (UserAdminResponse) */
export interface UserAdmin extends User {
  created_at: string
  updated_at: string
}

/** Настройки пользователя (UserSettingsResponse) */
export interface UserSettings {
  ui_language: string        // 'en' | 'de' | 'ru'
  proposal_language: string  // 'en' | 'de' | 'ru'
  default_radius: number     // метры
  default_place_types: string[]
}

/** Payload для обновления настроек (UserSettingsUpdate) */
export interface UserSettingsUpdate {
  ui_language?: string
  proposal_language?: string
  default_radius?: number
  default_place_types?: string[]
}

/** Payload для создания пользователя администратором (UserAdminCreate) */
export interface UserAdminCreate {
  email: string
  username: string
  password: string
  role: UserRole
  is_active?: boolean
}

/** Payload для обновления пользователя администратором (UserAdminUpdate) */
export interface UserAdminUpdate {
  email?: string
  username?: string
  password?: string
  role?: UserRole
  is_active?: boolean
}

// ─── JWT токены ─────────────────────────────────────────────────────────────

/** Пара токенов доступа и обновления (Token) */
export interface Token {
  access_token: string
  refresh_token: string
  token_type: string
}

// ─── Поиск ──────────────────────────────────────────────────────────────────

/** Ответ со списком поисков (SearchResponse) */
export interface Search {
  id: number
  status: SearchStatus
  total_found: number
  qualified_count: number
  lat: number
  lon: number
  radius: number
  place_types: string[]
  query_string: string | null
  created_at: string
}

/** Payload для создания поиска (SearchCreate) — бэкенд ожидает latitude/longitude */
export interface SearchCreate {
  latitude: number
  longitude: number
  radius: number
  place_types: string[]
  query_string?: string | null
}

// ─── Лид ────────────────────────────────────────────────────────────────────

/** Данные лида (LeadResponse) */
export interface Lead {
  id: number
  google_place_id: string
  name: string
  address: string | null
  phone: string | null
  website: string | null
  rating: number | null
  review_count: number | null
  last_negative_review_text: string | null
  pain_points: string[] | null
  status: LeadStatus
  created_at: string
  updated_at: string
}

// ─── Коммерческое предложение ────────────────────────────────────────────────

/** Данные КП (ProposalResponse) */
export interface Proposal {
  id: number
  lead_id: number
  language: string
  content_text: string
  recommendations: string[] | null
  pdf_url: string | null
  status: ProposalStatus
  generated_at: string | null
}

/** Payload для создания КП (ProposalCreate) */
export interface ProposalCreate {
  lead_id: number
  language: string
}

// ─── Глобальные настройки (AdminSettings) ───────────────────────────────────

/** Запись глобальных настроек системы (GlobalSettingsResponse) */
export interface GlobalSettings {
  id: number
  key: string
  value: string
  description: string | null
  created_at: string
  updated_at: string
}
