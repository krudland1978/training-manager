import { render, screen } from '@testing-library/react'
import ImportSummary from '../../src/components/ImportSummary'

describe('ImportSummary', () => {
  it('renders nothing when result is null', () => {
    const { container } = render(<ImportSummary result={null} />)
    expect(container).toBeEmptyDOMElement()
  })

  it('shows imported and skipped counts', () => {
    render(<ImportSummary result={{ imported: 5, skipped: 1 }} />)
    expect(screen.getByText('5')).toBeInTheDocument()
    expect(screen.getByText('1')).toBeInTheDocument()
  })

  it('shows warning count when warnings present', () => {
    const result = {
      imported: 3,
      skipped: 0,
      warnings: [{ cert_id: 'aws-das', reason: 'Retired cert' }],
    }
    render(<ImportSummary result={result} />)
    expect(screen.getByText(/1/)).toBeInTheDocument()
    expect(screen.getByText(/Warnings/)).toBeInTheDocument()
  })

  it('does not show warnings section when empty', () => {
    render(<ImportSummary result={{ imported: 3, skipped: 0, warnings: [] }} />)
    expect(screen.queryByText(/Warnings/)).not.toBeInTheDocument()
  })

  it('shows errors section when errors present', () => {
    const result = {
      imported: 2,
      skipped: 1,
      errors: [{ row: 3, reason: 'Missing grade_level' }],
    }
    render(<ImportSummary result={result} />)
    expect(screen.getByText(/Errors/)).toBeInTheDocument()
    expect(screen.getByText(/Missing grade_level/)).toBeInTheDocument()
  })
})
