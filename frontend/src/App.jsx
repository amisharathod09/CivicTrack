
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'

import Home from './pages/Home'
import AdminDashboard from './pages/AdminDashboard'
import Login from './pages/Login'
import Register from './pages/Register'

import { ThemeProvider } from './context/ThemeContext'
import api, { clearAccessToken } from './services/api'
import CitizenDashboard from './pages/CitizenDashboard'
import StaffDashboard from './pages/StaffDashboard'
import './App.css'

// Protect routes according to user role
function ProtectedRoute({ children, allowedRoles }) {
  const [userRole, setUserRole] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const verifyUser = async () => {
      const token = localStorage.getItem('civictrack_access_token')

      if (!token) {
        setUserRole(false)
        setIsLoading(false)
        return
      }

      try {
        const response = await api.get('/auth/me')
        setUserRole(response.data.role)
      } catch (error) {
        clearAccessToken()
        setUserRole(false)
      } finally {
        setIsLoading(false)
      }
    }

    verifyUser()
  }, [])

  if (isLoading) {
    return <div>Verifying authentication...</div>
  }

  if (!userRole) {
    return <Navigate to="/login" replace />
  }

  if (!allowedRoles.includes(userRole)) {
    if (userRole === 'admin') {
      return <Navigate to="/admin" replace />
    }

    if (userRole === 'staff') {
      return <Navigate to="/staff" replace />
    }

    if (userRole === 'citizen') {
      return <Navigate to="/citizen" replace />
    }

    return <Navigate to="/login" replace />
  }

  return children
}

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />

          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />

          <Route
            path="/staff"
            element={
              <ProtectedRoute allowedRoles={['staff']}>
                <StaffDashboard />
              </ProtectedRoute>
            }
          />

          <Route
            path="/citizen"
            element={
              <ProtectedRoute allowedRoles={['citizen']}>
                <CitizenDashboard />
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App
