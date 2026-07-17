import * as React from "react"
import { Plus } from "lucide-react"
import { useNavigate } from "react-router-dom"
import { toast } from "sonner"

import { AuthStatus, useAuth } from "@/components/auth-provider"
import { CreateNotebookDialog } from "@/components/notebooks/create-notebook-dialog"
import {
  CreateNotebookCard,
  NotebookCard,
} from "@/components/notebooks/notebook-card"
import { NotebookStats } from "@/components/notebooks/notebook-stats"
import { NotebooksEmptyState } from "@/components/notebooks/notebooks-empty-state"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"
import { useNotebooks } from "@/hooks/use-notebooks"
import { deleteNotebook } from "@/lib/api"

function DashboardSkeleton() {
  return (
    <div className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-8 px-4 py-8 sm:px-6">
      <Skeleton className="h-10 w-56" />
      <div className="grid gap-3 sm:grid-cols-2">
        <Skeleton className="h-24 rounded-xl" />
        <Skeleton className="h-24 rounded-xl" />
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <Skeleton className="h-72 rounded-2xl" />
        <Skeleton className="h-72 rounded-2xl" />
        <Skeleton className="h-72 rounded-2xl" />
      </div>
    </div>
  )
}

export function DashboardPage() {
  const navigate = useNavigate()
  const { status, user } = useAuth()
  const { notebooks, loading, error, reload } = useNotebooks()
  const [dialogOpen, setDialogOpen] = React.useState(false)

  React.useEffect(() => {
    if (status === AuthStatus.Unauthenticated) {
      navigate("/", { replace: true })
    }
  }, [status, navigate])

  React.useEffect(() => {
    if (error) toast.error(error)
  }, [error])

  if (status === AuthStatus.Loading || status === AuthStatus.Unauthenticated) {
    return <DashboardSkeleton />
  }

  const firstName = user?.full_name?.split(" ")[0] ?? "there"

  async function handleDeleteNotebook(notebookId: string) {
    try {
      await deleteNotebook(notebookId)
      await reload()
      toast.success("Notebook deleted.")
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Failed to delete notebook"
      )
    }
  }

  return (
    <>
      <div className="relative flex flex-1 flex-col">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-x-0 top-0 h-72 bg-[radial-gradient(ellipse_at_top,oklch(0.72_0.14_285/0.12),transparent_60%)] dark:bg-[radial-gradient(ellipse_at_top,oklch(0.55_0.16_285/0.18),transparent_60%)]"
        />

        <div className="relative mx-auto flex w-full max-w-6xl flex-1 flex-col gap-8 px-4 py-8 sm:px-6 sm:py-10">
          <Card className="border-none bg-transparent py-0 shadow-none ring-0">
            <CardHeader className="flex flex-col gap-6 px-0 sm:flex-row sm:items-end sm:justify-between">
              <div className="space-y-2">
                <CardDescription className="font-medium text-violet-600 dark:text-violet-400">
                  Welcome back, {firstName}
                </CardDescription>
                <CardTitle className="text-3xl font-semibold sm:text-4xl">
                  My Notebooks
                </CardTitle>
                <CardDescription>
                  Manage your question papers and study materials.
                </CardDescription>
              </div>
              <Button
                size="lg"
                className="gap-2 self-start bg-violet-600 text-white hover:bg-violet-600/90 sm:self-auto"
                onClick={() => setDialogOpen(true)}
              >
                <Plus />
                Create Notebook
              </Button>
            </CardHeader>
          </Card>

          <Separator />

          <NotebookStats notebooks={notebooks} />

          {loading ? (
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              <Skeleton className="h-72 rounded-2xl" />
              <Skeleton className="h-72 rounded-2xl" />
              <Skeleton className="h-72 rounded-2xl" />
            </div>
          ) : notebooks.length === 0 ? (
            <NotebooksEmptyState onCreateClick={() => setDialogOpen(true)} />
          ) : (
            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {notebooks.map((notebook, index) => (
                <NotebookCard
                  key={notebook.id}
                  notebook={notebook}
                  index={index}
                  onDelete={() => handleDeleteNotebook(notebook.id)}
                />
              ))}
              <CreateNotebookCard onClick={() => setDialogOpen(true)} />
            </section>
          )}
        </div>
      </div>

      <CreateNotebookDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        onCreated={reload}
      />
    </>
  )
}
