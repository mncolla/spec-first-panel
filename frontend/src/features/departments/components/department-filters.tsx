import type { FormEvent } from 'react'

export type FilterDraft = {
  disponible: '' | 'true' | 'false'
  precio_min: string
  precio_max: string
  metros_min: string
  metros_max: string
}

type Props = {
  draft: FilterDraft
  onDraftChange: (draft: FilterDraft) => void
  onSubmit: () => void
  onReset: () => void
}

const emptyDraft: FilterDraft = {
  disponible: '',
  precio_min: '',
  precio_max: '',
  metros_min: '',
  metros_max: '',
}

export const EMPTY_FILTER_DRAFT = emptyDraft

export function DepartmentFilters({ draft, onDraftChange, onSubmit, onReset }: Props) {
  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    onSubmit()
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="sheet grid gap-3 p-4 md:grid-cols-6 md:items-end"
    >
      <label className="flex flex-col gap-1 text-sm">
        <span className="field-label">Estado</span>
        <select
          className="field-input"
          value={draft.disponible}
          onChange={(event) =>
            onDraftChange({
              ...draft,
              disponible: event.target.value as FilterDraft['disponible'],
            })
          }
        >
          <option value="">Todos</option>
          <option value="true">Disponible</option>
          <option value="false">No disponible</option>
        </select>
      </label>
      <NumberField
        label="Precio mín."
        value={draft.precio_min}
        onChange={(precio_min) => onDraftChange({ ...draft, precio_min })}
      />
      <NumberField
        label="Precio máx."
        value={draft.precio_max}
        onChange={(precio_max) => onDraftChange({ ...draft, precio_max })}
      />
      <NumberField
        label="m² mín."
        value={draft.metros_min}
        onChange={(metros_min) => onDraftChange({ ...draft, metros_min })}
      />
      <NumberField
        label="m² máx."
        value={draft.metros_max}
        onChange={(metros_max) => onDraftChange({ ...draft, metros_max })}
      />
      <div className="flex gap-2">
        <button type="submit" className="btn-primary flex-1">
          Filtrar
        </button>
        <button type="button" onClick={onReset} className="btn-ghost">
          Limpiar
        </button>
      </div>
    </form>
  )
}

function NumberField({
  label,
  value,
  onChange,
}: {
  label: string
  value: string
  onChange: (value: string) => void
}) {
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span className="field-label">{label}</span>
      <input
        type="number"
        min="0"
        inputMode="numeric"
        className="field-input"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  )
}
