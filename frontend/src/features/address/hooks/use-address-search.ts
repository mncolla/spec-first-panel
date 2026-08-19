import { useEffect, useState } from 'react'
import { searchAddresses } from '../services/nominatim.ts'
import type { AddressSuggestion } from '../types.ts'

export type AddressSearchStatus = 'idle' | 'loading' | 'empty' | 'error'

const DEBOUNCE_MS = 300

export function useAddressSearch(query: string) {
  const [results, setResults] = useState<AddressSuggestion[]>([])
  const [status, setStatus] = useState<AddressSearchStatus>('idle')

  useEffect(() => {
    const trimmed = query.trim()
    if (trimmed.length < 3) {
      setResults([])
      setStatus('idle')
      return
    }

    const controller = new AbortController()
    const timer = window.setTimeout(() => {
      setStatus('loading')
      void searchAddresses(trimmed, controller.signal)
        .then((items) => {
          setResults(items)
          setStatus(items.length === 0 ? 'empty' : 'idle')
        })
        .catch((error: unknown) => {
          if (isAbortError(error)) return
          setResults([])
          setStatus('error')
        })
    }, DEBOUNCE_MS)

    return () => {
      window.clearTimeout(timer)
      controller.abort()
    }
  }, [query])

  return { results, status }
}

function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError'
}
