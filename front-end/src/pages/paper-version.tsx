import * as React from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { toast } from "sonner"

import { AuthStatus, useAuth } from "@/components/auth-provider"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { PaperVersionView, useNotebookPapers } from "@/features/question-papers"
import { useNotebooks } from "@/hooks/use-notebooks"

export function PaperVersionPage() {
  const {
    notebookId = "",
    paperId = "",
    versionNumber: versionNumberParam = "",
  } = useParams()
  const versionNumber = Number.parseInt(versionNumberParam, 10)
  const navigate = useNavigate()
  const { status } = useAuth()
  const authenticated = status === AuthStatus.Authenticated
  const { notebooks, loading, error } = useNotebooks(authenticated)
  const notebook = notebooks.find((item) => item.id === notebookId)
  const papersQuery = useNotebookPapers(
    notebookId,
    authenticated && Boolean(notebook)
  )
  const paper = papersQuery.data?.find((item) => item.id === paperId)
  const siblingVersions =
    paper?.versions.map((version) => version.version_number) ?? []

  React.useEffect(() => {
    if (status === AuthStatus.Unauthenticated) {
      navigate("/", { replace: true })
    }
  }, [status, navigate])

  React.useEffect(() => {
    if (error) toast.error(error)
  }, [error])

  if (
    status === AuthStatus.Loading ||
    !authenticated ||
    loading ||
    Number.isNaN(versionNumber)
  ) {
    return (
      <div className="mx-auto flex w-full max-w-4xl flex-col gap-4 px-4 py-6 sm:px-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-5 w-40" />
        <Skeleton className="h-96 w-full rounded-2xl" />
      </div>
    )
  }

  if (!notebook) {
    return (
      <div className="mx-auto flex w-full max-w-lg flex-1 flex-col items-center justify-center gap-4 px-4 py-16 text-center">
        <h1 className="font-heading text-xl font-semibold">Notebook not found</h1>
        <Button render={<Link to="/dashboard" />}>Back to dashboard</Button>
      </div>
    )
  }

  return (
    <section className="min-h-0 flex-1 overflow-y-auto">
      <PaperVersionView
        notebookId={notebookId}
        paperId={paperId}
        versionNumber={versionNumber}
        siblingVersions={siblingVersions}
      />
    </section>
  )
}
