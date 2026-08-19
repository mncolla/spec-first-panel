import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useLocation } from 'wouter'
import { deleteSession } from '../services/session.ts'
import { clearSessionToken } from '../token.ts'

export function useLogout() {
  const queryClient = useQueryClient()
  const [, setLocation] = useLocation()
  return useMutation({
    mutationFn: deleteSession,
    onSettled: () => {
      clearSessionToken()
      queryClient.clear()
      setLocation('/ingresar')
    },
  })
}
