import { useQuery } from '@tanstack/react-query'
import { listOperators } from '../services/operators.ts'

export function useOperators(enabled: boolean) {
  return useQuery({
    queryKey: ['operators'],
    queryFn: listOperators,
    enabled,
  })
}
