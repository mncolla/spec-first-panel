import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Router } from 'wouter'
import { memoryLocation } from 'wouter/memory-location'
import { SessionMenu } from './session-menu.tsx'

function renderMenu(rol: 'admin' | 'agente') {
  const { hook } = memoryLocation({ path: '/' })
  const onLogout = vi.fn()
  const user = userEvent.setup()
  render(
    <Router hook={hook}>
      <SessionMenu
        email="admin@lebane.local"
        rol={rol}
        logoutPending={false}
        onLogout={onLogout}
      />
    </Router>,
  )
  return { user, onLogout }
}

describe('SessionMenu', () => {
  it('el admin ve Operadores y puede cerrar sesión', async () => {
    const { user, onLogout } = renderMenu('admin')
    await user.click(screen.getByRole('button', { name: 'Cuenta de admin@lebane.local' }))
    expect(await screen.findByRole('menuitem', { name: 'Operadores' })).toHaveAttribute(
      'href',
      '/operadores',
    )
    await user.click(screen.getByRole('menuitem', { name: 'Cerrar sesión' }))
    expect(onLogout).toHaveBeenCalledOnce()
  })

  it('un agente no ve Operadores', async () => {
    const { user } = renderMenu('agente')
    await user.click(screen.getByRole('button', { name: 'Cuenta de admin@lebane.local' }))
    expect(await screen.findByRole('menuitem', { name: 'Cerrar sesión' })).toBeInTheDocument()
    expect(screen.queryByRole('menuitem', { name: 'Operadores' })).not.toBeInTheDocument()
  })
})
