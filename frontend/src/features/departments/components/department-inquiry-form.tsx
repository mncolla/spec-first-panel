import { useId, useState, type FormEvent, type ReactNode } from 'react'
import {
  emptyInquiryDraft,
  inquiryWriteFromDraft,
  validateInquiryForm,
  type InquiryFormDraft,
} from '../inquiry-form-state.ts'
import {
  MAX_INQUIRY_MESSAGE_LENGTH,
  MAX_INQUIRY_NAME_LENGTH,
  type InquiryWrite,
} from '../types.ts'

type Props = {
  pending: boolean
  apiError?: string
  apiFieldErrors?: Record<string, string>
  onSubmit: (body: InquiryWrite) => void | Promise<void>
  onCancel?: () => void
}

export function DepartmentInquiryForm({
  pending,
  apiError,
  apiFieldErrors = {},
  onSubmit,
  onCancel,
}: Props) {
  const [draft, setDraft] = useState<InquiryFormDraft>(emptyInquiryDraft)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const formId = useId()

  function update<K extends keyof InquiryFormDraft>(key: K, value: InquiryFormDraft[K]) {
    setDraft((current) => ({ ...current, [key]: value }))
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const nextErrors = validateInquiryForm(draft)
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return
    void Promise.resolve(onSubmit(inquiryWriteFromDraft(draft))).then(
      () => {
        setDraft(emptyInquiryDraft())
        setErrors({})
      },
      () => undefined,
    )
  }

  const fieldErrors = { ...errors, ...apiFieldErrors }

  return (
    <form onSubmit={handleSubmit} className="mt-4 grid gap-4" noValidate>
      <p className="text-sm text-ink-soft">
        Registrá a alguien interesado. Nombre, email y mensaje.
      </p>
      <Field id={`${formId}-nombre`} label="Nombre" error={fieldErrors.nombre}>
        <input
          id={`${formId}-nombre`}
          className="field-input"
          value={draft.nombre}
          maxLength={MAX_INQUIRY_NAME_LENGTH}
          autoComplete="name"
          onChange={(event) => update('nombre', event.target.value)}
        />
      </Field>
      <Field id={`${formId}-email`} label="Email" error={fieldErrors.email}>
        <input
          id={`${formId}-email`}
          type="email"
          className="field-input"
          value={draft.email}
          autoComplete="email"
          onChange={(event) => update('email', event.target.value)}
        />
      </Field>
      <Field id={`${formId}-mensaje`} label="Mensaje" error={fieldErrors.mensaje}>
        <textarea
          id={`${formId}-mensaje`}
          className="field-input min-h-24"
          value={draft.mensaje}
          maxLength={MAX_INQUIRY_MESSAGE_LENGTH}
          onChange={(event) => update('mensaje', event.target.value)}
        />
      </Field>
      {apiError ? (
        <div role="alert" className="sheet px-4 py-3 text-danger">
          {apiError}
        </div>
      ) : null}
      <div className="flex flex-wrap gap-2">
        <button
          type="submit"
          disabled={pending}
          className="btn-primary justify-self-start disabled:opacity-60"
        >
          {pending ? 'Enviando…' : 'Enviar'}
        </button>
        {onCancel ? (
          <button
            type="button"
            disabled={pending}
            className="btn-ghost disabled:opacity-60"
            onClick={onCancel}
          >
            Cancelar
          </button>
        ) : null}
      </div>
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
      <label htmlFor={id} className="field-label">
        {label}
      </label>
      {children}
      {error ? <p className="text-danger">{error}</p> : null}
    </div>
  )
}
