import { useId, useState, type FormEvent, type ReactNode } from 'react'
import { AddressAutocomplete } from '../../address/components/address-autocomplete.tsx'
import {
  MAX_DEPARTMENT_IMAGES,
  MAX_DESCRIPTION_LENGTH,
  MAX_TITLE_LENGTH,
  type Currency,
  type DepartmentDetail,
  type DepartmentWrite,
} from '../types.ts'
import {
  draftFromDetail,
  emptyDraft,
  validateDepartmentForm,
  type DepartmentFormDraft,
} from '../department-form-state.ts'
import { DepartmentThumbnail } from './department-thumbnail.tsx'

type Props = {
  initial?: DepartmentDetail
  submitLabel: string
  pending: boolean
  apiError?: string
  apiFieldErrors?: Record<string, string>
  onSubmit: (body: DepartmentWrite) => void
}

const inputClass = 'field-input'
const labelClass = 'field-label'

export function DepartmentForm({
  initial,
  submitLabel,
  pending,
  apiError,
  apiFieldErrors = {},
  onSubmit,
}: Props) {
  const [draft, setDraft] = useState<DepartmentFormDraft>(() =>
    initial ? draftFromDetail(initial) : emptyDraft(),
  )
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [photoLimitHit, setPhotoLimitHit] = useState(false)
  const formId = useId()

  function update<K extends keyof DepartmentFormDraft>(key: K, value: DepartmentFormDraft[K]) {
    setDraft((current) => ({ ...current, [key]: value }))
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const nextErrors = validateDepartmentForm(draft, initial)
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return
    onSubmit({
      titulo: draft.titulo.trim(),
      descripcion: draft.descripcion.trim() ? draft.descripcion.trim() : null,
      precio: Number(draft.precio),
      moneda: draft.moneda,
      metros_cuadrados: Number(draft.metros_cuadrados),
      direccion: draft.direccion.trim(),
      lat: draft.lat,
      lng: draft.lng,
      disponible: draft.disponible,
      imagenes: draft.imagenes,
    })
  }

  async function handleFiles(fileList: FileList | null) {
    if (!fileList || fileList.length === 0) return
    const incoming = Array.from(fileList).filter((file) => file.type.startsWith('image/'))
    const room = MAX_DEPARTMENT_IMAGES - draft.imagenes.length
    setPhotoLimitHit(incoming.length > room)
    const accepted = incoming.slice(0, Math.max(0, room))
    if (accepted.length === 0) return
    const urls = await Promise.all(accepted.map(fileToDataUrl))
    setDraft((current) => ({
      ...current,
      imagenes: [...current.imagenes, ...urls].slice(0, MAX_DEPARTMENT_IMAGES),
    }))
  }

  const fieldErrors = { ...errors, ...apiFieldErrors }
  const photoInputDisabled = draft.imagenes.length >= MAX_DEPARTMENT_IMAGES || pending

  return (
    <form onSubmit={handleSubmit} className="grid gap-4" noValidate>
      <Field
        id={`${formId}-titulo`}
        label="Título"
        error={fieldErrors.titulo}
      >
        <input
          id={`${formId}-titulo`}
          className={inputClass}
          value={draft.titulo}
          maxLength={MAX_TITLE_LENGTH}
          onChange={(event) => update('titulo', event.target.value)}
        />
      </Field>

      <AddressAutocomplete
        id={`${formId}-direccion`}
        value={draft.direccion}
        error={fieldErrors.direccion}
        onValueChange={(value) => {
          setDraft((current) => ({
            ...current,
            direccion: value,
            lat: null,
            lng: null,
          }))
        }}
        onSelect={(suggestion) => {
          setDraft((current) => ({
            ...current,
            direccion: suggestion.label,
            lat: suggestion.lat,
            lng: suggestion.lng,
          }))
        }}
      />

      <Field id={`${formId}-descripcion`} label="Descripción" error={fieldErrors.descripcion}>
        <textarea
          id={`${formId}-descripcion`}
          className={`${inputClass} min-h-28`}
          value={draft.descripcion}
          maxLength={MAX_DESCRIPTION_LENGTH}
          onChange={(event) => update('descripcion', event.target.value)}
        />
      </Field>

      <div className="grid gap-4 md:grid-cols-3">
        <Field id={`${formId}-precio`} label="Precio" error={fieldErrors.precio}>
          <input
            id={`${formId}-precio`}
            className={inputClass}
            type="number"
            min="0"
            step="any"
            inputMode="decimal"
            value={draft.precio}
            onChange={(event) => update('precio', event.target.value)}
          />
        </Field>
        <Field id={`${formId}-moneda`} label="Moneda" error={fieldErrors.moneda}>
          <select
            id={`${formId}-moneda`}
            className={inputClass}
            value={draft.moneda}
            onChange={(event) => update('moneda', event.target.value as Currency)}
          >
            <option value="USD">USD</option>
            <option value="ARS">ARS</option>
          </select>
        </Field>
        <Field id={`${formId}-metros`} label="m²" error={fieldErrors.metros_cuadrados}>
          <input
            id={`${formId}-metros`}
            className={inputClass}
            type="number"
            min="0"
            step="any"
            inputMode="decimal"
            value={draft.metros_cuadrados}
            onChange={(event) => update('metros_cuadrados', event.target.value)}
          />
        </Field>
      </div>

      <label className="flex items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={draft.disponible}
          onChange={(event) => update('disponible', event.target.checked)}
        />
        Disponible para la venta
      </label>

      <fieldset className="sheet p-4">
        <legend className={`${labelClass} px-1`}>Fotos (máximo {MAX_DEPARTMENT_IMAGES})</legend>
        <input
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          multiple
          disabled={photoInputDisabled}
          aria-label="Adjuntar fotos"
          onChange={(event) => {
            void handleFiles(event.target.files)
            event.target.value = ''
          }}
          className="block text-sm"
        />
        {photoLimitHit || fieldErrors.imagenes ? (
          <p className="mt-2 text-sm text-danger" role="alert">
            {fieldErrors.imagenes ?? `Como máximo ${MAX_DEPARTMENT_IMAGES} fotos.`}
          </p>
        ) : (
          <p className="mt-2 text-sm text-ink-soft">
            {draft.imagenes.length}/{MAX_DEPARTMENT_IMAGES} fotos. JPEG, PNG, WebP o GIF.
          </p>
        )}
        {draft.imagenes.length > 0 ? (
          <ul className="mt-3 flex flex-wrap gap-3">
            {draft.imagenes.map((src, index) => (
              <li key={`${src}-${index}`} className="flex flex-col items-start gap-1">
                <DepartmentThumbnail src={src} alt={`Foto ${index + 1}`} />
                <button
                  type="button"
                  className="text-xs text-danger underline-offset-2 hover:underline"
                  onClick={() => {
                    setPhotoLimitHit(false)
                    setDraft((current) => ({
                      ...current,
                      imagenes: current.imagenes.filter((_, itemIndex) => itemIndex !== index),
                    }))
                  }}
                >
                  Quitar
                </button>
              </li>
            ))}
          </ul>
        ) : null}
      </fieldset>

      {apiError ? (
        <div role="alert" className="sheet px-4 py-3 text-danger">
          {apiError}
        </div>
      ) : null}

      <button
        type="submit"
        disabled={pending}
        className="btn-primary justify-self-start disabled:opacity-60"
      >
        {pending ? 'Guardando…' : submitLabel}
      </button>
    </form>
  )
}

function Field({
  id,
  label,
  error,
  children,
}: {
  id: string
  label: string
  error?: string
  children: ReactNode
}) {
  return (
    <div className="flex flex-col gap-1 text-sm">
      <label htmlFor={id} className={labelClass}>
        {label}
      </label>
      {children}
      {error ? <p className="text-danger">{error}</p> : null}
    </div>
  )
}

function fileToDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result))
    reader.onerror = () => reject(reader.error ?? new Error('No se pudo leer la foto'))
    reader.readAsDataURL(file)
  })
}
