import {
  MAX_INQUIRY_MESSAGE_LENGTH,
  MAX_INQUIRY_NAME_LENGTH,
  type InquiryWrite,
} from './types.ts'

export type InquiryFormDraft = {
  nombre: string
  email: string
  mensaje: string
}

const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/

export function emptyInquiryDraft(): InquiryFormDraft {
  return { nombre: '', email: '', mensaje: '' }
}

export function validateInquiryForm(draft: InquiryFormDraft): Record<string, string> {
  const errors: Record<string, string> = {}
  const nombre = draft.nombre.trim()
  const email = draft.email.trim()
  const mensaje = draft.mensaje.trim()

  if (!nombre) {
    errors.nombre = 'El nombre es obligatorio.'
  } else if (nombre.length > MAX_INQUIRY_NAME_LENGTH) {
    errors.nombre = `El nombre no puede superar ${MAX_INQUIRY_NAME_LENGTH} caracteres.`
  }

  if (!email) {
    errors.email = 'El email es obligatorio.'
  } else if (EMAIL.exec(email) === null) {
    errors.email = 'El email no es válido.'
  }

  if (!mensaje) {
    errors.mensaje = 'El mensaje es obligatorio.'
  } else if (mensaje.length > MAX_INQUIRY_MESSAGE_LENGTH) {
    errors.mensaje = `El mensaje no puede superar ${MAX_INQUIRY_MESSAGE_LENGTH} caracteres.`
  }

  return errors
}

export function inquiryWriteFromDraft(draft: InquiryFormDraft): InquiryWrite {
  return {
    nombre: draft.nombre.trim(),
    email: draft.email.trim(),
    mensaje: draft.mensaje.trim(),
  }
}
