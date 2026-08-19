import type { OperatorRole } from './types.ts'

export function roleLabel(role: OperatorRole): string {
  return role === 'admin' ? 'Admin' : 'Agente'
}
