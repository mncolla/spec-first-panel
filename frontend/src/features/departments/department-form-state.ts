import {
  MAX_DEPARTMENT_IMAGES,
  MAX_DESCRIPTION_LENGTH,
  MAX_TITLE_LENGTH,
  MIN_TITLE_LENGTH,
  type Currency,
  type DepartmentDetail,
} from './types.ts'

export type DepartmentFormDraft = {
  titulo: string
  descripcion: string
  direccion: string
  lat: number | null
  lng: number | null
  precio: string
  moneda: Currency
  metros_cuadrados: string
  disponible: boolean
  imagenes: string[]
}

export function emptyDraft(): DepartmentFormDraft {
  return {
    titulo: '',
    descripcion: '',
    direccion: '',
    lat: null,
    lng: null,
    precio: '',
    moneda: 'USD',
    metros_cuadrados: '',
    disponible: true,
    imagenes: [],
  }
}

export function draftFromDetail(detail: DepartmentDetail): DepartmentFormDraft {
  return {
    titulo: detail.titulo,
    descripcion: detail.descripcion ?? '',
    direccion: detail.direccion,
    lat: detail.lat,
    lng: detail.lng,
    precio: String(detail.precio),
    moneda: detail.moneda,
    metros_cuadrados: String(detail.metros_cuadrados),
    disponible: detail.disponible,
    imagenes: [...detail.imagenes],
  }
}

export function validateDepartmentForm(
  draft: DepartmentFormDraft,
  initial?: DepartmentDetail,
): Record<string, string> {
  const errors: Record<string, string> = {}
  const titulo = draft.titulo.trim()
  if (titulo.length < MIN_TITLE_LENGTH) {
    errors.titulo = `El título debe tener al menos ${MIN_TITLE_LENGTH} caracteres.`
  } else if (titulo.length > MAX_TITLE_LENGTH) {
    errors.titulo = `El título no puede superar ${MAX_TITLE_LENGTH} caracteres.`
  }
  if (draft.descripcion.length > MAX_DESCRIPTION_LENGTH) {
    errors.descripcion = `La descripción no puede superar ${MAX_DESCRIPTION_LENGTH} caracteres.`
  }
  const precio = Number(draft.precio)
  if (!Number.isFinite(precio) || precio <= 0) {
    errors.precio = 'El precio debe ser mayor a 0.'
  }
  const meters = Number(draft.metros_cuadrados)
  if (!Number.isFinite(meters) || meters <= 0) {
    errors.metros_cuadrados = 'Los m² deben ser mayores a 0.'
  }
  const address = draft.direccion.trim()
  if (!address) {
    errors.direccion = 'Elegí una dirección de la lista.'
  } else if (draft.lat == null || draft.lng == null) {
    const unchanged = initial != null && address === initial.direccion.trim()
    if (!unchanged) {
      errors.direccion = 'Elegí una dirección de la lista.'
    }
  }
  if (draft.imagenes.length > MAX_DEPARTMENT_IMAGES) {
    errors.imagenes = `Como máximo ${MAX_DEPARTMENT_IMAGES} fotos.`
  }
  return errors
}
