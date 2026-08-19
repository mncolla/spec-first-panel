import { useId, useState, type KeyboardEvent } from 'react'
import { useAddressSearch } from '../hooks/use-address-search.ts'
import type { AddressSuggestion } from '../types.ts'

type Props = {
  id?: string
  value: string
  error?: string
  onValueChange: (value: string) => void
  onSelect: (suggestion: AddressSuggestion) => void
}

export function AddressAutocomplete({
  id,
  value,
  error,
  onValueChange,
  onSelect,
}: Props) {
  const generatedId = useId()
  const inputId = id ?? generatedId
  const listId = `${inputId}-list`
  const errorId = `${inputId}-error`
  const [committed, setCommitted] = useState(() => value.trim().length > 0)
  const { results, status } = useAddressSearch(committed ? '' : value)
  const [highlight, setHighlight] = useState(0)
  const open = !committed && results.length > 0

  function handleSelect(suggestion: AddressSuggestion) {
    setCommitted(true)
    setHighlight(0)
    onSelect(suggestion)
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'Escape') {
      event.preventDefault()
      setCommitted(true)
      return
    }
    if (!open) return
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      setHighlight((current) => (current + 1) % results.length)
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      setHighlight((current) => (current - 1 + results.length) % results.length)
    } else if (event.key === 'Enter') {
      event.preventDefault()
      const selected = results[highlight]
      if (selected) handleSelect(selected)
    }
  }

  return (
    <div className="relative">
      <label className="flex flex-col gap-1 text-sm" htmlFor={inputId}>
        <span className="field-label">
          Dirección
        </span>
        <input
          id={inputId}
          role="combobox"
          aria-autocomplete="list"
          aria-expanded={open}
          aria-controls={listId}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? errorId : undefined}
          autoComplete="off"
          value={value}
          onChange={(event) => {
            setCommitted(false)
            setHighlight(0)
            onValueChange(event.target.value)
          }}
          onKeyDown={handleKeyDown}
          className="field-input"
          placeholder="Calle y barrio en CABA"
        />
      </label>
      {status === 'loading' ? (
        <p className="mt-1 text-sm text-ink-soft">Buscando direcciones…</p>
      ) : null}
      {status === 'empty' ? (
        <p className="mt-1 text-sm text-ink-soft">No hay sugerencias para esa búsqueda.</p>
      ) : null}
      {status === 'error' ? (
        <p role="alert" className="mt-1 text-sm text-danger">
          No se pudo buscar la dirección. Probá de nuevo.
        </p>
      ) : null}
      {open ? (
        <ul
          id={listId}
          role="listbox"
          className="sheet absolute z-10 mt-1 max-h-56 w-full overflow-auto"
        >
          {results.map((item, index) => (
            <li key={item.id}>
              <button
                type="button"
                role="option"
                aria-selected={index === highlight}
                className={`block w-full px-3 py-2 text-left text-sm ${
                  index === highlight ? 'bg-bloom/10' : 'hover:bg-panel'
                }`}
                onMouseEnter={() => setHighlight(index)}
                onClick={() => handleSelect(item)}
              >
                {item.label}
              </button>
            </li>
          ))}
        </ul>
      ) : null}
      {error ? (
        <p id={errorId} className="mt-1 text-sm text-danger">
          {error}
        </p>
      ) : null}
    </div>
  )
}
