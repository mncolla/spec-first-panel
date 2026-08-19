import { Link, useRoute } from 'wouter'
import type { ReactNode } from 'react'
import { isNotFoundError } from '../../../lib/api.ts'
import { formatPrice } from '../format.ts'
import { useDepartment } from '../hooks/use-department.ts'
import { useCreateInquiry, useUpdateDepartment } from '../hooks/use-department-mutations.ts'
import { mapApiError } from '../map-api-error.ts'
import type { DepartmentDetail } from '../types.ts'
import { DepartmentForm } from './department-form.tsx'
import { DepartmentGallery } from './department-gallery.tsx'
import { DepartmentInquiries } from './department-inquiries.tsx'
import { DepartmentInquiryRecorder } from './department-inquiry-recorder.tsx'

export function DepartmentDetailPage() {
  const [, params] = useRoute('/departamentos/:id')
  const id = params?.id
  const query = useDepartment(id)

  if (query.isPending) {
    return (
      <PageFrame>
        <p className="text-ink-soft">Cargando ficha…</p>
      </PageFrame>
    )
  }

  if (isNotFoundError(query.error) || !id) {
    return (
      <PageFrame>
        <h1 className="font-display text-4xl font-extrabold tracking-tight">
          No encontramos ese departamento
        </h1>
        <p className="mt-2 text-sm text-ink-soft">Puede que el ID no exista o que se haya movido.</p>
        <Link href="/" className="mt-4 inline-block text-bloom underline-offset-4 hover:underline">
          Volver al inventario
        </Link>
      </PageFrame>
    )
  }

  if (query.isError || !query.data) {
    return (
      <PageFrame>
        <div role="alert" className="sheet px-4 py-4 text-danger">
          <p className="font-semibold">No se pudo cargar la ficha.</p>
          <button
            type="button"
            className="btn-ghost mt-3"
            onClick={() => void query.refetch()}
          >
            Reintentar
          </button>
        </div>
      </PageFrame>
    )
  }

  return <DepartmentDetailBody department={query.data} />
}

function DepartmentDetailBody({ department }: { department: DepartmentDetail }) {
  const mutation = useUpdateDepartment(department.id)
  const inquiryMutation = useCreateInquiry(department.id)
  const mapped = mutation.isError ? mapApiError(mutation.error) : undefined
  const inquiryMapped = inquiryMutation.isError ? mapApiError(inquiryMutation.error) : undefined
  const saved = mutation.data ?? department

  return (
    <PageFrame>
      <header>
        <h1 className="font-display text-4xl font-extrabold tracking-tight text-ink">
          {saved.titulo}
        </h1>
        <p className="mt-1 font-mono text-lg font-medium tabular-nums">
          {formatPrice(saved.precio, saved.moneda)}
        </p>
        <p className="mt-1 text-sm text-ink-soft">{saved.direccion}</p>
        <Link href="/" className="mt-3 inline-block text-sm text-bloom underline-offset-4 hover:underline">
          Volver al inventario
        </Link>
      </header>

      <DepartmentGallery urls={saved.imagenes} title={saved.titulo} />
      <DepartmentInquiries consultas={department.consultas}>
        {saved.disponible ? (
          <DepartmentInquiryRecorder
            pending={inquiryMutation.isPending}
            apiError={inquiryMapped?.message}
            apiFieldErrors={inquiryMapped?.fields}
            onSubmit={(body) => inquiryMutation.mutateAsync(body)}
          />
        ) : null}
      </DepartmentInquiries>

      <section>
        <h2 className="font-display text-xl font-bold">Editar</h2>
        <p className="mt-1 mb-4 text-sm text-ink-soft">
          Los cambios se guardan con PUT. Desmarcar disponible es la baja.
        </p>
        <DepartmentForm
          key={`${saved.id}-${saved.imagenes.join('|')}`}
          initial={saved}
          submitLabel="Guardar cambios"
          pending={mutation.isPending}
          apiError={mapped?.message}
          apiFieldErrors={mapped?.fields}
          onSubmit={(body) => mutation.mutate(body)}
        />
        {mutation.isSuccess ? (
          <p className="mt-3 text-sm text-shade">Cambios guardados.</p>
        ) : null}
      </section>
    </PageFrame>
  )
}

function PageFrame({ children }: { children: ReactNode }) {
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-8 px-4 py-8 md:px-8">{children}</div>
  )
}
