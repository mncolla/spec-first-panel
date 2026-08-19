import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { Router } from 'wouter'
import { memoryLocation } from 'wouter/memory-location'
import { AppRouter } from './router.tsx'
import { listDepartments } from '../features/departments/services/departments.ts'

vi.mock('../features/departments/services/departments.ts', () => ({
  listDepartments: vi.fn(),
}))

describe('AppRouter', () => {
  it('renderiza el inventario en /', async () => {
    vi.mocked(listDepartments).mockResolvedValue({
      items: [],
      pagina: 1,
      cantidad: 20,
      total: 0,
    })
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    const { hook } = memoryLocation({ path: '/' })
    render(
      <QueryClientProvider client={client}>
        <Router hook={hook}>
          <AppRouter />
        </Router>
      </QueryClientProvider>,
    )
    expect(await screen.findByRole('heading', { name: 'Inventario' })).toBeInTheDocument()
  })
})
