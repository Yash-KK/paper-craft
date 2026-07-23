import * as React from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { toast } from "sonner"

import { AuthStatus, useAuth } from "@/components/auth-provider"
import { NotebookHeader } from "@/components/notebooks/notebook-header"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { ChatPanel } from "@/features/chat"
import { useNotebookChat } from "@/hooks/use-notebook-chat"
import { useNotebooks } from "@/hooks/use-notebooks"

export function NotebookPage() {
  const { notebookId = "" } = useParams()
  const navigate = useNavigate()
  const { status } = useAuth()
  const { notebooks, loading, error } = useNotebooks()
  const notebook = notebooks.find((item) => item.id === notebookId)
  const chat = useNotebookChat(
    notebookId,
    status === AuthStatus.Authenticated && !loading && Boolean(notebook)
  )

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
    status === AuthStatus.Unauthenticated ||
    loading ||
    chat.isPending
  ) {
    return <NotebookWorkspaceSkeleton />
  }

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

  if (chat.error || !chat.data) {
    return (
      <div className="mx-auto flex w-full max-w-lg flex-1 flex-col items-center justify-center gap-4 px-4 py-16 text-center">
        <h1 className="font-heading text-xl font-semibold">
          Unable to load chat
        </h1>
        <p className="text-sm text-muted-foreground">
          {chat.error instanceof Error
            ? chat.error.message
            : "The notebook chat could not be loaded."}
        </p>
        <Button onClick={() => void chat.refetch()}>Try again</Button>
      </div>
    )
  }

  return (
    <section className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
      <NotebookHeader notebook={notebook} />
      <ChatPanel
        key={chat.data.id}
        notebookId={notebook.id}
        notebookName={notebook.name}
        initialMessages={chat.data.messages}
      />
    </section>
  )
}

function NotebookWorkspaceSkeleton() {
  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
      <div className="flex shrink-0 items-center gap-3 border-b px-4 py-3 sm:px-6">
        <Skeleton className="size-10 rounded-xl" />
        <div className="space-y-2">
          <Skeleton className="h-3 w-28" />
          <Skeleton className="h-5 w-48" />
        </div>
      </div>
      <div className="flex min-h-0 flex-1 flex-col gap-4 p-6">
        <Skeleton className="mx-auto h-24 w-full max-w-4xl" />
        <div className="mt-auto">
          <Skeleton className="mx-auto h-24 w-full max-w-4xl" />
        </div>
      </div>
    </div>
  )
}
