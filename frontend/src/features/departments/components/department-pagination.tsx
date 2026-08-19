type Props = {
  pagina: number
  cantidad: number
  total: number
  onPageChange: (pagina: number) => void
}

export function DepartmentPagination({ pagina, cantidad, total, onPageChange }: Props) {
  const pageCount = Math.max(1, Math.ceil(total / cantidad))
  const previous = pagina > 1
  const next = pagina < pageCount

  return (
    <nav
      aria-label="Paginación"
      className="flex flex-wrap items-center justify-between gap-3 pt-1 text-sm"
    >
      <p className="text-ink-soft">
        Página {pagina} de {pageCount} · {total} departamentos
      </p>
      <div className="flex gap-2">
        <button
          type="button"
          disabled={!previous}
          onClick={() => onPageChange(pagina - 1)}
          className="btn-ghost"
        >
          Anterior
        </button>
        <button
          type="button"
          disabled={!next}
          onClick={() => onPageChange(pagina + 1)}
          className="btn-ghost"
        >
          Siguiente
        </button>
      </div>
    </nav>
  )
}
