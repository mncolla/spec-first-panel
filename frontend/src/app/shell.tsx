import type { ReactNode } from 'react'
import { Link } from 'wouter'

export function Shell({ children }: { children: ReactNode }) {
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
        </div>
      </header>
      {children}
    </div>
  )
}
