import { useId, useState, type FormEvent, type ReactNode } from 'react'
import {
  emptyLoginDraft,
  sessionWriteFromDraft,
  validateLoginForm,
  type LoginDraft,
} from '../login-form-state.ts'
import type { SessionWrite } from '../types.ts'

type Props = {
  pending: boolean
  apiError?: string
  onSubmit: (body: SessionWrite) => void
}

export function LoginForm({ pending, apiError, onSubmit }: Props) {
  const [draft, setDraft] = useState<LoginDraft>(emptyLoginDraft)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const formId = useId()

  function update<K extends keyof LoginDraft>(key: K, value: LoginDraft[K]) {
    setDraft((current) => ({ ...current, [key]: value }))
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const nextErrors = validateLoginForm(draft)
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return
    onSubmit(sessionWriteFromDraft(draft))
  }

  return (
    <form onSubmit={handleSubmit} className="grid gap-4" noValidate>
      <Field id={`${formId}-email`} label="Email" error={errors.email}>
        <input
          id={`${formId}-email`}
          type="email"
          className="field-input"
          value={draft.email}
          autoComplete="username"
          onChange={(event) => update('email', event.target.value)}
        />
      </Field>
      <Field id={`${formId}-clave`} label="Clave" error={errors.clave}>
        <input
          id={`${formId}-clave`}
          type="password"
          className="field-input"
          value={draft.clave}
          autoComplete="current-password"
          onChange={(event) => update('clave', event.target.value)}
        />
      </Field>
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
        {pending ? 'Ingresando…' : 'Ingresar'}
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
    <div className="grid gap-1">
      <label htmlFor={id} className="field-label">
        {label}
      </label>
      {children}
      {error ? (
        <p className="text-sm text-danger" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  )
}
