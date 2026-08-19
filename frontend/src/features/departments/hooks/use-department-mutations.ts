import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createDepartment, createInquiry, updateDepartment } from '../services/departments.ts'
import type { DepartmentWrite, InquiryWrite } from '../types.ts'

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

export function useCreateInquiry(id: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: InquiryWrite) => createInquiry(id, body),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['department', id] })
      await queryClient.invalidateQueries({ queryKey: ['departments'] })
    },
  })
}
