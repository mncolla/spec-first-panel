import { searchAddresses } from './nominatim.ts'

describe('searchAddresses', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => [
          {
            place_id: 99,
            display_name: 'Calle Falsa 123, CABA',
            lat: '-34.6',
            lon: '-58.4',
          },
        ],
      }),
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('arma la query de Nominatim sin API key y con email de contacto', async () => {
    vi.stubEnv('VITE_NOMINATIM_CONTACT', 'lebane@example.com')
    const results = await searchAddresses('Santa Fe 3500')
    expect(results).toEqual([
      { id: '99', label: 'Calle Falsa 123, CABA', lat: -34.6, lng: -58.4 },
    ])
    const called = vi.mocked(fetch).mock.calls[0]?.[0]
    expect(called).toBeInstanceOf(URL)
    const url = called as URL
    expect(url.origin).toBe('https://nominatim.openstreetmap.org')
    expect(url.searchParams.get('q')).toBe('Santa Fe 3500')
    expect(url.searchParams.get('email')).toBe('lebane@example.com')
    expect(url.searchParams.get('countrycodes')).toBe('ar')
  })
})
