import api from './api'

// Fetch complaint categories
export const getCategories = async () => {
  const response = await api.get('/categories')
  return response.data
}