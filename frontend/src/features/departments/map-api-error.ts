import { isApiError } from '../../lib/api.ts'

export type MappedApiError = {
  message: string
  fields: Record<string, string>
}

type FastApiIssue = {
  loc?: unknown[]
  msg?: string
}

export function mapApiError(error: unknown): MappedApiError {
  if (!isApiError(error)) {
    return {
      message: 'No se pudo guardar. Comprobá que la API esté en marcha.',
      fields: {},
    }
  }
  if (typeof error.detail === 'string') {
    return { message: humanizeDomain(error.detail), fields: {} }
  }
  if (!Array.isArray(error.detail)) {
    return {
      message: error.status === 404 ? 'No encontramos ese departamento.' : 'No se pudo guardar.',
      fields: {},
    }
  }
  const fields: Record<string, string> = {}
  for (const item of error.detail as FastApiIssue[]) {
    const key = fieldFromLoc(item.loc)
    if (key && item.msg) {
      fields[key] = humanizePydantic(item.msg)
    }
  }
  return {
    message: 'Revisá los campos marcados.',
    fields,
  }
}

function fieldFromLoc(loc: unknown[] | undefined): string | undefined {
  if (!loc) return undefined
  for (let index = loc.length - 1; index >= 0; index -= 1) {
    const part = loc[index]
    if (typeof part === 'string' && part !== 'body') return part
  }
  return undefined
}

function humanizePydantic(message: string): string {
  if (message.includes('at least 3')) return 'El título debe tener al menos 3 caracteres.'
  if (message.includes('at most 120')) return 'El título no puede superar 120 caracteres.'
  return message
}

function humanizeDomain(detail: string): string {
  if (detail.includes('available departments')) {
    return 'Solo se pueden registrar consultas en departamentos disponibles.'
  }
  if (detail.includes('Inquiry email')) return 'El email no es válido.'
  if (detail.includes('Inquiry name is required')) return 'El nombre es obligatorio.'
  if (detail.includes('Inquiry message is required')) return 'El mensaje es obligatorio.'
  return detail
}
