import type { ReactNode } from 'react'
import { Redirect } from 'wouter'
import { useSessionToken } from '../hooks/use-session-token.ts'

export function RequireSession({ children }: { children: ReactNode }) {
  const token = useSessionToken()
  if (!token) {
    return <Redirect to="/ingresar" />
  }
  return children
}
