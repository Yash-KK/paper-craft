import * as React from "react"
import { AlertCircle, ChevronDown, Plus, Sparkles } from "lucide-react"
import { Link } from "react-router-dom"

import { PaperVersionDialog } from "@/features/question-papers/components/paper-version-dialog"
import { useNotebookPapers } from "@/features/question-papers/hooks/use-notebook-papers"
import { isActiveGenerationStatus } from "@/features/question-papers/lib/question-paper-utils"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Skeleton } from "@/components/ui/skeleton"
import type { QuestionPaperSummary } from "@/lib/types/generation"
import type { NotebookListItem } from "@/lib/types/notebook"
import { cn } from "@/lib/utils"

type QuestionPapersSidebarProps = {
  notebook: NotebookListItem
  className?: string
}

type SelectedVersion = {
  paperId: string
  paperTitle: string
  versionNumber: number
}

export function QuestionPapersSidebar({
  notebook,
  className,
}: QuestionPapersSidebarProps) {
  const papersQuery = useNotebookPapers(notebook.id)
  const papers = papersQuery.data ?? []
  const canGenerate = notebook.selected_chapters.length > 0
  const generateHref = `/notebooks/${notebook.id}/generate`

  const [collapsedIds, setCollapsedIds] = React.useState<Set<string>>(
    () => new Set()
  )
  const [selected, setSelected] = React.useState<SelectedVersion | null>(null)

  function togglePaper(paperId: string) {
    setCollapsedIds((prev) => {
      const next = new Set(prev)
      if (next.has(paperId)) next.delete(paperId)
      else next.add(paperId)
      return next
    })
  }

  function openVersion(paper: QuestionPaperSummary, versionNumber: number) {
    setSelected({
      paperId: paper.id,
      paperTitle: paper.title,
      versionNumber,
    })
  }

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
      </div>

      <div className="flex items-center justify-between px-4 py-3">
        <p className="text-xs font-medium text-muted-foreground">
          Generated papers
        </p>
        <Badge variant="secondary">{papers.length}</Badge>
      </div>

      <ScrollArea className="min-h-0 flex-1">
        <div className="flex flex-col gap-1 px-2 pb-4">
          {papersQuery.isPending ? (
            Array.from({ length: 3 }).map((_, index) => (
              <Skeleton key={index} className="h-10 w-full rounded-lg" />
            ))
          ) : papersQuery.isError ? (
            <div className="flex flex-col items-start gap-3 rounded-xl border border-destructive/20 bg-destructive/5 px-3 py-4">
              <div className="flex items-center gap-2 text-destructive">
                <AlertCircle className="size-4 shrink-0" aria-hidden />
                <p className="text-sm font-medium">Couldn&apos;t load papers</p>
              </div>
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
            </div>
          ) : (
            papers.map((paper) => {
              const expanded = !collapsedIds.has(paper.id)
              const versions = [...paper.versions].reverse()

              return (
                <div key={paper.id} className="rounded-lg">
                  <button
                    type="button"
                    onClick={() => togglePaper(paper.id)}
                    className="flex w-full items-center gap-2 rounded-lg px-2 py-2 text-left text-sm font-medium hover:bg-muted/60"
                  >
                    <ChevronDown
                      className={cn(
                        "size-4 shrink-0 text-muted-foreground transition-transform",
                        !expanded && "-rotate-90"
                      )}
                      aria-hidden
                    />
                    <span className="truncate">{paper.title}</span>
                  </button>

                  {expanded ? (
                    <ul className="ml-4 space-y-0.5 border-l border-border/70 py-1 pl-3">
                      {versions.map((version) => {
                        const processing = isActiveGenerationStatus(
                          version.status
                        )
                        const ready = version.status === "ready"
                        const label = processing
                          ? `Version ${version.version_number} (Processing...)`
                          : `Version ${version.version_number}`

                        if (!ready) {
                          return (
                            <li
                              key={version.id}
                              className="px-2 py-1.5 text-xs text-muted-foreground"
                            >
                              {label}
                            </li>
                          )
                        }

                        return (
                          <li key={version.id}>
                            <button
                              type="button"
                              onClick={() =>
                                openVersion(paper, version.version_number)
                              }
                              className="w-full rounded-md px-2 py-1.5 text-left text-xs hover:bg-muted/60"
                            >
                              {label}
                            </button>
                          </li>
                        )
                      })}
                    </ul>
                  ) : null}
                </div>
              )
            })
          )}
        </div>
      </ScrollArea>

      {selected ? (
        <PaperVersionDialog
          open
          onOpenChange={(open) => {
            if (!open) setSelected(null)
          }}
          paperId={selected.paperId}
          paperTitle={selected.paperTitle}
          versionNumber={selected.versionNumber}
        />
      ) : null}
    </div>
  )
}
