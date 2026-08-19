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

export type OperatorWrite = {
  email: string
  clave: string
  rol: 'agente'
}

export type OperatorDetail = {
  email: string
  rol: OperatorRole
}

export type OperatorListResponse = {
  items: OperatorDetail[]
}
