import { MutationCache, QueryCache, QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Router } from 'wouter'
import { memoryLocation } from 'wouter/memory-location'
import { ApiError } from '../lib/api.ts'
import { clearTokenIfUnauthorized } from '../features/auth/handle-unauthorized.ts'
import { createSession, getSession } from '../features/auth/services/session.ts'
import { setSessionToken } from '../features/auth/token.ts'
import { listDepartments } from '../features/departments/services/departments.ts'
import { AppRouter } from './router.tsx'

vi.mock('../features/departments/services/departments.ts', () => ({
  listDepartments: vi.fn(),
}))

vi.mock('../features/auth/services/session.ts', () => ({
  createSession: vi.fn(),
  getSession: vi.fn(),
  deleteSession: vi.fn(),
}))

const emptyList = {
  items: [],
  pagina: 1,
  cantidad: 20,
  total: 0,
}

function renderRouter(path: string) {
  const client = new QueryClient({
    queryCache: new QueryCache({ onError: clearTokenIfUnauthorized }),
    mutationCache: new MutationCache({ onError: clearTokenIfUnauthorized }),
    defaultOptions: { queries: { retry: false } },
  })
  const { hook } = memoryLocation({ path })
  return render(
    <QueryClientProvider client={client}>
      <Router hook={hook}>
        <AppRouter />
      </Router>
    </QueryClientProvider>,
  )
}

describe('AppRouter', () => {
  it('muestra el ingreso si no hay sesión', async () => {
    renderRouter('/')
    expect(await screen.findByRole('heading', { name: 'Ingresar' })).toBeInTheDocument()
  })

  it('llega al inventario después de ingresar', async () => {
    vi.mocked(createSession).mockResolvedValue({
      email: 'admin@lebane.local',
      rol: 'admin',
      token: 'test-token',
    })
    vi.mocked(getSession).mockResolvedValue({
      email: 'admin@lebane.local',
      rol: 'admin',
    })
    vi.mocked(listDepartments).mockResolvedValue(emptyList)

    const user = userEvent.setup()
    renderRouter('/ingresar')
    await user.type(screen.getByLabelText('Email'), 'admin@lebane.local')
    await user.type(screen.getByLabelText('Clave'), 'lebanelebane')
    await user.click(screen.getByRole('button', { name: 'Ingresar' }))

    expect(await screen.findByRole('heading', { name: 'Inventario' })).toBeInTheDocument()
    expect(screen.getByText('admin@lebane.local')).toBeInTheDocument()
    expect(screen.getByText('Admin')).toBeInTheDocument()
  })

  it('vuelve al ingreso si un pedido de departamentos responde 401', async () => {
    setSessionToken('stale-token')
    vi.mocked(getSession).mockResolvedValue({
      email: 'admin@lebane.local',
      rol: 'admin',
    })
    vi.mocked(listDepartments).mockRejectedValue(
      new ApiError(401, 'Invalid credentials'),
    )
    renderRouter('/')
    expect(await screen.findByRole('heading', { name: 'Ingresar' })).toBeInTheDocument()
  })
})
