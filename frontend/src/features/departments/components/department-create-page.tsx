import { Link, useLocation } from 'wouter'
import { useCreateDepartment } from '../hooks/use-department-mutations.ts'
import { mapApiError } from '../map-api-error.ts'
import { DepartmentForm } from './department-form.tsx'

export function DepartmentCreatePage() {
  const [, setLocation] = useLocation()
  const mutation = useCreateDepartment()
  const mapped = mutation.isError ? mapApiError(mutation.error) : undefined

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6 px-4 py-8 md:px-8">
      <header>
        <h1 className="font-display text-4xl font-extrabold tracking-tight text-ink">
          Alta de departamento
        </h1>
        <p className="mt-1 text-sm text-ink-soft">
          Completá los datos. La dirección sale de OpenStreetMap.
        </p>
        <Link href="/" className="mt-3 inline-block text-sm text-bloom underline-offset-4 hover:underline">
          Volver al inventario
        </Link>
      </header>
      <DepartmentForm
        submitLabel="Crear departamento"
        pending={mutation.isPending}
        apiError={mapped?.message}
        apiFieldErrors={mapped?.fields}
        onSubmit={(body) => {
          mutation.mutate(body, {
            onSuccess: (created) => setLocation(`/departamentos/${created.id}`),
          })
        }}
      />
    </div>
  )
}
