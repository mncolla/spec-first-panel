import { apiGet, apiSend } from '../../../lib/api.ts'
import type { OperatorDetail, OperatorListResponse, OperatorWrite } from '../types.ts'

export function listOperators(): Promise<OperatorListResponse> {
  return apiGet<OperatorListResponse>('/operadores')
}

export function createOperator(body: OperatorWrite): Promise<OperatorDetail> {
  return apiSend<OperatorDetail>('POST', '/operadores', body)
}
