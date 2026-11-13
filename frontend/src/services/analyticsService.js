
import api from './api'

// Fetch complaint overview
export const getComplaintOverview = async () => {
  const response = await api.get('/analytics/overview')
  return response.data
}

// Fetch monthly complaint trends
export const getComplaintTrends = async () => {
  const response = await api.get('/analytics/trends')
  return response.data
}

// Fetch category analytics
export const getCategoryAnalytics = async () => {
  const response = await api.get('/analytics/categories')
  return response.data
}

// Fetch department analytics
export const getDepartmentAnalytics = async () => {
  const response = await api.get('/analytics/departments')
  return response.data
}

// Fetch staff workload
export const getStaffWorkload = async () => {
  const response = await api.get('/analytics/staff-workload')
  return response.data
}

// Fetch SLA performance
export const getSLAPerformance = async () => {
  const response = await api.get('/analytics/sla-performance')
  return response.data
}

// Fetch priority analytics
export const getPriorityAnalytics = async () => {
  const response = await api.get('/analytics/priority')
  return response.data
}

// Fetch resolution time
export const getResolutionTime = async () => {
  const response = await api.get('/analytics/resolution-time')
  return response.data
}

// Fetch citizen feedback
export const getFeedbackAnalytics = async () => {
  const response = await api.get('/analytics/feedback')
  return response.data
}
