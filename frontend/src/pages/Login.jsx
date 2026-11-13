
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { saveAccessToken, clearAccessToken } from '../services/api'
import api from '../services/api'
import ThemeToggle from '../components/ThemeToggle'
import './Login.css'

function Login() {
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async (event) => {
    event.preventDefault()
    setError('')
    setLoading(true)

    try {
      clearAccessToken()

      const response = await api.post('/auth/login', {
        email,
        password
      })

      saveAccessToken(response.data.access_token)

      const userResponse = await api.get('/auth/me')

      if (userResponse.data.role !== 'admin') {
        clearAccessToken()
        setError('Access denied. Only administrators can access this dashboard.')
        return
      }

      navigate('/admin')
    } catch (err) {
      clearAccessToken()

      setError(
        err.response?.data?.detail ||
        'Login failed. Please check your email and password.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-theme-toggle">
  <ThemeToggle />
</div>
      <div className="login-card">
        <div className="login-brand">
          <span className="login-brand-icon">C</span>
          <span>CivicTrack</span>
        </div>

        <span className="login-tag">ADMINISTRATION</span>

        <h1>Welcome Back</h1>
        <p className="login-description">
          Sign in to access the CivicTrack administration dashboard.
        </p>

        <form onSubmit={handleLogin}>
          <label htmlFor="email">Email Address</label>
          <input
            id="email"
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />

          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />

          {error && <p className="login-error">{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p className="login-footer">
          Secure access for authorized administrators only.
        </p>
      </div>
    </div>
  )
}

export default Login
