import { useState } from 'react'
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { isAuthenticated, logout } from './services/auth.js'
import LoginPage from './pages/LoginPage.jsx'
import TeamUploadPage from './pages/TeamUploadPage.jsx'
import CertificationUploadPage from './pages/CertificationUploadPage.jsx'
import RequirementsPage from './pages/RequirementsPage.jsx'
import PlanGenerationPage from './pages/PlanGenerationPage.jsx'
import PlansDashboardPage from './pages/PlansDashboardPage.jsx'

const navStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: 0,
  background: '#1a1a2e',
  padding: '0 1.5rem',
}

const linkStyle = ({ isActive }) => ({
  display: 'block',
  padding: '0.9rem 1.2rem',
  color: isActive ? '#fff' : '#aaa',
  textDecoration: 'none',
  borderBottom: isActive ? '3px solid #4da6ff' : '3px solid transparent',
  fontSize: '0.9rem',
  fontWeight: isActive ? 600 : 400,
})

export default function App() {
  const [authed, setAuthed] = useState(isAuthenticated())

  function handleLogin() {
    setAuthed(true)
  }

  function handleLogout() {
    logout()
    setAuthed(false)
  }

  if (!authed) {
    return <LoginPage onLogin={handleLogin} />
  }

  return (
    <BrowserRouter>
      <nav style={navStyle}>
        <span style={{ color: '#fff', padding: '0.9rem 1.2rem 0.9rem 0', fontWeight: 700, fontSize: '0.95rem', marginRight: 'auto' }}>
          Training Manager
        </span>
        <NavLink to="/team" style={linkStyle}>Team</NavLink>
        <NavLink to="/certifications" style={linkStyle}>Certifications</NavLink>
        <NavLink to="/requirements" style={linkStyle}>Requirements</NavLink>
        <NavLink to="/generate" style={linkStyle}>Generate</NavLink>
        <NavLink to="/plans" style={linkStyle}>Plans</NavLink>
        <button
          onClick={handleLogout}
          style={{
            marginLeft: '1rem',
            padding: '0.4rem 0.9rem',
            background: 'transparent',
            color: '#aaa',
            border: '1px solid #444',
            borderRadius: 4,
            cursor: 'pointer',
            fontSize: '0.85rem',
          }}
        >
          Sign out
        </button>
      </nav>

      <Routes>
        <Route path="/" element={<TeamUploadPage />} />
        <Route path="/team" element={<TeamUploadPage />} />
        <Route path="/certifications" element={<CertificationUploadPage />} />
        <Route path="/requirements" element={<RequirementsPage />} />
        <Route path="/generate" element={<PlanGenerationPage />} />
        <Route path="/plans" element={<PlansDashboardPage />} />
      </Routes>
    </BrowserRouter>
  )
}
