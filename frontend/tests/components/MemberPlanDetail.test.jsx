import { render, screen } from '@testing-library/react'
import MemberPlanDetail from '../../src/components/MemberPlanDetail'

const SAMPLE_PLAN = {
  person_id: 'P001',
  name: 'Alice Smith',
  role_id: 'solution_architect',
  grade_level: 7,
  required_cert_ids: ['aws-sap'],
  certs_held: ['aws-saa'],
  outstanding_certs: [
    { cert_id: 'aws-sap', name: 'SAP', level: 'professional', level_order: 3, effective_study_days: 35 },
  ],
  total_study_days_required: 35,
  days_remaining: 10,
  days_warning: true,
  requirement_met: false,
  no_requirement: false,
}

describe('MemberPlanDetail', () => {
  it('renders nothing when plan is null', () => {
    const { container } = render(<MemberPlanDetail plan={null} />)
    expect(container).toBeEmptyDOMElement()
  })

  it('shows member name', () => {
    render(<MemberPlanDetail plan={SAMPLE_PLAN} />)
    expect(screen.getByText('Alice Smith')).toBeInTheDocument()
  })

  it('shows outstanding cert in table', () => {
    render(<MemberPlanDetail plan={SAMPLE_PLAN} />)
    expect(screen.getByText('SAP')).toBeInTheDocument()
    expect(screen.getByText('professional')).toBeInTheDocument()
  })

  it('shows "All required certifications are held" when met', () => {
    const plan = { ...SAMPLE_PLAN, requirement_met: true, outstanding_certs: [], total_study_days_required: 0, days_warning: false }
    render(<MemberPlanDetail plan={plan} />)
    expect(screen.getByText(/All required certifications are held/)).toBeInTheDocument()
  })

  it('shows no requirement message when no_requirement is true', () => {
    const plan = { ...SAMPLE_PLAN, no_requirement: true, outstanding_certs: [], required_cert_ids: [] }
    render(<MemberPlanDetail plan={plan} />)
    expect(screen.getByText(/No certification requirement/)).toBeInTheDocument()
  })

  it('shows days warning badge when days_warning is true', () => {
    render(<MemberPlanDetail plan={SAMPLE_PLAN} />)
    expect(screen.getByText(/short/)).toBeInTheDocument()
  })
})
