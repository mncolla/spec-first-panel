const TOKEN_KEY = 'lebane:v1:token'

const listeners = new Set<() => void>()

function emit() {
  for (const listener of listeners) {
    listener()
  }
}

export function getSessionToken(): string | null {
  try {
    return sessionStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export function setSessionToken(token: string): void {
  try {
    sessionStorage.setItem(TOKEN_KEY, token)
  } catch {
    return
  }
  emit()
}

export function clearSessionToken(): void {
  try {
    sessionStorage.removeItem(TOKEN_KEY)
  } catch {
    return
  }
  emit()
}

export function subscribeSessionToken(onStoreChange: () => void): () => void {
  listeners.add(onStoreChange)
  return () => {
    listeners.delete(onStoreChange)
  }
}
