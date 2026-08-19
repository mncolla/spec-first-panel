import { useQuery } from '@tanstack/react-query'
import { listDepartments } from '../services/departments.ts'
import type { DepartmentListFilters } from '../types.ts'

export function useDepartments(filters: DepartmentListFilters) {
  return useQuery({
    queryKey: ['departments', filters],
    queryFn: () => listDepartments(filters),
  })
}
