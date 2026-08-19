import type { ReactNode } from 'react'
import { Link } from 'wouter'
import { SessionMenu } from '../features/auth/components/session-menu.tsx'
import { useLogout } from '../features/auth/hooks/use-logout.ts'
import { useSession } from '../features/auth/hooks/use-session.ts'

export function Shell({ children }: { children: ReactNode }) {
  const session = useSession()
  const logout = useLogout()
  const operator = session.data

  return (
    <div className="min-h-dvh">
      <header className="border-b border-ink/10 bg-sheet">
        <div className="mx-auto flex max-w-6xl items-center gap-3 px-4 py-3 md:px-8">
          <span className="ochava-mark" aria-hidden="true" />
          <Link href="/" className="font-display text-lg font-bold tracking-tight text-ink">
            Lebane
          </Link>
          <span className="text-[0.65rem] font-bold tracking-[0.22em] text-ink-soft uppercase">
            CABA
          </span>
          <div className="ml-auto">
            {operator ? (
              <SessionMenu
                email={operator.email}
                rol={operator.rol}
                logoutPending={logout.isPending}
                onLogout={() => logout.mutate()}
              />
            ) : null}
          </div>
        </div>
      </header>
      {children}
    </div>
  )
}
