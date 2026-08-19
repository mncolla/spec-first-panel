import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { Router } from 'wouter'
import { memoryLocation } from 'wouter/memory-location'
import { DepartmentListPage } from './department-list-page.tsx'
import { listDepartments } from '../services/departments.ts'

vi.mock('../services/departments.ts', () => ({
  listDepartments: vi.fn(),
}))

const mockedList = vi.mocked(listDepartments)

function renderPage() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  const { hook } = memoryLocation({ path: '/' })
  return render(
    <QueryClientProvider client={client}>
      <Router hook={hook}>
        <DepartmentListPage />
      </Router>
    </QueryClientProvider>,
  )
}

describe('DepartmentListPage', () => {
  it('muestra los departamentos que devuelve la query', async () => {
    mockedList.mockResolvedValue({
      items: [
        {
          id: 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
          titulo: 'PH en Boedo',
          precio: 90000,
          moneda: 'USD',
          metros_cuadrados: 48,
          direccion: 'Av. San Juan 2700',
          disponible: true,
          imagen_principal: 'http://broken.example/x.jpg',
          total_imagenes: 1,
          total_consultas: 4,
        },
      ],
      pagina: 1,
      cantidad: 20,
      total: 1,
    })

    renderPage()
    expect(await screen.findByText('PH en Boedo')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Agregar Departamento' })).toHaveAttribute(
      'href',
      '/departamentos/nuevo',
    )
  })

  it('muestra inventario vacío si no hay departamentos', async () => {
    mockedList.mockResolvedValue({
      items: [],
      pagina: 1,
      cantidad: 20,
      total: 0,
    })
    renderPage()
    expect(
      await screen.findByText('Todavía no hay departamentos en el inventario.'),
    ).toBeInTheDocument()
  })

  it('muestra error si la API falla', async () => {
    mockedList.mockRejectedValue(new Error('API 500'))
    renderPage()
    expect(
      await screen.findByText('No se pudo cargar el inventario.'),
    ).toBeInTheDocument()
  })
})
