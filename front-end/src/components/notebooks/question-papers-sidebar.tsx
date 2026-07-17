import { FileText, Plus, Sparkles } from "lucide-react"

import {
  MOCK_QUESTION_PAPERS,
  type MockQuestionPaper,
} from "@/components/notebooks/mock-question-papers"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { cn } from "@/lib/utils"

type QuestionPapersSidebarProps = {
  notebookName: string
  className?: string
  papers?: MockQuestionPaper[]
}

export function QuestionPapersSidebar({
  notebookName,
  className,
  papers = MOCK_QUESTION_PAPERS,
}: QuestionPapersSidebarProps) {
  return (
    <div
      className={cn(
        "flex h-full min-h-0 w-full flex-col",
        className
      )}
    >
      <div className="space-y-3 border-b p-4">
        <div className="space-y-1">
          <p className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
            Notebook
          </p>
          <h2 className="truncate font-heading text-sm font-semibold">
            {notebookName}
          </h2>
        </div>
        <Button
          type="button"
          className="w-full gap-2 bg-violet-600 text-white hover:bg-violet-600/90"
          disabled
          title="Coming soon — generation will call the Agentic RAG backend"
        >
          <Sparkles className="size-4" />
          Generate Question Paper
        </Button>
        <p className="text-[11px] leading-relaxed text-muted-foreground">
          Dummy for now. This will create papers scoped to this notebook.
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
          {papers.length === 0 ? (
            <div className="flex flex-col items-center gap-2 rounded-xl border border-dashed px-3 py-8 text-center">
              <Plus className="size-5 text-muted-foreground" />
              <p className="text-xs text-muted-foreground">
                No papers yet. Generate one to get started.
              </p>
            </div>
          ) : (
            papers.map((paper) => (
              <button
                key={paper.id}
                type="button"
                className="flex w-full items-start gap-3 rounded-xl border bg-card px-3 py-3 text-left transition-colors hover:bg-muted/60"
              >
                <div className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg bg-violet-500/10 text-violet-600 dark:text-violet-400">
                  <FileText className="size-4" />
                </div>
                <div className="min-w-0 flex-1 space-y-1">
                  <p className="truncate text-sm font-medium">{paper.title}</p>
                  <div className="flex flex-wrap items-center gap-2 text-[11px] text-muted-foreground">
                    <Badge
                      variant="secondary"
                      className={cn(
                        "h-5 px-1.5 text-[10px]",
                        paper.status === "ready"
                          ? "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300"
                          : "bg-amber-500/10 text-amber-700 dark:text-amber-300"
                      )}
                    >
                      {paper.status}
                    </Badge>
                    <span>{paper.marks} marks</span>
                    <Separator orientation="vertical" className="h-3" />
                    <span>{paper.updated_at}</span>
                  </div>
                </div>
              </button>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  )
}
