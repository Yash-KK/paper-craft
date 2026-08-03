import * as React from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { toast } from "sonner"

import { AuthStatus, useAuth } from "@/providers/auth-provider"
import { GeneratePaperForm } from "@/features/notebooks/generate-paper-form"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useNotebooks } from "@/hooks/use-notebooks"

export function GeneratePaperPage() {
  const { notebookId = "" } = useParams()
  const navigate = useNavigate()
  const { status, user } = useAuth()
  const authenticated = status === AuthStatus.Authenticated
  const { notebooks, loading, error } = useNotebooks(authenticated)
  const notebook = notebooks.find((item) => item.id === notebookId)
  const notebookPath = `/notebooks/${notebookId}`

  React.useEffect(() => {
    if (status === AuthStatus.Unauthenticated) navigate("/", { replace: true })
  }, [status, navigate])

  React.useEffect(() => {
    if (error) toast.error(error)
  }, [error])

  if (status === AuthStatus.Loading || !authenticated || loading) {
    return (
      <div className="mx-auto flex w-full max-w-4xl flex-col gap-6 px-4 py-6 sm:px-6">
        <div className="space-y-2">
          <Skeleton className="h-3 w-28" />
          <Skeleton className="h-8 w-56" />
          <Skeleton className="h-4 w-full max-w-md" />
        </div>
        <Skeleton className="h-24 w-full rounded-2xl" />
        <Skeleton className="h-64 w-full rounded-2xl" />
      </div>
    )
  }

  if (!notebook) {
    return (
      <div className="mx-auto flex w-full max-w-lg flex-1 flex-col items-center justify-center gap-4 px-4 py-16 text-center">
        <h1 className="font-heading text-xl font-semibold">Notebook not found</h1>
        <p className="text-sm text-muted-foreground">
          This notebook may have been deleted, or the list hasn&apos;t loaded yet.
        </p>
        <Button render={<Link to="/dashboard" />}>Back to dashboard</Button>
      </div>
    )
  }

  return (
    <GeneratePaperForm
      notebook={notebook}
      schoolName={user?.school_name ?? null}
      onCancel={() => navigate(notebookPath)}
      onGenerated={() => {
        toast.success("Paper generation started.")
        navigate(notebookPath)
      }}
    />
  )
}
