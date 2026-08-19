import { useQuery } from '@tanstack/react-query'
import { getSession } from '../services/session.ts'
import { useSessionToken } from './use-session-token.ts'

export function useSession() {
  const token = useSessionToken()
  return useQuery({
    queryKey: ['session'],
    queryFn: getSession,
    enabled: Boolean(token),
  })
}
