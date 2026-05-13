import { useState, useRef } from 'react'

export default function FileUpload({ onUpload, accept = '.csv', label = 'Choose CSV file' }) {
  const [dragging, setDragging] = useState(false)
  const [filename, setFilename] = useState(null)
  const inputRef = useRef()

  function handleFile(file) {
    if (!file) return
    setFilename(file.name)
    onUpload(file)
  }

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]) }}
      onClick={() => inputRef.current.click()}
      style={{
        border: `2px dashed ${dragging ? '#0066cc' : '#aaa'}`,
        borderRadius: 8,
        padding: '2rem',
        textAlign: 'center',
        cursor: 'pointer',
        background: dragging ? '#f0f7ff' : '#fafafa',
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        style={{ display: 'none' }}
        onChange={(e) => handleFile(e.target.files[0])}
      />
      <p>{filename ? `Selected: ${filename}` : label}</p>
      <p style={{ fontSize: '0.85rem', color: '#666' }}>Drag and drop or click to browse</p>
    </div>
  )
}
