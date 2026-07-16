import * as React from "react"
import { Plus } from "lucide-react"
import { useNavigate } from "react-router-dom"

import { AuthStatus, useAuth } from "@/components/auth-provider"
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
import { MOCK_NOTEBOOKS } from "@/lib/mock-notebooks"

function handleNotebookClick() {
  alert("Hello")
}

function handleCreateClick() {
  alert("Hello")
}

function DashboardSkeleton() {
  return (
    <div className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-8 px-4 py-8 sm:px-6 sm:py-10">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-2">
          <Skeleton className="h-4 w-40" />
          <Skeleton className="h-9 w-56" />
          <Skeleton className="h-4 w-80 max-w-full" />
        </div>
        <Skeleton className="h-10 w-40" />
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        <Skeleton className="h-24 rounded-xl" />
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
  const notebooks = MOCK_NOTEBOOKS

  React.useEffect(() => {
    if (status === AuthStatus.Unauthenticated) {
      navigate("/", { replace: true })
    }
  }, [status, navigate])

  if (status === AuthStatus.Loading || status === AuthStatus.Unauthenticated) {
    return <DashboardSkeleton />
  }

  const firstName = user?.full_name?.split(" ")[0] ?? "there"

  return (
    <div className="relative flex flex-1 flex-col">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 h-72 bg-[radial-gradient(ellipse_at_top,oklch(0.72_0.14_285/0.12),transparent_60%)] dark:bg-[radial-gradient(ellipse_at_top,oklch(0.55_0.16_285/0.18),transparent_60%)]"
      />

      <div className="relative mx-auto flex w-full max-w-6xl flex-1 flex-col gap-8 px-4 py-8 sm:px-6 sm:py-10 lg:py-12">
        <Card className="border-none bg-transparent py-0 shadow-none ring-0">
          <CardHeader className="flex flex-col gap-6 px-0 sm:flex-row sm:items-end sm:justify-between">
            <div className="space-y-2">
              <CardDescription className="text-sm font-medium text-violet-600 dark:text-violet-400">
                Welcome back, {firstName}
              </CardDescription>
              <CardTitle className="text-3xl font-semibold tracking-tight sm:text-4xl">
                My Notebooks
              </CardTitle>
              <CardDescription className="max-w-xl text-sm sm:text-base">
                Manage your question papers and study materials in one beautiful
                workspace.
              </CardDescription>
            </div>

            <Button
              size="lg"
              className="h-10 shrink-0 gap-2 self-start bg-violet-600 px-4 text-white shadow-lg shadow-violet-600/20 hover:bg-violet-600/90 sm:self-auto dark:bg-violet-500 dark:hover:bg-violet-500/90"
              onClick={handleCreateClick}
            >
              <Plus />
              Create Notebook
            </Button>
          </CardHeader>
        </Card>

        <Separator />

        <NotebookStats />

        {notebooks.length === 0 ? (
          <NotebooksEmptyState onCreateClick={handleCreateClick} />
        ) : (
          <section className="grid gap-4 sm:grid-cols-2 sm:gap-5 xl:grid-cols-4">
            {notebooks.map((notebook) => (
              <NotebookCard
                key={notebook.id}
                notebook={notebook}
                onClick={handleNotebookClick}
              />
            ))}
            <CreateNotebookCard onClick={handleCreateClick} />
          </section>
        )}
      </div>
    </div>
  )
}
