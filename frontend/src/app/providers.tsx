import { MutationCache, QueryCache, QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, type ReactNode } from 'react'
import { clearTokenIfUnauthorized } from '../features/auth/handle-unauthorized.ts'

function createAppQueryClient() {
  return new QueryClient({
    queryCache: new QueryCache({
      onError: clearTokenIfUnauthorized,
    }),
    mutationCache: new MutationCache({
      onError: clearTokenIfUnauthorized,
    }),
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        retry: 1,
      },
    },
  })
}

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(createAppQueryClient)

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
}
