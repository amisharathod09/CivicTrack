
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Home from './pages/Home'
import AdminDashboard from './pages/AdminDashboard'
import Login from './pages/Login'
import { ThemeProvider } from './context/ThemeContext'
import { useState, useEffect } from 'react'
import api, { clearAccessToken } from './services/api'
import './App.css'

// Protect admin dashboard
function ProtectedRoute({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(null)

  useEffect(() => {
    const verifyAdmin = async () => {
      const token = localStorage.getItem('civictrack_access_token')

      if (!token) {
        setIsAuthenticated(false)
        return
      }

      try {
        const response = await api.get('/auth/me')

        if (response.data.role === 'admin') {
          setIsAuthenticated(true)
        } else {
          clearAccessToken()
          setIsAuthenticated(false)
        }
      } catch (error) {
        clearAccessToken()
        setIsAuthenticated(false)
      }
    }

    verifyAdmin()
  }, [])

  if (isAuthenticated === null) {
    return <div>Verifying authentication...</div>
  }

  return isAuthenticated
    ? children
    : <Navigate to="/login" replace />
}

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />

          <Route path="/login" element={<Login />} />

          <Route
            path="/admin"
            element={
              <ProtectedRoute>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App
