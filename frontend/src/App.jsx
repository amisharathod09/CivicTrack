
import { BrowserRouter, Routes, Route } from 'react-router-dom'

import Home from './pages/Home'
import AdminDashboard from './pages/AdminDashboard'
import Login from './pages/Login'
import { ThemeProvider } from './context/ThemeContext'

import './App.css'

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/admin" element={<AdminDashboard />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App
