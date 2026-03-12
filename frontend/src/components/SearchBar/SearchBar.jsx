export function SearchBar({ value, onChange, placeholder }) {
  return (
    <div style={{ margin: '16px 0 24px' }}>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        style={{
          width: '100%',
          padding: '12px 14px',
          fontSize: 16,
          borderRadius: 10,
          border: '1px solid #ddd',
        }}
      />
    </div>
  )
}

