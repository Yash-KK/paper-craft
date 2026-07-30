import * as React from "react"
import {
  AlertCircle,
  Check,
  ChevronDown,
  Download,
  Eye,
  Loader2,
  Plus,
  Sparkles,
} from "lucide-react"
import { Link } from "react-router-dom"
import { toast } from "sonner"

import { PaperVersionDialog } from "@/features/question-papers/components/paper-version-dialog"
import { useNotebookPapers } from "@/features/question-papers/hooks/use-notebook-papers"
import { isActiveGenerationStatus } from "@/features/question-papers/lib/question-paper-utils"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Skeleton } from "@/components/ui/skeleton"
import { downloadVersionExport } from "@/lib/api"
import type {
  QuestionPaperSummary,
  QuestionPaperVersionSummary,
} from "@/lib/types/generation"
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
  const [downloadingId, setDownloadingId] = React.useState<string | null>(null)

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

  async function downloadVersion(
    paper: QuestionPaperSummary,
    version: QuestionPaperVersionSummary
  ) {
    setDownloadingId(version.id)
    try {
      await downloadVersionExport(paper.id, version.version_number, "paper")
      toast.success("Question paper downloaded.")
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Download failed")
    } finally {
      setDownloadingId(null)
    }
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
        <div className="flex flex-col gap-2 px-2 pb-4">
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
                    className="flex w-full cursor-pointer items-center gap-2 rounded-lg px-2 py-2 text-left text-sm font-medium hover:bg-muted/60"
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
                    <ul className="space-y-0.5 px-1 pb-1">
                      {versions.map((version) => {
                        const processing = isActiveGenerationStatus(
                          version.status
                        )
                        const ready = version.status === "ready"
                        const failed = version.status === "failed"
                        const downloading = downloadingId === version.id
                        const label = processing
                          ? `Version ${version.version_number} (Processing...)`
                          : `Version ${version.version_number}`

                        return (
                          <li key={version.id}>
                            <div
                              role={ready ? "button" : undefined}
                              tabIndex={ready ? 0 : undefined}
                              onClick={
                                ready
                                  ? () =>
                                      openVersion(paper, version.version_number)
                                  : undefined
                              }
                              onKeyDown={
                                ready
                                  ? (event) => {
                                      if (
                                        event.key === "Enter" ||
                                        event.key === " "
                                      ) {
                                        event.preventDefault()
                                        openVersion(
                                          paper,
                                          version.version_number
                                        )
                                      }
                                    }
                                  : undefined
                              }
                              className={cn(
                                "flex items-center gap-2 rounded-md px-2 py-2 text-sm",
                                ready &&
                                  "cursor-pointer hover:bg-emerald-500/10",
                                processing && "text-muted-foreground",
                                failed && "text-destructive/80"
                              )}
                            >
                              <span className="flex size-4 shrink-0 items-center justify-center">
                                {processing ? (
                                  <Loader2
                                    className="size-3.5 animate-spin"
                                    aria-hidden
                                  />
                                ) : ready ? (
                                  <Check
                                    className="size-3.5 text-emerald-600 dark:text-emerald-400"
                                    aria-hidden
                                  />
                                ) : (
                                  <AlertCircle
                                    className="size-3.5"
                                    aria-hidden
                                  />
                                )}
                              </span>

                              <span
                                className={cn(
                                  "min-w-0 flex-1 truncate",
                                  ready &&
                                    "font-medium text-emerald-600 dark:text-emerald-400"
                                )}
                              >
                                {label}
                              </span>

                              {ready ? (
                                <span className="flex shrink-0 items-center gap-0.5">
                                  <Button
                                    type="button"
                                    variant="ghost"
                                    size="icon-xs"
                                    className="text-muted-foreground hover:text-foreground"
                                    aria-label={`Preview version ${version.version_number}`}
                                    onClick={(event) => {
                                      event.stopPropagation()
                                      openVersion(
                                        paper,
                                        version.version_number
                                      )
                                    }}
                                  >
                                    <Eye className="size-3.5" />
                                  </Button>
                                  <Button
                                    type="button"
                                    variant="ghost"
                                    size="icon-xs"
                                    className="text-muted-foreground hover:text-foreground"
                                    disabled={downloading}
                                    aria-label={`Download version ${version.version_number}`}
                                    onClick={(event) => {
                                      event.stopPropagation()
                                      void downloadVersion(paper, version)
                                    }}
                                  >
                                    {downloading ? (
                                      <Loader2 className="size-3.5 animate-spin" />
                                    ) : (
                                      <Download className="size-3.5" />
                                    )}
                                  </Button>
                                </span>
                              ) : null}
                            </div>
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
