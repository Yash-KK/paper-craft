import * as React from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { toast } from "sonner"

import { Thread } from "@/components/assistant-ui/thread"
import { AuthStatus, useAuth } from "@/components/auth-provider"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { ChatRuntimeProvider } from "@/features/chat/runtime/chat-runtime-provider"
import { useNotebooks } from "@/hooks/use-notebooks"

export function NotebookPage() {
  const { notebookId = "" } = useParams()
  const navigate = useNavigate()
  const { status } = useAuth()
  const { notebooks, loading, error } = useNotebooks()

  React.useEffect(() => {
    if (status === AuthStatus.Unauthenticated) {
      navigate("/", { replace: true })
    }
  }, [status, navigate])

  React.useEffect(() => {
    if (error) toast.error(error)
  }, [error])

  if (status === AuthStatus.Loading || status === AuthStatus.Unauthenticated) {
    return <NotebookWorkspaceSkeleton />
  }

  if (loading) {
    return <NotebookWorkspaceSkeleton />
  }

  const notebook = notebooks.find((n) => n.id === notebookId)

  if (!notebook) {
    return (
      <div className="mx-auto flex w-full max-w-lg flex-1 flex-col items-center justify-center gap-4 px-4 py-16 text-center">
        <h1 className="font-heading text-xl font-semibold">
          Notebook not found
        </h1>
        <p className="text-sm text-muted-foreground">
          This notebook may have been deleted, or the list hasn&apos;t loaded
          yet.
        </p>
        <Button render={<Link to="/dashboard" />}>Back to dashboard</Button>
      </div>
    )
  }

  return (
    <section className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
      <ChatRuntimeProvider
        key={notebook.id}
        notebookId={notebook.id}
        notebookName={notebook.name}
      >
        <Thread notebookName={notebook.name} />
      </ChatRuntimeProvider>
    </section>
  )
}

function NotebookWorkspaceSkeleton() {
  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4 p-6">
      <Skeleton className="mx-auto h-8 w-64" />
      <Skeleton className="mx-auto h-24 w-full max-w-4xl" />
      <div className="mt-auto">
        <Skeleton className="mx-auto h-24 w-full max-w-4xl" />
      </div>
    </div>
  )
}
