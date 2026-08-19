import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createSession } from '../services/session.ts'
import { setSessionToken } from '../token.ts'
import type { SessionPublic, SessionWrite } from '../types.ts'

export function useLogin() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: SessionWrite) => createSession(body),
    onSuccess: (created) => {
      setSessionToken(created.token)
      const session: SessionPublic = { email: created.email, rol: created.rol }
      queryClient.setQueryData(['session'], session)
    },
  })
}
