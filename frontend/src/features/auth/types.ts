export type OperatorRole = 'admin' | 'agente'

export type SessionPublic = {
  email: string
  rol: OperatorRole
}

export type SessionCreated = SessionPublic & {
  token: string
}

export type SessionWrite = {
  email: string
  clave: string
}
