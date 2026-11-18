
import { useState } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { saveAccessToken, clearAccessToken } from '../services/api'
import api from '../services/api'
import ThemeToggle from '../components/ThemeToggle'
import './Login.css'

function Login() {
  const navigate = useNavigate()
  const location = useLocation()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const successMessage = location.state?.message

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
      const role = userResponse.data.role

      if (role === 'admin') {
        navigate('/admin', { replace: true })
      } else if (role === 'staff') {
        navigate('/staff', { replace: true })
      } else if (role === 'citizen') {
        navigate('/citizen', { replace: true })
      } else {
        clearAccessToken()
        setError('Your account has an unrecognized role. Please contact support.')
      }
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

        <span className="login-tag">SECURE LOGIN</span>

        <h1>Welcome Back</h1>

        <p className="login-description">
          Sign in to access your CivicTrack account and services.
        </p>

        {successMessage && (
          <p className="login-success">{successMessage}</p>
        )}

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
          Don't have an account? <Link to="/register">Create Account</Link>
        </p>
      </div>
    </div>
  )
}

export default Login
