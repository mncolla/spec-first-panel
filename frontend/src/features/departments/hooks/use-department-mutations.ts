import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createDepartment, updateDepartment } from '../services/departments.ts'
import type { DepartmentWrite } from '../types.ts'

export function useCreateDepartment() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createDepartment,
    onSuccess: async (created) => {
      await queryClient.invalidateQueries({ queryKey: ['departments'] })
      queryClient.setQueryData(['department', created.id], created)
    },
  })
}

export function useUpdateDepartment(id: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: DepartmentWrite) => updateDepartment(id, body),
    onSuccess: async (updated) => {
      queryClient.setQueryData(['department', id], updated)
      await queryClient.invalidateQueries({ queryKey: ['departments'] })
    },
  })
}
