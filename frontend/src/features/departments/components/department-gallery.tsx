import { useState } from 'react'
import { DepartmentThumbnail } from './department-thumbnail.tsx'

type Props = {
  urls: string[]
  title: string
}

export function DepartmentGallery({ urls, title }: Props) {
  if (urls.length === 0) {
    return (
      <div className="sheet px-4 py-8 text-center text-sm text-ink-soft">
        Este departamento todavía no tiene fotos.
      </div>
    )
  }

  return (
    <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-5">
      {urls.map((url, index) => (
        <li key={`${url}-${index}`}>
          <GalleryShot src={url} alt={`${title}, foto ${index + 1}`} />
        </li>
      ))}
    </ul>
  )
}

function GalleryShot({ src, alt }: { src: string; alt: string }) {
  const [failed, setFailed] = useState(false)
  if (failed) {
    return <DepartmentThumbnail src={null} alt={alt} />
  }
  return (
    <img
      src={src}
      alt={alt}
      onError={() => setFailed(true)}
      className="ochava h-40 w-full bg-panel object-cover"
    />
  )
}
