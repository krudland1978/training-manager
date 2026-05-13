import { render, screen, fireEvent } from '@testing-library/react'
import FileUpload from '../../src/components/FileUpload'

describe('FileUpload', () => {
  it('renders default label', () => {
    render(<FileUpload onUpload={() => {}} />)
    expect(screen.getByText('Choose CSV file')).toBeInTheDocument()
  })

  it('renders custom label', () => {
    render(<FileUpload onUpload={() => {}} label="Upload team CSV" />)
    expect(screen.getByText('Upload team CSV')).toBeInTheDocument()
  })

  it('shows filename after file is selected', () => {
    const onUpload = jest.fn()
    render(<FileUpload onUpload={onUpload} />)

    const file = new File(['name,grade\nAlice,7'], 'team.csv', { type: 'text/csv' })
    const input = document.querySelector('input[type="file"]')
    fireEvent.change(input, { target: { files: [file] } })

    expect(screen.getByText('Selected: team.csv')).toBeInTheDocument()
    expect(onUpload).toHaveBeenCalledWith(file)
  })

  it('calls onUpload when file selected via input', () => {
    const onUpload = jest.fn()
    render(<FileUpload onUpload={onUpload} />)

    const file = new File(['data'], 'data.csv', { type: 'text/csv' })
    const input = document.querySelector('input[type="file"]')
    fireEvent.change(input, { target: { files: [file] } })

    expect(onUpload).toHaveBeenCalledTimes(1)
    expect(onUpload).toHaveBeenCalledWith(file)
  })
})
