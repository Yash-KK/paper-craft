import { AlertCircle, FileText, Loader2, Plus, Sparkles } from "lucide-react"
import { Link, useLocation } from "react-router-dom"

import { VersionStatusBadge } from "@/features/question-papers/components/version-status-badge"
import { useNotebookPapers } from "@/features/question-papers/hooks/use-notebook-papers"
import {
  formatRelativeTime,
  paperHref,
  versionHref,
} from "@/features/question-papers/lib/question-paper-utils"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Skeleton } from "@/components/ui/skeleton"
import type { NotebookListItem } from "@/lib/types/notebook"
import { cn } from "@/lib/utils"

type QuestionPapersSidebarProps = {
  notebook: NotebookListItem
  className?: string
}

export function QuestionPapersSidebar({
  notebook,
  className,
}: QuestionPapersSidebarProps) {
  const location = useLocation()
  const papersQuery = useNotebookPapers(notebook.id)
  const papers = papersQuery.data ?? []
  const canGenerate = notebook.selected_chapters.length > 0
  const generateHref = `/notebooks/${notebook.id}/generate`

  return (
    <div className={cn("flex h-full min-h-0 w-full flex-col", className)}>
      <div className="space-y-3 border-b p-4">
        <div className="space-y-1">
          <p className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
            Notebook
          </p>
          <h2 className="truncate font-heading text-sm font-semibold">
            {notebook.name}
          </h2>
        </div>
        <Button
          type="button"
          className="w-full gap-2 bg-emerald-600 text-white hover:bg-emerald-600/90"
          disabled={!canGenerate}
          title={
            canGenerate
              ? "Open question paper generation"
              : "Select chapters on this notebook first"
          }
          render={canGenerate ? <Link to={generateHref} /> : undefined}
        >
          <Sparkles className="size-4" aria-hidden />
          Generate Question Paper
        </Button>
        <p className="text-[11px] leading-relaxed text-muted-foreground">
          {canGenerate
            ? "Opens the paper builder with sample blueprints and marking scheme."
            : "Add chapters to this notebook before generating a paper."}
        </p>
      </div>

      <div className="flex items-center justify-between px-4 py-3">
        <p className="text-xs font-medium text-muted-foreground">
          Generated papers
        </p>
        <Badge variant="secondary">{papers.length}</Badge>
      </div>

      <ScrollArea className="min-h-0 flex-1">
        <div className="flex flex-col gap-2 px-3 pb-4">
          {papersQuery.isPending ? (
            Array.from({ length: 3 }).map((_, index) => (
              <Skeleton key={index} className="h-20 w-full rounded-xl" />
            ))
          ) : papersQuery.isError ? (
            <div className="flex flex-col items-start gap-3 rounded-xl border border-destructive/20 bg-destructive/5 px-3 py-4">
              <div className="flex items-center gap-2 text-destructive">
                <AlertCircle className="size-4 shrink-0" aria-hidden />
                <p className="text-sm font-medium">Couldn&apos;t load papers</p>
              </div>
              <p className="text-xs text-muted-foreground">
                {papersQuery.error instanceof Error
                  ? papersQuery.error.message
                  : "Please try again."}
              </p>
              <Button
                type="button"
                variant="secondary"
                size="sm"
                onClick={() => void papersQuery.refetch()}
              >
                Try again
              </Button>
            </div>
          ) : papers.length === 0 ? (
            <div className="flex flex-col items-center gap-2 rounded-xl border border-dashed px-3 py-8 text-center">
              <Plus className="size-5 text-muted-foreground" aria-hidden />
              <p className="text-xs text-muted-foreground">
                No papers yet. Generate one to get started.
              </p>
              {canGenerate ? (
                <Button
                  type="button"
                  size="sm"
                  variant="secondary"
                  render={<Link to={generateHref} />}
                >
                  Generate paper
                </Button>
              ) : null}
            </div>
          ) : (
            papers.map((paper) => {
              const href = paperHref(notebook.id, paper)
              const latest = paper.latest_version
              const isPaperActive =
                href != null && location.pathname.startsWith(
                  `/notebooks/${notebook.id}/papers/${paper.id}/`
                )

              return (
                <div
                  key={paper.id}
                  className={cn(
                    "rounded-xl border bg-card transition-colors",
                    isPaperActive && "border-violet-500/40 bg-violet-500/5"
                  )}
                >
                  {href ? (
                    <Link
                      to={href}
                      className="flex w-full items-start gap-3 px-3 py-3 text-left outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    >
                      <div className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg bg-violet-500/10 text-violet-600 dark:text-violet-400">
                        <FileText className="size-4" aria-hidden />
                      </div>
                      <div className="min-w-0 flex-1 space-y-1">
                        <p className="truncate text-sm font-medium">
                          {paper.title}
                        </p>
                        <div className="flex flex-wrap items-center gap-2 text-[11px] text-muted-foreground">
                          {latest ? (
                            <VersionStatusBadge status={latest.status} />
                          ) : null}
                          {latest ? (
                            <span>v{latest.version_number}</span>
                          ) : null}
                          <span>{formatRelativeTime(paper.updated_at)}</span>
                          {latest &&
                          (latest.status === "pending" ||
                            latest.status === "running") ? (
                            <Loader2
                              className="size-3 animate-spin text-sky-600"
                              aria-label="Generating"
                            />
                          ) : null}
                        </div>
                      </div>
                    </Link>
                  ) : (
                    <div className="px-3 py-3 text-sm text-muted-foreground">
                      {paper.title}
                    </div>
                  )}

                  {paper.versions.length > 1 ? (
                    <div className="space-y-1 border-t px-3 py-2">
                      {[...paper.versions].reverse().map((version) => {
                        const versionPath = versionHref(
                          notebook.id,
                          paper.id,
                          version.version_number
                        )
                        const active = location.pathname === versionPath
                        return (
                          <Link
                            key={version.id}
                            to={versionPath}
                            className={cn(
                              "flex min-h-10 items-center justify-between gap-2 rounded-lg px-2 py-1.5 text-xs outline-none transition-colors hover:bg-muted/60 focus-visible:ring-2 focus-visible:ring-ring",
                              active && "bg-muted font-medium"
                            )}
                          >
                            <span>Version {version.version_number}</span>
                            <VersionStatusBadge status={version.status} />
                          </Link>
                        )
                      })}
                    </div>
                  ) : null}
                </div>
              )
            })
          )}
        </div>
      </ScrollArea>
    </div>
  )
}
