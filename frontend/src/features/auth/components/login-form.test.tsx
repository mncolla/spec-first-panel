import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LoginForm } from './login-form.tsx'

describe('LoginForm', () => {
  it('muestra errores si se envía vacío', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<LoginForm pending={false} onSubmit={onSubmit} />)
    await user.click(screen.getByRole('button', { name: 'Ingresar' }))
    expect(screen.getByText('El email es obligatorio.')).toBeInTheDocument()
    expect(screen.getByText('La clave es obligatoria.')).toBeInTheDocument()
    expect(onSubmit).not.toHaveBeenCalled()
  })
})
