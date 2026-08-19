export const MIN_TITLE_LENGTH = 3
export const MAX_TITLE_LENGTH = 120
export const MAX_DESCRIPTION_LENGTH = 4000
export const MAX_DEPARTMENT_IMAGES = 5

export type Currency = 'USD' | 'ARS'

export type DepartmentListItem = {
  id: string
  titulo: string
  precio: number
  moneda: Currency
  metros_cuadrados: number
  direccion: string
  disponible: boolean
  imagen_principal: string | null
  total_imagenes: number
  total_consultas: number
}

export type DepartmentListResponse = {
  items: DepartmentListItem[]
  pagina: number
  cantidad: number
  total: number
}

export type DepartmentListFilters = {
  pagina: number
  cantidad: number
  disponible?: boolean
  precio_min?: number
  precio_max?: number
  metros_min?: number
  metros_max?: number
}

export type InquiryDetail = {
  nombre: string
  email: string
  mensaje: string
  fecha: string
}

export type DepartmentDetail = {
  id: string
  titulo: string
  descripcion: string | null
  precio: number
  moneda: Currency
  metros_cuadrados: number
  direccion: string
  lat: number | null
  lng: number | null
  disponible: boolean
  imagenes: string[]
  consultas: InquiryDetail[]
  created_at: string
}

export type DepartmentWrite = {
  titulo: string
  descripcion: string | null
  precio: number
  moneda: Currency
  metros_cuadrados: number
  direccion: string
  lat: number | null
  lng: number | null
  disponible: boolean
  imagenes: string[]
}
