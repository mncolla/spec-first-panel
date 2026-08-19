import { Link, useLocation } from 'wouter'
import { formatPrice } from '../format.ts'
import type { DepartmentListItem } from '../types.ts'
import { DepartmentThumbnail } from './department-thumbnail.tsx'

type Props = {
  items: DepartmentListItem[]
}

export function DepartmentTable({ items }: Props) {
  const [, setLocation] = useLocation()

  return (
    <div className="sheet overflow-x-auto">
      <table className="w-full min-w-[720px] border-collapse text-left">
        <caption className="sr-only">Departamentos en inventario</caption>
        <thead>
          <tr className="border-b border-line text-[0.7rem] font-bold tracking-[0.14em] text-ink-soft uppercase">
            <th className="px-4 py-3 pr-3 font-bold">Foto</th>
            <th className="py-3 pr-3 font-bold">ID</th>
            <th className="py-3 pr-3 font-bold">Título</th>
            <th className="py-3 pr-3 font-bold">Precio</th>
            <th className="py-3 pr-3 font-bold">Fotos</th>
            <th className="py-3 pr-4 font-bold">Consultas</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr
              key={item.id}
              className="cursor-pointer border-b border-line/80 last:border-b-0 hover:bg-panel"
              onClick={() => setLocation(`/departamentos/${item.id}`)}
            >
              <td className="px-4 py-3 pr-3">
                <DepartmentThumbnail
                  src={item.imagen_principal}
                  alt={`Foto de ${item.titulo}`}
                />
              </td>
              <td className="py-3 pr-3 font-mono text-xs text-ink-soft">
                <span title={item.id}>{item.id.slice(0, 8)}</span>
              </td>
              <td className="py-3 pr-3">
                <Link
                  href={`/departamentos/${item.id}`}
                  className="font-medium text-ink underline-offset-4 hover:underline"
                  onClick={(event) => event.stopPropagation()}
                >
                  {item.titulo}
                </Link>
                <p className="mt-0.5 text-sm text-ink-soft">{item.direccion}</p>
                <p className="mt-1 text-[0.7rem] font-bold tracking-[0.12em] uppercase">
                  {item.disponible ? (
                    <span className="text-shade">Disponible</span>
                  ) : (
                    <span className="text-ink-soft">No disponible</span>
                  )}
                </p>
              </td>
              <td className="py-3 pr-3 font-mono text-sm font-medium tabular-nums">
                {formatPrice(item.precio, item.moneda)}
              </td>
              <td className="py-3 pr-3 tabular-nums">{item.total_imagenes}</td>
              <td className="py-3 pr-4 tabular-nums">{item.total_consultas}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
