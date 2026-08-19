import { useState } from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AddressAutocomplete } from './address-autocomplete.tsx'
import { searchAddresses } from '../services/nominatim.ts'
import type { AddressSuggestion } from '../types.ts'

vi.mock('../services/nominatim.ts', () => ({
  searchAddresses: vi.fn(),
}))

const mockedSearch = vi.mocked(searchAddresses)

function Harness({
  initial = '',
  onSelect,
}: {
  initial?: string
  onSelect?: (item: AddressSuggestion) => void
}) {
  const [value, setValue] = useState(initial)
  return (
    <AddressAutocomplete
      value={value}
      onValueChange={setValue}
      onSelect={(item) => {
        setValue(item.label)
        onSelect?.(item)
      }}
    />
  )
}

describe('AddressAutocomplete', () => {
  beforeEach(() => {
    mockedSearch.mockReset()
  })

  it('muestra sugerencias y notifica la selección', async () => {
    mockedSearch.mockResolvedValue([
      {
        id: '1',
        label: 'Av. Santa Fe 3500, Palermo, CABA',
        lat: -34.588,
        lng: -58.411,
      },
    ])
    const onSelect = vi.fn()
    const user = userEvent.setup()
    render(<Harness onSelect={onSelect} />)

    await user.type(screen.getByRole('combobox'), 'Santa Fe')
    expect(
      await screen.findByRole('option', { name: /Santa Fe 3500/ }),
    ).toBeInTheDocument()
    await user.click(screen.getByRole('option', { name: /Santa Fe 3500/ }))
    expect(onSelect).toHaveBeenCalledWith({
      id: '1',
      label: 'Av. Santa Fe 3500, Palermo, CABA',
      lat: -34.588,
      lng: -58.411,
    })
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument()
  })

  it('no busca al montar con una dirección ya confirmada', async () => {
    mockedSearch.mockResolvedValue([
      {
        id: '1',
        label: 'Av. Santa Fe 3500, Palermo, CABA',
        lat: -34.588,
        lng: -58.411,
      },
    ])
    render(<Harness initial="Av. Santa Fe 3500, Palermo, CABA" />)
    await new Promise((resolve) => setTimeout(resolve, 400))
    expect(mockedSearch).not.toHaveBeenCalled()
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument()
  })

  it('muestra error si Nominatim falla', async () => {
    mockedSearch.mockRejectedValue(new Error('network'))
    const user = userEvent.setup()
    render(<Harness />)
    await user.type(screen.getByRole('combobox'), 'Libertador')
    expect(await screen.findByRole('alert')).toHaveTextContent(
      'No se pudo buscar la dirección. Probá de nuevo.',
    )
  })

  it('no busca con menos de 3 caracteres', async () => {
    const user = userEvent.setup()
    render(<Harness />)
    await user.type(screen.getByRole('combobox'), 'Sa')
    await waitFor(() => {
      expect(mockedSearch).not.toHaveBeenCalled()
    })
  })
})
