/**
 * Axios instance с JWT-интерцепторами.
 * Базовый URL '/api' проксируется через Vite на localhost:8000.
 */
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

// Request: подставляем access_token в заголовок Authorization
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Response: при 401 пробуем refresh, повторяем исходный запрос
// Флаг _retry предотвращает бесконечный цикл повторных refresh
api.interceptors.response.use(
  res => res,
  async error => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        const refresh = localStorage.getItem('refresh_token')
        const { data } = await axios.post('/api/auth/refresh', { refresh_token: refresh })
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        original.headers.Authorization = `Bearer ${data.access_token}`
        return api(original)
      } catch {
        // refresh провалился — очищаем хранилище и редиректим на логин
        localStorage.clear()
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
