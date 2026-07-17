import * as React from "react"
import { ArrowLeft, Menu, PanelLeftClose } from "lucide-react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { toast } from "sonner"

import { Thread } from "@/components/assistant-ui/thread"
import { AuthStatus, useAuth } from "@/components/auth-provider"
import { QuestionPapersSidebar } from "@/components/notebooks/question-papers-sidebar"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { ChatRuntimeProvider } from "@/features/chat/runtime/chat-runtime-provider"
import { useNotebooks } from "@/hooks/use-notebooks"
import { cn } from "@/lib/utils"

export function NotebookPage() {
  const { notebookId = "" } = useParams()
  const navigate = useNavigate()
  const { status } = useAuth()
  const { notebooks, loading, error } = useNotebooks()
  const [sidebarOpen, setSidebarOpen] = React.useState(true)

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
    <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
      <div className="flex shrink-0 items-center gap-2 border-b px-3 py-2 sm:px-4">
        <Button
          type="button"
          variant="ghost"
          size="icon-sm"
          className="lg:hidden"
          aria-label={sidebarOpen ? "Hide papers" : "Show papers"}
          onClick={() => setSidebarOpen((open) => !open)}
        >
          {sidebarOpen ? <PanelLeftClose /> : <Menu />}
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="gap-1.5 text-muted-foreground"
          render={<Link to="/dashboard" />}
        >
          <ArrowLeft className="size-4" />
          <span className="hidden sm:inline">Dashboard</span>
        </Button>
        <div className="min-w-0 flex-1">
          <h1 className="truncate text-sm font-semibold sm:text-base">
            {notebook.name}
          </h1>
          <p className="truncate text-xs text-muted-foreground">
            {[notebook.class_grade, notebook.subject]
              .filter(Boolean)
              .join(" · ") || "Notebook workspace"}
          </p>
        </div>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="hidden gap-1.5 lg:inline-flex"
          onClick={() => setSidebarOpen((open) => !open)}
        >
          {sidebarOpen ? (
            <PanelLeftClose className="size-4" />
          ) : (
            <Menu className="size-4" />
          )}
          Papers
        </Button>
      </div>

      <div className="relative flex min-h-0 flex-1 overflow-hidden">
        <div
          className={cn(
            "absolute inset-y-0 left-0 z-20 w-[min(100%,18rem)] border-r bg-background shadow-lg transition-transform lg:static lg:z-0 lg:w-72 lg:shadow-none xl:w-80",
            sidebarOpen ? "translate-x-0" : "-translate-x-full lg:hidden"
          )}
        >
          <QuestionPapersSidebar notebookName={notebook.name} />
        </div>

        {sidebarOpen && (
          <button
            type="button"
            aria-label="Close papers sidebar"
            className="absolute inset-0 z-10 bg-black/30 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        <section className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
          <ChatRuntimeProvider
            key={notebook.id}
            notebookId={notebook.id}
            notebookName={notebook.name}
          >
            <Thread notebookName={notebook.name} />
          </ChatRuntimeProvider>
        </section>
      </div>
    </div>
  )
}

function NotebookWorkspaceSkeleton() {
  return (
    <div className="flex min-h-0 flex-1 flex-col gap-0">
      <div className="flex items-center gap-3 border-b px-4 py-3">
        <Skeleton className="h-8 w-24" />
        <Skeleton className="h-5 w-48" />
      </div>
      <div className="flex min-h-0 flex-1">
        <Skeleton className="hidden h-full w-72 rounded-none lg:block" />
        <div className="flex flex-1 flex-col gap-4 p-6">
          <Skeleton className="mx-auto h-8 w-64" />
          <Skeleton className="mx-auto h-24 w-full max-w-2xl" />
          <Skeleton className="mx-auto mt-auto h-24 w-full max-w-2xl" />
        </div>
      </div>
    </div>
  )
}
