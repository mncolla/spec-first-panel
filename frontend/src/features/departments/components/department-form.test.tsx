import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { DepartmentForm } from './department-form.tsx'

vi.mock('../../address/services/nominatim.ts', () => ({
  searchAddresses: vi.fn().mockResolvedValue([]),
}))

describe('DepartmentForm', () => {
  it('no deja adjuntar más de 5 fotos', async () => {
    const user = userEvent.setup()
    render(
      <DepartmentForm
        submitLabel="Crear departamento"
        pending={false}
        onSubmit={() => undefined}
      />,
    )
    const files = Array.from(
      { length: 6 },
      (_, index) => new File([`img-${index}`], `foto-${index}.png`, { type: 'image/png' }),
    )
    await user.upload(screen.getByLabelText('Adjuntar fotos'), files)
    await waitFor(() => {
      expect(screen.getAllByRole('button', { name: 'Quitar' })).toHaveLength(5)
    })
    expect(screen.getByRole('alert')).toHaveTextContent('Como máximo 5 fotos.')
    expect(screen.getByLabelText('Adjuntar fotos')).toBeDisabled()
  })

  it('muestra errores si se envía vacío', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(
      <DepartmentForm submitLabel="Crear departamento" pending={false} onSubmit={onSubmit} />,
    )
    await user.click(screen.getByRole('button', { name: 'Crear departamento' }))
    expect(screen.getByText('El título debe tener al menos 3 caracteres.')).toBeInTheDocument()
    expect(screen.getByText('Elegí una dirección de la lista.')).toBeInTheDocument()
    expect(screen.getByText('El precio debe ser mayor a 0.')).toBeInTheDocument()
    expect(screen.getByText('Los m² deben ser mayores a 0.')).toBeInTheDocument()
    expect(onSubmit).not.toHaveBeenCalled()
  })
})
