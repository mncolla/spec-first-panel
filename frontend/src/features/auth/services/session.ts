import { apiDelete, apiGet, apiSend } from '../../../lib/api.ts'
import type { SessionCreated, SessionPublic, SessionWrite } from '../types.ts'

export function createSession(body: SessionWrite): Promise<SessionCreated> {
  return apiSend<SessionCreated>('POST', '/sesion', body)
}

export function getSession(): Promise<SessionPublic> {
  return apiGet<SessionPublic>('/sesion')
}

export function deleteSession(): Promise<void> {
  return apiDelete('/sesion')
}
