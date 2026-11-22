import api from './api'

// Fetch all complaints with optional filters
export const getAllComplaints = async (filters = {}) => {
  const response = await api.get('/service-requests', {
    params: filters
  })

  return response.data
}

// Fetch all active staff members
export const getActiveStaff = async () => {
  const response = await api.get('/auth/staff')
  return response.data
}

// Assign a complaint to a staff member
export const assignComplaint = async (assignmentData) => {
  const response = await api.post('/assignments', assignmentData)
  return response.data
}

export const getComplaintDetails = async (requestId) => {
  const response = await api.get(`/service-requests/${requestId}`)
  return response.data
}

export const getAllAssignments = async () => {
  const response = await api.get('/assignments')
  return response.data
}

export const createStaff = async (staffData) => {
  const response = await api.post('/auth/staff', staffData)
  return response.data
}

export const updateStaff = async (userId, staffData) => {
  const response = await api.put(`/auth/staff/${userId}`, staffData)
  return response.data
}
export const getDepartments = async () => {
  const response = await api.get('/departments')
  return response.data
}

// Get all staff members (active and inactive) for management
export const getAllStaff = async () => {
  const response = await api.get('/auth/staff/manage')
  return response.data
}

// Activate or deactivate a staff member
export const updateStaffStatus = async (userId, isActive) => {
  const response = await api.patch(`/auth/staff/${userId}/status`, {
    is_active: isActive
  })
  return response.data
}
// Fetch all complaint attachments (Admin only)
export const getAllAttachments = async () => {
  const response = await api.get('/attachments')
  return response.data
}