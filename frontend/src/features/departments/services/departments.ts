import { apiGet, apiSend } from '../../../lib/api.ts'
import type {
  DepartmentDetail,
  DepartmentListFilters,
  DepartmentListResponse,
  DepartmentWrite,
} from '../types.ts'

export function listDepartments(
  filters: DepartmentListFilters,
): Promise<DepartmentListResponse> {
  const params: Record<string, string> = {
    pagina: String(filters.pagina),
    cantidad: String(filters.cantidad),
  }
  if (filters.disponible !== undefined) {
    params.disponible = String(filters.disponible)
  }
  if (filters.precio_min !== undefined) {
    params.precio_min = String(filters.precio_min)
  }
  if (filters.precio_max !== undefined) {
    params.precio_max = String(filters.precio_max)
  }
  if (filters.metros_min !== undefined) {
    params.metros_min = String(filters.metros_min)
  }
  if (filters.metros_max !== undefined) {
    params.metros_max = String(filters.metros_max)
  }
  return apiGet<DepartmentListResponse>('/departamentos', params)
}

export function getDepartment(id: string): Promise<DepartmentDetail> {
  return apiGet<DepartmentDetail>(`/departamentos/${id}`)
}

export function createDepartment(body: DepartmentWrite): Promise<DepartmentDetail> {
  return apiSend<DepartmentDetail>('POST', '/departamentos', body)
}

export function updateDepartment(
  id: string,
  body: DepartmentWrite,
): Promise<DepartmentDetail> {
  return apiSend<DepartmentDetail>('PUT', `/departamentos/${id}`, body)
}
