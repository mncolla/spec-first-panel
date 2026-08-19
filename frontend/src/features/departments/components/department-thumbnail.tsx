import { useState } from 'react'

type Props = {
  src: string | null
  alt: string
}

export function DepartmentThumbnail({ src, alt }: Props) {
  const [failed, setFailed] = useState(false)
  const showPlaceholder = !src || failed

  if (showPlaceholder) {
    return (
      <span
        className="ochava flex h-20 w-14 shrink-0 items-end justify-center bg-ink text-panel"
        aria-hidden={!src}
        role={src ? undefined : 'img'}
        aria-label={src ? undefined : 'Sin foto'}
      >
        <svg viewBox="0 0 56 80" className="h-20 w-14" aria-hidden="true">
          <rect width="56" height="80" fill="#171c1a" />
          <rect x="10" y="12" width="12" height="14" fill="#dde3de" opacity="0.4" />
          <rect x="26" y="12" width="12" height="14" fill="#dde3de" opacity="0.22" />
          <rect x="10" y="32" width="12" height="14" fill="#dde3de" opacity="0.22" />
          <rect x="26" y="32" width="12" height="14" fill="#dde3de" opacity="0.4" />
          <rect x="18" y="56" width="20" height="24" fill="#c43d5a" />
        </svg>
        <span className="sr-only">{alt}</span>
      </span>
    )
  }

  return (
    <img
      src={src}
      alt={alt}
      onError={() => setFailed(true)}
      className="ochava h-20 w-14 shrink-0 bg-panel object-cover"
    />
  )
}
