import { useState } from 'react'
import type { InquiryWrite } from '../types.ts'
import { DepartmentInquiryForm } from './department-inquiry-form.tsx'

type Props = {
  pending: boolean
  apiError?: string
  apiFieldErrors?: Record<string, string>
  onSubmit: (body: InquiryWrite) => void | Promise<void>
}

export function DepartmentInquiryRecorder({
  pending,
  apiError,
  apiFieldErrors,
  onSubmit,
}: Props) {
  const [open, setOpen] = useState(false)

  if (!open) {
    return (
      <button
        type="button"
        className="btn-primary mt-4 justify-self-start"
        onClick={() => setOpen(true)}
      >
        Registrar nueva consulta
      </button>
    )
  }

  return (
    <DepartmentInquiryForm
      pending={pending}
      apiError={apiError}
      apiFieldErrors={apiFieldErrors}
      onCancel={() => setOpen(false)}
      onSubmit={async (body) => {
        await onSubmit(body)
        setOpen(false)
      }}
    />
  )
}
