import { roleLabel } from '../role-label.ts'
import type { OperatorDetail } from '../types.ts'

export function OperatorTable({ items }: { items: OperatorDetail[] }) {
  return (
    <div className="sheet overflow-x-auto">
      <table className="w-full border-collapse text-left">
        <caption className="sr-only">Operadores del panel</caption>
        <thead>
          <tr className="border-b border-line text-[0.7rem] font-bold tracking-[0.14em] text-ink-soft uppercase">
            <th className="px-4 py-3 pr-3 font-bold">Email</th>
            <th className="py-3 pr-4 font-bold">Rol</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.email} className="border-b border-line/80 last:border-b-0">
              <td className="px-4 py-3 pr-3 font-medium">{item.email}</td>
              <td className="py-3 pr-4 text-sm text-ink-soft">{roleLabel(item.rol)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
