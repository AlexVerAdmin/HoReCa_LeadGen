/**
 * Vue Router — все маршруты приложения + auth/RBAC guards.
 * meta.public = true  → доступен без авторизации
 * meta.roles = [...]  → доступен только указанным ролям
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Lazy-импорты views (code splitting)
const LoginView          = () => import('@/views/LoginView.vue')
const DashboardView      = () => import('@/views/DashboardView.vue')
const NewSearchView      = () => import('@/views/NewSearchView.vue')
const SearchResultsView  = () => import('@/views/SearchResultsView.vue')
const LeadDetailView     = () => import('@/views/LeadDetailView.vue')
const SettingsView       = () => import('@/views/SettingsView.vue')
const AdminUsersView     = () => import('@/views/admin/AdminUsersView.vue')
const AdminSettingsView  = () => import('@/views/admin/AdminSettingsView.vue')

// Расширяем типы meta для поддержки custom-полей
declare module 'vue-router' {
  interface RouteMeta {
    public?: boolean
    roles?: string[]
    title?: string
  }
}

const routes = [
  {
    path: '/login',
    component: LoginView,
    meta: { public: true, title: '' },
  },
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    component: DashboardView,
    meta: { title: 'nav.dashboard' },
  },
  {
    path: '/search/new',
    component: NewSearchView,
    meta: { title: 'nav.newSearch' },
  },
  {
    path: '/search/:id',
    component: SearchResultsView,
    meta: { title: 'search.history' },
  },
  {
    path: '/leads/:id',
    component: LeadDetailView,
    meta: { title: 'leads.title' },
  },
  {
    path: '/settings',
    component: SettingsView,
    meta: { title: 'settings.title' },
  },
  {
    path: '/admin/users',
    component: AdminUsersView,
    meta: { title: 'admin.users', roles: ['admin'] },
  },
  {
    path: '/admin/settings',
    component: AdminSettingsView,
    meta: { title: 'nav.admin', roles: ['admin'] },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// ─── Navigation Guard ─────────────────────────────────────────────────────

router.beforeEach(to => {
  const auth = useAuthStore()

  // Незалогиненный пользователь → только публичные маршруты
  if (!auth.isAuthenticated && !to.meta.public) {
    return '/login'
  }

  // Ограничение по ролям (RBAC)
  if (to.meta.roles && auth.user && !to.meta.roles.includes(auth.user.role)) {
    return '/dashboard'
  }
})

export default router
