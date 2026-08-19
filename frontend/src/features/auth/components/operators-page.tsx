import type { ReactNode } from 'react'
import { Link } from 'wouter'
import { isApiError, isForbiddenError } from '../../../lib/api.ts'
import { useCreateOperator } from '../hooks/use-create-operator.ts'
import { useOperators } from '../hooks/use-operators.ts'
import { useSession } from '../hooks/use-session.ts'
import { CreateAgentForm } from './create-agent-form.tsx'
import { OperatorTable } from './operator-table.tsx'

export function OperatorsPage() {
  const session = useSession()
  const isAdmin = session.data?.rol === 'admin'
  const list = useOperators(isAdmin)
  const create = useCreateOperator()

  if (session.isPending) {
    return (
      <PageFrame>
        <p className="text-ink-soft">Cargando sesión…</p>
      </PageFrame>
    )
  }

  if (!isAdmin) {
    return (
      <PageFrame>
        <h1 className="font-display text-4xl font-extrabold tracking-tight text-ink">
          Solo el admin ve operadores
        </h1>
        <p className="mt-1 text-sm text-ink-soft">
          Un agente inmobiliario usa el inventario; no da de alta operadores.
        </p>
        <Link href="/" className="mt-4 inline-block text-sm text-bloom underline-offset-4 hover:underline">
          Volver al inventario
        </Link>
      </PageFrame>
    )
  }

  return (
    <PageFrame>
      <header>
        <h1 className="font-display text-4xl font-extrabold tracking-tight text-ink md:text-[2.75rem]">
          Operadores
        </h1>
        <p className="mt-1 text-sm text-ink-soft">
          Un admin único. El resto son agentes del inventario.
        </p>
        <Link href="/" className="mt-3 inline-block text-sm text-bloom underline-offset-4 hover:underline">
          Volver al inventario
        </Link>
      </header>

      {list.isPending ? <p className="text-ink-soft">Cargando operadores…</p> : null}
      {list.isError ? (
        <div role="alert" className="sheet px-4 py-4 text-danger">
          <p className="font-semibold">No se pudieron cargar los operadores.</p>
          <p className="mt-1 text-sm">Comprobá que la API esté en marcha y reintentá.</p>
          <button type="button" onClick={() => void list.refetch()} className="btn-ghost mt-3">
            Reintentar
          </button>
        </div>
      ) : null}
      {list.data && list.data.items.length === 0 ? (
        <div className="sheet px-4 py-10 text-center">
          <p className="font-medium">Todavía no hay operadores.</p>
        </div>
      ) : null}
      {list.data && list.data.items.length > 0 ? <OperatorTable items={list.data.items} /> : null}

      <section>
        <h2 className="font-display text-xl font-bold">Alta de agente</h2>
        <p className="mt-1 mb-4 text-sm text-ink-soft">
          Email y clave. El rol queda en agente; no se puede crear otro admin.
        </p>
        <div className="sheet p-4">
          <CreateAgentForm
            key={create.data?.email ?? 'new'}
            pending={create.isPending}
            apiError={create.isError ? createAgentErrorMessage(create.error) : undefined}
            onSubmit={(body) => create.mutate(body)}
          />
        </div>
        {create.isSuccess ? (
          <p className="mt-3 text-sm text-shade" role="status">
            Agente creado: {create.data.email}
          </p>
        ) : null}
      </section>
    </PageFrame>
  )
}

function PageFrame({ children }: { children: ReactNode }) {
  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-8 md:px-8">{children}</div>
  )
}

function createAgentErrorMessage(error: unknown): string {
  if (isForbiddenError(error)) {
    return 'No tenés permiso para crear agentes.'
  }
  if (isApiError(error) && typeof error.detail === 'string') {
    if (error.detail.includes('already exists')) {
      return 'Ese email ya está en uso.'
    }
  }
  return 'No se pudo crear el agente. Comprobá que la API esté en marcha.'
}
