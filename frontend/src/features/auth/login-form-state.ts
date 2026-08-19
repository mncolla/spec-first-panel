import type { SessionWrite } from './types.ts'

export type LoginDraft = {
  email: string
  clave: string
}

const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/
const MIN_PASSWORD_LENGTH = 8

export function emptyLoginDraft(): LoginDraft {
  return { email: '', clave: '' }
}

export function validateLoginForm(draft: LoginDraft): Record<string, string> {
  const errors: Record<string, string> = {}
  const email = draft.email.trim()
  const clave = draft.clave

  if (!email) {
    errors.email = 'El email es obligatorio.'
  } else if (EMAIL.exec(email) === null) {
    errors.email = 'El email no es válido.'
  }

  if (!clave) {
    errors.clave = 'La clave es obligatoria.'
  } else if (clave.length < MIN_PASSWORD_LENGTH) {
    errors.clave = 'La clave debe tener al menos 8 caracteres.'
  }

  return errors
}

export function sessionWriteFromDraft(draft: LoginDraft): SessionWrite {
  return {
    email: draft.email.trim(),
    clave: draft.clave,
  }
}
