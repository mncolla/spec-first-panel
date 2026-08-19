import { useSyncExternalStore } from 'react'
import { getSessionToken, subscribeSessionToken } from '../token.ts'

export function useSessionToken(): string | null {
  return useSyncExternalStore(subscribeSessionToken, getSessionToken, () => null)
}
