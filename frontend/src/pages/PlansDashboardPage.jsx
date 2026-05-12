import { useState, useEffect, useCallback } from 'react'
import PlanFilter from '../components/PlanFilter.jsx'
import TeamPlansList from '../components/TeamPlansList.jsx'
import MemberPlanDetail from '../components/MemberPlanDetail.jsx'
import ExportButton from '../components/ExportButton.jsx'
import StalePlansBanner from '../components/StalePlansBanner.jsx'
import { listPlans, getPlan } from '../services/api.js'

export default function PlansDashboardPage() {
  const [plans, setPlans] = useState([])
  const [filters, setFilters] = useState({})
  const [nameSearch, setNameSearch] = useState('')
  const [selectedPersonId, setSelectedPersonId] = useState(null)
  const [selectedPlan, setSelectedPlan] = useState(null)
  const [loading, setLoading] = useState(false)
  const [detailLoading, setDetailLoading] = useState(false)
  const [apiError, setApiError] = useState(null)

  const loadPlans = useCallback(async (activeFilters) => {
    setLoading(true)
    setApiError(null)
    try {
      const params = {}
      if (activeFilters.role_id) params.role_id = activeFilters.role_id
      if (activeFilters.days_warning) params.days_warning = activeFilters.days_warning
      const data = await listPlans(params)
      setPlans(data.plans || [])
    } catch (e) {
      setApiError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadPlans(filters)
  }, [filters, loadPlans])

  function handleFilterChange(newFilters) {
    setFilters(newFilters)
    setNameSearch('')
    setSelectedPersonId(null)
    setSelectedPlan(null)
  }

  async function handleSelectMember(personId) {
    setSelectedPersonId(personId)
    setDetailLoading(true)
    try {
      const plan = await getPlan(personId)
      setSelectedPlan(plan)
    } catch (e) {
      setSelectedPlan(null)
    } finally {
      setDetailLoading(false)
    }
  }

  const filteredPlans = nameSearch
    ? plans.filter(p => p.name?.toLowerCase().includes(nameSearch.toLowerCase()))
    : plans

  return (
    <div style={{ maxWidth: 1100, margin: '2rem auto', padding: '0 1rem' }}>
      <StalePlansBanner />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' }}>
        <h1 style={{ margin: 0 }}>Training Plans Dashboard</h1>
        <ExportButton />
      </div>

      <PlanFilter filters={filters} onChange={handleFilterChange} />

      <div style={{ marginBottom: '1rem' }}>
        <input
          type="search"
          placeholder="Search by name…"
          value={nameSearch}
          onChange={e => setNameSearch(e.target.value)}
          style={{ padding: '0.4rem 0.6rem', border: '1px solid #ccc', borderRadius: 4, width: 240, fontSize: '0.9rem' }}
        />
      </div>

      {loading && <p>Loading plans…</p>}
      {apiError && <p style={{ color: 'red' }}>{apiError}</p>}
      {!loading && !apiError && filteredPlans.length === 0 && (
        <p style={{ color: '#666', fontStyle: 'italic' }}>No plans found. Generate plans first.</p>
      )}

      {!loading && filteredPlans.length > 0 && (
        <TeamPlansList
          plans={filteredPlans}
          onSelect={handleSelectMember}
          selectedPersonId={selectedPersonId}
        />
      )}

      {selectedPersonId && (
        <div style={{ marginTop: '2rem', borderTop: '2px solid #ddd', paddingTop: '1.5rem' }}>
          {detailLoading ? <p>Loading plan detail…</p> : <MemberPlanDetail plan={selectedPlan} />}
        </div>
      )}
    </div>
  )
}
