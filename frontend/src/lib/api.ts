import { clearSessionToken, getSessionToken } from '../features/auth/token.ts'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export class ApiError extends Error {
  readonly status: number
  readonly detail: unknown

  constructor(status: number, detail: unknown) {
    super(`API ${status}`)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError
}

export function isNotFoundError(error: unknown): boolean {
  return isApiError(error) && error.status === 404
}

export function isUnauthorizedError(error: unknown): boolean {
  return isApiError(error) && error.status === 401
}

function authHeaders(): HeadersInit {
  const token = getSessionToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function apiGet<T>(path: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(path, API_URL)
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      url.searchParams.set(key, value)
    }
  }
  return parseResponse<T>(
    await fetch(url, {
      headers: authHeaders(),
    }),
  )
}

export async function apiSend<T>(method: 'POST' | 'PUT', path: string, body: unknown): Promise<T> {
  const url = new URL(path, API_URL)
  return parseResponse<T>(
    await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(body),
    }),
  )
}

export async function apiDelete(path: string): Promise<void> {
  const url = new URL(path, API_URL)
  await parseResponse<void>(
    await fetch(url, {
      method: 'DELETE',
      headers: authHeaders(),
    }),
  )
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (response.status === 401) {
    clearSessionToken()
  }
  if (response.ok) {
    if (response.status === 204) {
      return undefined as T
    }
    return (await response.json()) as T
  }
  let payload: unknown
  try {
    payload = await response.json()
  } catch {
    payload = undefined
  }
  const detail =
    payload && typeof payload === 'object' && 'detail' in payload
      ? (payload as { detail: unknown }).detail
      : payload
  throw new ApiError(response.status, detail)
}
