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
  X,
} from "lucide-react"
import { Link } from "react-router-dom"
import { toast } from "sonner"

import { QuestionPaperActionsMenu } from "@/features/question-papers/components/question-paper-actions-menu"
import { GenerateVersionDialog } from "@/features/question-papers/components/generate-version-dialog"
import { PaperVersionDialog } from "@/features/question-papers/components/paper-version-dialog"
import { useCancelPaperVersion } from "@/features/question-papers/hooks/use-cancel-paper-version"
import { useDeleteQuestionPaper } from "@/features/question-papers/hooks/use-delete-question-paper"
import { useNotebookPapers } from "@/features/question-papers/hooks/use-notebook-papers"
import {
  canCancelVersion,
  canCreateNewVersion,
  isActiveGenerationStatus,
  nextVersionNumber,
} from "@/features/question-papers/lib/question-paper-utils"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
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
  const deletePaper = useDeleteQuestionPaper(notebook.id)
  const cancelVersion = useCancelPaperVersion(notebook.id)
  const papers = papersQuery.data ?? []
  const canGenerate = notebook.selected_chapters.length > 0
  const generateHref = `/notebooks/${notebook.id}/generate`

  const [collapsedIds, setCollapsedIds] = React.useState<Set<string>>(
    () => new Set()
  )
  const [selected, setSelected] = React.useState<SelectedVersion | null>(null)
  const [downloadingId, setDownloadingId] = React.useState<string | null>(null)
  const [generatePaper, setGeneratePaper] =
    React.useState<QuestionPaperSummary | null>(null)

  function setPaperOpen(paperId: string, open: boolean) {
    setCollapsedIds((prev) => {
      const next = new Set(prev)
      if (open) next.delete(paperId)
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
      await downloadVersionExport(paper.id, version.version_number)
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
                <Collapsible
                  key={paper.id}
                  open={expanded}
                  onOpenChange={(open) => setPaperOpen(paper.id, open)}
                  className="rounded-lg"
                >
                  <QuestionPaperActionsMenu
                    title={paper.title}
                    nextVersionNumber={
                      canCreateNewVersion(paper)
                        ? nextVersionNumber(paper)
                        : null
                    }
                    onGenerateVersion={() => setGeneratePaper(paper)}
                    onDelete={() => deletePaper.mutateAsync(paper.id)}
                  >
                    <CollapsibleTrigger
                      render={
                        <Button
                          type="button"
                          variant="ghost"
                          className="h-auto w-full justify-start gap-2 bg-transparent p-2 text-sm font-medium hover:bg-transparent aria-expanded:bg-transparent"
                        />
                      }
                    >
                      <ChevronDown
                        className={cn(
                          "size-4 shrink-0 text-muted-foreground transition-transform",
                          !expanded && "-rotate-90"
                        )}
                        aria-hidden
                      />
                      <span className="truncate">{paper.title}</span>
                    </CollapsibleTrigger>
                  </QuestionPaperActionsMenu>

                  <CollapsibleContent>
                    <ul className="space-y-0.5 px-1 pb-1">
                      {versions.map((version) => {
                        const processing = isActiveGenerationStatus(
                          version.status
                        )
                        const ready = version.status === "ready"
                        const failed = version.status === "failed"
                        const cancelled = version.status === "cancelled"
                        const cancellable = canCancelVersion(version)
                        const cancelling =
                          cancelVersion.isPending &&
                          cancelVersion.variables?.paperId === paper.id &&
                          cancelVersion.variables?.versionNumber ===
                            version.version_number
                        const downloading = downloadingId === version.id
                        const label = processing
                          ? `Version ${version.version_number} (Processing...)`
                          : cancelled
                            ? `Version ${version.version_number} (Cancelled)`
                            : `Version ${version.version_number}`

                        return (
                          <li key={version.id}>
                            <div
                              className={cn(
                                "flex items-center gap-1 rounded-md",
                                ready && "hover:bg-emerald-500/10",
                                processing && "text-muted-foreground",
                                (failed || cancelled) && "text-destructive/80"
                              )}
                            >
                              {ready ? (
                                <Button
                                  type="button"
                                  variant="ghost"
                                  className="h-auto min-w-0 flex-1 cursor-pointer justify-start gap-2 px-3 py-1 text-xs font-medium text-emerald-600 hover:bg-transparent hover:text-emerald-600 dark:text-emerald-400 dark:hover:text-emerald-400"
                                  onClick={() =>
                                    openVersion(paper, version.version_number)
                                  }
                                >
                                  <Check
                                    className="size-3.5 shrink-0"
                                    aria-hidden
                                  />
                                  <span className="truncate">{label}</span>
                                </Button>
                              ) : (
                                <div className="flex min-w-0 flex-1 items-center gap-2 px-2 py-2 text-sm">
                                  <span className="flex size-4 shrink-0 items-center justify-center">
                                    {processing ? (
                                      <Loader2
                                        className="size-3.5 animate-spin"
                                        aria-hidden
                                      />
                                    ) : (
                                      <AlertCircle
                                        className="size-3.5"
                                        aria-hidden
                                      />
                                    )}
                                  </span>
                                  <span className="truncate">{label}</span>
                                </div>
                              )}

                              {cancellable ? (
                                <span className="flex shrink-0 items-center pr-1">
                                  <Tooltip>
                                    <TooltipTrigger
                                      render={
                                        <Button
                                          type="button"
                                          variant="ghost"
                                          size="icon-xs"
                                          className="text-muted-foreground hover:text-destructive"
                                          disabled={cancelling}
                                          aria-label={`Cancel version ${version.version_number}`}
                                          onClick={() =>
                                            void cancelVersion.mutateAsync({
                                              paperId: paper.id,
                                              versionNumber:
                                                version.version_number,
                                            })
                                          }
                                        />
                                      }
                                    >
                                      {cancelling ? (
                                        <Loader2 className="size-3.5 animate-spin" />
                                      ) : (
                                        <X className="size-3.5" />
                                      )}
                                    </TooltipTrigger>
                                    <TooltipContent>Cancel</TooltipContent>
                                  </Tooltip>
                                </span>
                              ) : null}

                              {ready ? (
                                <span className="flex shrink-0 items-center gap-0.5 pr-1">
                                  <Tooltip>
                                    <TooltipTrigger
                                      render={
                                        <Button
                                          type="button"
                                          variant="ghost"
                                          size="icon-xs"
                                          className="text-muted-foreground hover:text-foreground"
                                          aria-label={`Preview version ${version.version_number}`}
                                          onClick={() =>
                                            openVersion(
                                              paper,
                                              version.version_number
                                            )
                                          }
                                        />
                                      }
                                    >
                                      <Eye className="size-3.5" />
                                    </TooltipTrigger>
                                    <TooltipContent>Preview</TooltipContent>
                                  </Tooltip>
                                  <Tooltip>
                                    <TooltipTrigger
                                      render={
                                        <Button
                                          type="button"
                                          variant="ghost"
                                          size="icon-xs"
                                          className="text-muted-foreground hover:text-foreground"
                                          disabled={downloading}
                                          aria-label={`Download version ${version.version_number}`}
                                          onClick={() =>
                                            void downloadVersion(paper, version)
                                          }
                                        />
                                      }
                                    >
                                      {downloading ? (
                                        <Loader2 className="size-3.5 animate-spin" />
                                      ) : (
                                        <Download className="size-3.5" />
                                      )}
                                    </TooltipTrigger>
                                    <TooltipContent>Download</TooltipContent>
                                  </Tooltip>
                                </span>
                              ) : null}
                            </div>
                          </li>
                        )
                      })}
                    </ul>
                  </CollapsibleContent>
                </Collapsible>
              )
            })
          )}
        </div>
      </ScrollArea>

      {generatePaper ? (
        <GenerateVersionDialog
          open
          onOpenChange={(open) => {
            if (!open) setGeneratePaper(null)
          }}
          notebookId={notebook.id}
          paper={generatePaper}
        />
      ) : null}

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
