import { Redirect } from 'wouter'
import { isUnauthorizedError } from '../../../lib/api.ts'
import { useLogin } from '../hooks/use-login.ts'
import { useSessionToken } from '../hooks/use-session-token.ts'
import { LoginForm } from './login-form.tsx'

function loginErrorMessage(error: unknown): string {
  if (isUnauthorizedError(error)) {
    return 'Email o clave incorrectos.'
  }
  return 'No se pudo ingresar. Comprobá que la API esté en marcha.'
}

export function LoginPage() {
  const token = useSessionToken()
  const login = useLogin()

  if (token) {
    return <Redirect to="/" />
  }

  const apiError = login.isError ? loginErrorMessage(login.error) : undefined

  return (
    <div className="min-h-dvh">
      <header className="border-b border-ink/10 bg-sheet">
        <div className="mx-auto flex max-w-6xl items-center gap-3 px-4 py-3 md:px-8">
          <span className="ochava-mark" aria-hidden="true" />
          <span className="font-display text-lg font-bold tracking-tight text-ink">Lebane</span>
          <span className="text-[0.65rem] font-bold tracking-[0.22em] text-ink-soft uppercase">
            CABA
          </span>
        </div>
      </header>
      <main className="mx-auto flex max-w-md flex-col gap-6 px-4 py-16 md:px-0">
        <div>
          <h1 className="font-display text-4xl font-extrabold tracking-tight text-ink">
            Ingresar
          </h1>
          <p className="mt-1 text-sm text-ink-soft">
            Panel interno. Inventario de departamentos.
          </p>
        </div>
        <div className="sheet ochava p-6 md:p-8">
          <LoginForm
            pending={login.isPending}
            apiError={apiError}
            onSubmit={(body) => login.mutate(body)}
          />
        </div>
      </main>
    </div>
  )
}
