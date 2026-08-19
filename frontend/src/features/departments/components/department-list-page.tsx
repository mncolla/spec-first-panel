import { useMemo, useState } from 'react'
import { Link } from 'wouter'
import { useDepartments } from '../hooks/use-departments.ts'
import type { DepartmentListFilters } from '../types.ts'
import {
  DepartmentFilters,
  EMPTY_FILTER_DRAFT,
  type FilterDraft,
} from './department-filters.tsx'
import { DepartmentPagination } from './department-pagination.tsx'
import { DepartmentTable } from './department-table.tsx'

const PAGE_SIZE = 20

export function DepartmentListPage() {
  const [draft, setDraft] = useState<FilterDraft>(EMPTY_FILTER_DRAFT)
  const [applied, setApplied] = useState<FilterDraft>(EMPTY_FILTER_DRAFT)
  const [pagina, setPagina] = useState(1)

  const filters = useMemo(
    () => toQueryFilters(applied, pagina),
    [applied, pagina],
  )
  const query = useDepartments(filters)

  function applyFilters() {
    setApplied(draft)
    setPagina(1)
  }

  function resetFilters() {
    setDraft(EMPTY_FILTER_DRAFT)
    setApplied(EMPTY_FILTER_DRAFT)
    setPagina(1)
  }

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-8 md:px-8">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="font-display text-4xl font-extrabold tracking-tight text-ink md:text-[2.75rem]">
            Inventario
          </h1>
          <p className="mt-1 text-sm text-ink-soft">
            Departamentos en venta. Filtrá y abrí una ficha.
          </p>
        </div>
        <Link href="/departamentos/nuevo" className="btn-primary">
          Agregar Departamento
        </Link>
      </header>

      <DepartmentFilters
        draft={draft}
        onDraftChange={setDraft}
        onSubmit={applyFilters}
        onReset={resetFilters}
      />

      {query.isPending ? (
        <p className="text-ink-soft">Cargando inventario…</p>
      ) : null}

      {query.isError ? (
        <div
          role="alert"
          className="sheet px-4 py-4 text-danger"
        >
          <p className="font-semibold">No se pudo cargar el inventario.</p>
          <p className="mt-1 text-sm">Comprobá que la API esté en marcha y reintentá.</p>
          <button
            type="button"
            onClick={() => void query.refetch()}
            className="btn-ghost mt-3"
          >
            Reintentar
          </button>
        </div>
      ) : null}

      {query.data && query.data.items.length === 0 ? (
        <div className="sheet px-4 py-10 text-center">
          {hasActiveFilters(applied) ? (
            <>
              <p className="font-medium">No hay departamentos con esos filtros.</p>
              <p className="mt-1 text-sm text-ink-soft">
                Probá limpiar los filtros o cargá uno nuevo.
              </p>
            </>
          ) : (
            <>
              <p className="font-medium">Todavía no hay departamentos en el inventario.</p>
              <p className="mt-1 text-sm text-ink-soft">
                Usá Agregar Departamento para cargar el primero.
              </p>
            </>
          )}
        </div>
      ) : null}

      {query.data && query.data.items.length > 0 ? (
        <>
          <DepartmentTable items={query.data.items} />
          <DepartmentPagination
            pagina={query.data.pagina}
            cantidad={query.data.cantidad}
            total={query.data.total}
            onPageChange={setPagina}
          />
        </>
      ) : null}
    </div>
  )
}

function hasActiveFilters(draft: FilterDraft): boolean {
  return (
    draft.disponible !== '' ||
    draft.precio_min.trim() !== '' ||
    draft.precio_max.trim() !== '' ||
    draft.metros_min.trim() !== '' ||
    draft.metros_max.trim() !== ''
  )
}

function toQueryFilters(draft: FilterDraft, pagina: number): DepartmentListFilters {
  return {
    pagina,
    cantidad: PAGE_SIZE,
    disponible:
      draft.disponible === '' ? undefined : draft.disponible === 'true',
    precio_min: parseOptionalNumber(draft.precio_min),
    precio_max: parseOptionalNumber(draft.precio_max),
    metros_min: parseOptionalNumber(draft.metros_min),
    metros_max: parseOptionalNumber(draft.metros_max),
  }
}

function parseOptionalNumber(value: string): number | undefined {
  const trimmed = value.trim()
  if (!trimmed) return undefined
  const parsed = Number(trimmed)
  return Number.isFinite(parsed) ? parsed : undefined
}
