import { fireEvent, render, screen } from '@testing-library/react'
import { DepartmentThumbnail } from './department-thumbnail.tsx'

describe('DepartmentThumbnail', () => {
  it('usa placeholder si la imagen falla', () => {
    render(<DepartmentThumbnail src="http://broken.example/x.jpg" alt="Foto de prueba" />)
    fireEvent.error(screen.getByRole('img', { name: 'Foto de prueba' }))
    expect(screen.getByText('Foto de prueba')).toBeInTheDocument()
  })
})
