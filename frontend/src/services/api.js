import { getToken } from './auth.js'

const BASE_URL = import.meta.env.VITE_API_URL || ''

async function request(method, path, body = null, isFormData = false) {
  const token = getToken()
  const headers = { Authorization: `Bearer ${token}` }
  if (!isFormData) headers['Content-Type'] = 'application/json'

  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: isFormData ? body : body ? JSON.stringify(body) : null,
  })

  if (response.status === 204) return null

  const contentType = response.headers.get('Content-Type') || ''
  if (contentType.includes('text/csv')) {
    const blob = await response.blob()
    return blob
  }

  const data = await response.json()
  if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`)
  return data
}

// Team members
export const importTeamMembers = (file) => {
  const form = new FormData()
  form.append('file', file)
  return request('POST', '/team-members/import', form, true)
}
export const listTeamMembers = (params = {}) =>
  request('GET', `/team-members?${new URLSearchParams(params)}`)

// Certifications
export const importCertifications = (file) => {
  const form = new FormData()
  form.append('file', file)
  return request('POST', '/certifications/import', form, true)
}
export const listCertifications = (params = {}) =>
  request('GET', `/certifications?${new URLSearchParams(params)}`)

// Requirements
export const saveRequirements = (rules) => request('POST', '/requirements', { rules })
export const getRequirements = () => request('GET', '/requirements')

// Plans
export const generatePlans = () => request('POST', '/plans/generate', {})
export const listPlans = (params = {}) =>
  request('GET', `/plans?${new URLSearchParams(params)}`)
export const getPlan = (personId) => request('GET', `/plans/${personId}`)
export const exportPlans = () => request('GET', '/plans/export')

// Meta
export const getPlansStatus = () => request('GET', '/meta/plans-status')
