import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Router } from 'wouter'
import { memoryLocation } from 'wouter/memory-location'
import { ApiError } from '../../../lib/api.ts'
import { createInquiry, getDepartment } from '../services/departments.ts'
import type { DepartmentDetail } from '../types.ts'
import { DepartmentDetailPage } from './department-detail-page.tsx'

vi.mock('../services/departments.ts', () => ({
  getDepartment: vi.fn(),
  listDepartments: vi.fn(),
  createDepartment: vi.fn(),
  updateDepartment: vi.fn(),
  createInquiry: vi.fn(),
}))

const mockedGet = vi.mocked(getDepartment)
const mockedCreateInquiry = vi.mocked(createInquiry)

const detail: DepartmentDetail = {
  id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  titulo: '3 ambientes en Palermo',
  descripcion: 'Luminoso',
  precio: 180000,
  moneda: 'USD',
  metros_cuadrados: 72.5,
  direccion: 'Av. Santa Fe 3500, Palermo, CABA',
  lat: -34.588,
  lng: -58.411,
  disponible: true,
  imagenes: ['http://img.example/a.jpg'],
  consultas: [
    {
      nombre: 'Ana Pérez',
      email: 'ana@example.com',
      mensaje: '¿Sigue disponible?',
      fecha: '2026-08-18T12:00:00Z',
    },
  ],
  created_at: '2026-08-01T12:00:00Z',
}

function renderDetail(path: string) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  const { hook } = memoryLocation({ path })
  return render(
    <QueryClientProvider client={client}>
      <Router hook={hook}>
        <DepartmentDetailPage />
      </Router>
    </QueryClientProvider>,
  )
}

describe('DepartmentDetailPage', () => {
  beforeEach(() => {
    mockedGet.mockReset()
    mockedCreateInquiry.mockReset()
  })

  it('muestra título, precio y consultas del detalle', async () => {
    mockedGet.mockResolvedValue(detail)
    renderDetail(`/departamentos/${detail.id}`)
    expect(
      await screen.findByRole('heading', { name: '3 ambientes en Palermo' }),
    ).toBeInTheDocument()
    expect(screen.getByText('USD 180.000')).toBeInTheDocument()
    expect(screen.getByText('Ana Pérez')).toBeInTheDocument()
    expect(screen.getByText(/¿Sigue disponible?/)).toBeInTheDocument()
    expect(screen.getByDisplayValue('3 ambientes en Palermo')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Registrar nueva consulta' })).toBeInTheDocument()
    expect(screen.queryByLabelText('Nombre')).not.toBeInTheDocument()
  })

  it('registra una consulta y la muestra en la lista', async () => {
    const user = userEvent.setup()
    const created = {
      nombre: 'Dana López',
      email: 'dana@example.com',
      mensaje: 'Quiero visitar',
      fecha: '2026-08-19T14:42:00Z',
    }
    mockedGet
      .mockResolvedValueOnce(detail)
      .mockResolvedValue({
        ...detail,
        consultas: [created, ...detail.consultas],
      })
    mockedCreateInquiry.mockResolvedValue(created)
    renderDetail(`/departamentos/${detail.id}`)
    await screen.findByRole('button', { name: 'Registrar nueva consulta' })
    await user.click(screen.getByRole('button', { name: 'Registrar nueva consulta' }))
    await user.type(screen.getByLabelText('Nombre'), created.nombre)
    await user.type(screen.getByLabelText('Email'), created.email)
    await user.type(screen.getByLabelText('Mensaje'), created.mensaje)
    await user.click(screen.getByRole('button', { name: 'Enviar' }))
    expect(await screen.findByText('Dana López')).toBeInTheDocument()
    expect(mockedCreateInquiry).toHaveBeenCalledWith(detail.id, {
      nombre: created.nombre,
      email: created.email,
      mensaje: created.mensaje,
    })
    expect(screen.getByRole('button', { name: 'Registrar nueva consulta' })).toBeInTheDocument()
    expect(screen.queryByLabelText('Mensaje')).not.toBeInTheDocument()
  })

  it('no muestra el formulario si el departamento no está disponible', async () => {
    mockedGet.mockResolvedValue({ ...detail, disponible: false })
    renderDetail(`/departamentos/${detail.id}`)
    expect(
      await screen.findByRole('heading', { name: '3 ambientes en Palermo' }),
    ).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Registrar nueva consulta' })).not.toBeInTheDocument()
  })

  it('muestra not found si el API responde 404', async () => {
    mockedGet.mockRejectedValue(new ApiError(404, 'Department not found'))
    renderDetail('/departamentos/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')
    expect(
      await screen.findByRole('heading', { name: 'No encontramos ese departamento' }),
    ).toBeInTheDocument()
  })
})
