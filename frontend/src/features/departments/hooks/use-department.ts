import { useQuery } from '@tanstack/react-query'
import { isNotFoundError } from '../../../lib/api.ts'
import { getDepartment } from '../services/departments.ts'

export function useDepartment(id: string | undefined) {
  return useQuery({
    queryKey: ['department', id],
    queryFn: () => getDepartment(id!),
    enabled: Boolean(id),
    retry: (failureCount, error) => {
      if (isNotFoundError(error)) return false
      return failureCount < 1
    },
  })
}
