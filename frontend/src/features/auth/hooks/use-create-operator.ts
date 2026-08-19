import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createOperator } from '../services/operators.ts'

export function useCreateOperator() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createOperator,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['operators'] })
    },
  })
}
