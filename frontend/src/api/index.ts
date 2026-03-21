import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000')

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// Auth API
export const authApi = {
  register: (data: { email: string; username: string; password: string }) =>
    api.post('/api/auth/register', data),
  login: (email: string, password: string) => {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)
    return api.post('/api/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },
  me: () => api.get('/api/auth/me'),
}

// Projects API
export const projectsApi = {
  list: () => api.get('/api/projects'),
  create: (data: { name: string; description?: string }) => api.post('/api/projects', data),
  get: (id: number) => api.get(`/api/projects/${id}`),
  update: (id: number, data: { name?: string; description?: string }) =>
    api.put(`/api/projects/${id}`, data),
  delete: (id: number) => api.delete(`/api/projects/${id}`),
}

// Chapters API
export const chaptersApi = {
  list: (projectId: number) => api.get(`/api/projects/${projectId}/chapters`),
  create: (projectId: number, data: { title: string; content?: string; order?: number }) =>
    api.post(`/api/projects/${projectId}/chapters`, data),
  get: (chapterId: number) => api.get(`/api/chapters/${chapterId}`),
  update: (chapterId: number, data: any) => api.put(`/api/chapters/${chapterId}`, data),
  delete: (chapterId: number) => api.delete(`/api/chapters/${chapterId}`),
}

// Skills API
export const skillsApi = {
  list: () => api.get('/api/skills'),
  create: (data: { name: string; description?: string; config?: any; code: string }) =>
    api.post('/api/skills', data),
  get: (id: number) => api.get(`/api/skills/${id}`),
  update: (id: number, data: any) => api.put(`/api/skills/${id}`, data),
  delete: (id: number) => api.delete(`/api/skills/${id}`),
  execute: (id: number, parameters?: any, chapterId?: number) =>
    api.post(`/api/skills/${id}/execute`, { parameters, chapter_id: chapterId }),
}
