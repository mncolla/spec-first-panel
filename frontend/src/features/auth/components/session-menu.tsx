import { ChevronDownIcon } from 'lucide-react'
import { Link } from 'wouter'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../../../components/ui/dropdown-menu.tsx'
import { roleLabel } from '../role-label.ts'
import type { OperatorRole } from '../types.ts'

type Props = {
  email: string
  rol: OperatorRole
  logoutPending: boolean
  onLogout: () => void
}

export function SessionMenu({ email, rol, logoutPending, onLogout }: Props) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="btn-ghost gap-2" aria-label={`Cuenta de ${email}`}>
        <span className="text-ink">{email}</span>
        <span className="hidden text-ink-soft sm:inline">
          <span className="mx-1 text-line" aria-hidden="true">
            ·
          </span>
          {roleLabel(rol)}
        </span>
        <ChevronDownIcon className="size-4 text-ink-soft" aria-hidden="true" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {rol === 'admin' ? (
          <DropdownMenuItem asChild>
            <Link href="/operadores">Operadores</Link>
          </DropdownMenuItem>
        ) : null}
        <DropdownMenuItem
          variant="destructive"
          disabled={logoutPending}
          onSelect={() => onLogout()}
        >
          Cerrar sesión
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
