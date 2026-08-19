import { isUnauthorizedError } from '../../lib/api.ts'
import { clearSessionToken } from './token.ts'

export function clearTokenIfUnauthorized(error: unknown): void {
  if (isUnauthorizedError(error)) {
    clearSessionToken()
  }
}
