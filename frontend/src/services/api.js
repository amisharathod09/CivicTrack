
import axios from 'axios'

// CivicTrack backend connection
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Save JWT access token after login
export const saveAccessToken = (token) => {
  localStorage.setItem('civictrack_access_token', token)
}

// Remove JWT access token during logout
export const clearAccessToken = () => {
  localStorage.removeItem('civictrack_access_token')
}

// Automatically attach JWT token to API requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('civictrack_access_token')

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => Promise.reject(error)
)

export default api
