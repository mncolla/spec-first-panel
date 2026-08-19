import { render, screen } from '@testing-library/react'
import { Router } from 'wouter'
import { memoryLocation } from 'wouter/memory-location'
import { DepartmentTable } from './department-table.tsx'
import type { DepartmentListItem } from '../types.ts'

const item: DepartmentListItem = {
  id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  titulo: '3 ambientes en Palermo',
  precio: 180000,
  moneda: 'USD',
  metros_cuadrados: 72.5,
  direccion: 'Av. Santa Fe 3500, Palermo, CABA',
  disponible: true,
  imagen_principal: null,
  total_imagenes: 2,
  total_consultas: 3,
}

function renderTable(items: DepartmentListItem[] = [item]) {
  const { hook } = memoryLocation({ path: '/' })
  return render(
    <Router hook={hook}>
      <DepartmentTable items={items} />
    </Router>,
  )
}

describe('DepartmentTable', () => {
  it('renderiza los ítems del listado', () => {
    renderTable()
    expect(screen.getByText('3 ambientes en Palermo')).toBeInTheDocument()
    expect(screen.getByText(/USD 180/)).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
    expect(screen.getByText('3fa85f64')).toBeInTheDocument()
    expect(screen.getByText('Disponible')).toBeInTheDocument()
  })
})
