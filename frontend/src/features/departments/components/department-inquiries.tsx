import type { ReactNode } from 'react'
import { formatInquiryDate } from '../format.ts'
import type { InquiryDetail } from '../types.ts'

type Props = {
  consultas: InquiryDetail[]
  children?: ReactNode
}

export function DepartmentInquiries({ consultas, children }: Props) {
  return (
    <section>
      <h2 className="font-display text-xl font-bold">Consultas</h2>
      {consultas.length === 0 ? (
        <p className="mt-2 text-sm text-ink-soft">Nadie consultó este departamento todavía.</p>
      ) : (
        <ul className="sheet mt-3 divide-y divide-line">
          {consultas.map((consulta, index) => (
            <li key={`${consulta.email}-${consulta.fecha}-${index}`} className="px-4 py-3">
              <p className="font-medium">{consulta.nombre}</p>
              <p className="text-sm text-ink-soft">
                {consulta.email} · {formatInquiryDate(consulta.fecha)}
              </p>
              <p className="mt-1 text-sm">{consulta.mensaje}</p>
            </li>
          ))}
        </ul>
      )}
      {children}
    </section>
  )
}
