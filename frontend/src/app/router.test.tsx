import { MutationCache, QueryCache, QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Router } from 'wouter'
import { memoryLocation } from 'wouter/memory-location'
import { ApiError } from '../lib/api.ts'
import { clearTokenIfUnauthorized } from '../features/auth/handle-unauthorized.ts'
import { createSession, getSession } from '../features/auth/services/session.ts'
import { createOperator, listOperators } from '../features/auth/services/operators.ts'
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

vi.mock('../features/auth/services/operators.ts', () => ({
  createOperator: vi.fn(),
  listOperators: vi.fn(),
}))

const operatorList = {
  items: [{ email: 'admin@lebane.local', rol: 'admin' as const }],
}

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
    await user.click(screen.getByRole('button', { name: 'Cuenta de admin@lebane.local' }))
    expect(await screen.findByRole('menuitem', { name: 'Operadores' })).toHaveAttribute(
      'href',
      '/operadores',
    )
  })

  it('el admin ve la lista de operadores y el alta', async () => {
    setSessionToken('test-token')
    vi.mocked(getSession).mockResolvedValue({
      email: 'admin@lebane.local',
      rol: 'admin',
    })
    vi.mocked(listOperators).mockResolvedValue(operatorList)
    renderRouter('/operadores')
    expect(await screen.findByRole('heading', { name: 'Operadores' })).toBeInTheDocument()
    expect(await screen.findByRole('columnheader', { name: 'Email' })).toBeInTheDocument()
    expect(screen.getByRole('cell', { name: 'admin@lebane.local' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Alta de agente' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Crear agente' })).toBeInTheDocument()
  })

  it('el admin crea un agente y ve el email', async () => {
    setSessionToken('test-token')
    vi.mocked(getSession).mockResolvedValue({
      email: 'admin@lebane.local',
      rol: 'admin',
    })
    vi.mocked(listOperators).mockResolvedValue(operatorList)
    vi.mocked(createOperator).mockResolvedValue({
      email: 'agente@lebane.local',
      rol: 'agente',
    })
    const user = userEvent.setup()
    renderRouter('/operadores')
    await user.type(await screen.findByLabelText('Email'), 'agente@lebane.local')
    await user.type(screen.getByLabelText('Clave'), 'agentpass')
    await user.click(screen.getByRole('button', { name: 'Crear agente' }))
    expect(await screen.findByText('Agente creado: agente@lebane.local')).toBeInTheDocument()
  })

  it('un agente no ve el formulario de alta', async () => {
    setSessionToken('agent-token')
    vi.mocked(getSession).mockResolvedValue({
      email: 'agente@lebane.local',
      rol: 'agente',
    })
    vi.mocked(listDepartments).mockResolvedValue(emptyList)
    renderRouter('/')
    expect(await screen.findByRole('heading', { name: 'Inventario' })).toBeInTheDocument()
    const agent = userEvent.setup()
    await agent.click(
      await screen.findByRole('button', { name: 'Cuenta de agente@lebane.local' }),
    )
    expect(await screen.findByRole('menuitem', { name: 'Cerrar sesión' })).toBeInTheDocument()
    expect(screen.queryByRole('menuitem', { name: 'Operadores' })).not.toBeInTheDocument()

    renderRouter('/operadores')
    expect(
      await screen.findByRole('heading', { name: 'Solo el admin ve operadores' }),
    ).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Crear agente' })).not.toBeInTheDocument()
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
