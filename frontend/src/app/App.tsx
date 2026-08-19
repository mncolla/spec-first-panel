import { Providers } from './providers'
import { AppRouter } from './router'
import { Shell } from './shell.tsx'

export function App() {
  return (
    <Providers>
      <Shell>
        <AppRouter />
      </Shell>
    </Providers>
  )
}
