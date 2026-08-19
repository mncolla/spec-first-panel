import type { AddressSuggestion } from '../types.ts'

const NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'
const MIN_INTERVAL_MS = 1000

let lastStartedAt = 0
let chain: Promise<void> = Promise.resolve()

type NominatimHit = {
  place_id: number
  display_name: string
  lat: string
  lon: string
}

export async function searchAddresses(
  query: string,
  signal?: AbortSignal,
): Promise<AddressSuggestion[]> {
  const trimmed = query.trim()
  if (trimmed.length < 3) return []

  await enqueueRateLimit(signal)

  const url = new URL(NOMINATIM_URL)
  url.searchParams.set('q', trimmed)
  url.searchParams.set('format', 'jsonv2')
  url.searchParams.set('limit', '5')
  url.searchParams.set('addressdetails', '0')
  url.searchParams.set('countrycodes', 'ar')
  url.searchParams.set('accept-language', 'es')
  const contact = import.meta.env.VITE_NOMINATIM_CONTACT
  if (typeof contact === 'string' && contact.trim()) {
    url.searchParams.set('email', contact.trim())
  }

  const response = await fetch(url, {
    signal,
    headers: { Accept: 'application/json' },
  })
  if (!response.ok) {
    throw new Error(`Nominatim ${response.status}`)
  }
  const payload = (await response.json()) as NominatimHit[]
  return payload.map((hit) => ({
    id: String(hit.place_id),
    label: hit.display_name,
    lat: Number(hit.lat),
    lng: Number(hit.lon),
  }))
}

function enqueueRateLimit(signal?: AbortSignal): Promise<void> {
  const pending = chain.then(() => waitForSlot(signal))
  chain = pending.catch(() => undefined)
  return pending
}

async function waitForSlot(signal?: AbortSignal): Promise<void> {
  const wait = MIN_INTERVAL_MS - (Date.now() - lastStartedAt)
  if (wait > 0) {
    await sleep(wait, signal)
  }
  lastStartedAt = Date.now()
}

function sleep(ms: number, signal?: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) {
      reject(signal.reason ?? new DOMException('Aborted', 'AbortError'))
      return
    }
    const timer = window.setTimeout(resolve, ms)
    signal?.addEventListener(
      'abort',
      () => {
        window.clearTimeout(timer)
        reject(signal.reason ?? new DOMException('Aborted', 'AbortError'))
      },
      { once: true },
    )
  })
}
