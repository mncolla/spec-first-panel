import type { Currency } from './types.ts'

const priceFormat = new Intl.NumberFormat('es-AR', {
  maximumFractionDigits: 0,
})

export function formatPrice(precio: number, moneda: Currency): string {
  const amount = priceFormat.format(precio)
  return moneda === 'USD' ? `USD ${amount}` : `ARS ${amount}`
}

export function formatInquiryDate(iso: string): string {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return iso
  return new Intl.DateTimeFormat('es-AR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(date)
}
