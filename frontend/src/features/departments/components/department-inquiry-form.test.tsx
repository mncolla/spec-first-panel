import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { DepartmentInquiryForm } from './department-inquiry-form.tsx'

describe('DepartmentInquiryForm', () => {
  it('muestra errores si se envía vacío', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<DepartmentInquiryForm pending={false} onSubmit={onSubmit} />)
    await user.click(screen.getByRole('button', { name: 'Enviar' }))
    expect(screen.getByText('El nombre es obligatorio.')).toBeInTheDocument()
    expect(screen.getByText('El email es obligatorio.')).toBeInTheDocument()
    expect(screen.getByText('El mensaje es obligatorio.')).toBeInTheDocument()
    expect(onSubmit).not.toHaveBeenCalled()
  })
})
