import { FileText, Plus, TrendingUp } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import {
  formatNotebookDate,
  NOTEBOOK_THEME_STYLES,
  type MockNotebook,
} from "@/lib/mock-notebooks"
import { cn } from "@/lib/utils"

type NotebookCardProps = {
  notebook: MockNotebook
  onClick?: () => void
}

export function NotebookCard({ notebook, onClick }: NotebookCardProps) {
  const theme = NOTEBOOK_THEME_STYLES[notebook.theme]
  const chapterPreview = notebook.chapters.slice(0, 4).join(", ")
  const extraChapters =
    notebook.chapters.length > 4
      ? ` +${notebook.chapters.length - 4} more`
      : ""

  return (
    <Card
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault()
          onClick?.()
        }
      }}
      className={cn(
        "group cursor-pointer gap-0 rounded-2xl py-0 ring-border/60 transition-all duration-300",
        "hover:-translate-y-1 hover:shadow-xl focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none",
        theme.glow
      )}
    >
      <div className={cn("h-1.5 w-full shrink-0", theme.stripe)} />

      <CardHeader className="gap-3 pt-5">
        <div className="flex items-start justify-between gap-3">
          <div
            className={cn(
              "flex size-11 shrink-0 items-center justify-center rounded-xl transition-transform duration-300 group-hover:scale-105",
              theme.iconBg
            )}
          >
            <FileText className={cn("size-5", theme.iconText)} />
          </div>
          <Badge variant="secondary" className={theme.badge}>
            {notebook.classGrade}
          </Badge>
        </div>
        <CardTitle className="text-lg font-semibold tracking-tight">
          {notebook.title}
        </CardTitle>
        <CardDescription className="line-clamp-2 leading-relaxed">
          {notebook.description}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-2 pb-4">
        <div className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
          <TrendingUp className="size-3.5" />
          Chapters
        </div>
        <p className="text-sm text-foreground/80">
          {chapterPreview}
          {extraChapters}
        </p>
      </CardContent>

      <Separator />

      <CardFooter className="justify-between gap-3 border-t-0 bg-transparent">
        <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
          <FileText className="size-3.5" />
          <span>
            {notebook.documentCount}{" "}
            {notebook.documentCount === 1 ? "Paper" : "Papers"}
          </span>
        </div>
        <p className="text-xs text-muted-foreground">
          Updated {formatNotebookDate(notebook.lastUpdated)}
        </p>
      </CardFooter>

      <div className="flex items-center justify-end gap-1.5 px-4 pb-4">
        {(["violet", "teal", "amber"] as const).map((dotTheme, index) => (
          <span
            key={dotTheme}
            className={cn(
              "size-1.5 rounded-full opacity-60 transition-opacity group-hover:opacity-100",
              NOTEBOOK_THEME_STYLES[
                index === 0 ? notebook.theme : index === 1 ? "teal" : "amber"
              ].dot
            )}
          />
        ))}
      </div>
    </Card>
  )
}

type CreateNotebookCardProps = {
  onClick?: () => void
}

export function CreateNotebookCard({ onClick }: CreateNotebookCardProps) {
  return (
    <Card
      className={cn(
        "group min-h-[280px] justify-center rounded-2xl border-2 border-dashed bg-muted/20 py-0 ring-border/80 transition-all duration-300",
        "hover:border-violet-500/40 hover:bg-violet-500/5 hover:shadow-lg hover:shadow-violet-500/10"
      )}
    >
      <CardContent className="flex flex-col items-center justify-center gap-4 py-10 text-center">
        <Button
          type="button"
          variant="ghost"
          size="icon-lg"
          onClick={onClick}
          className="size-14 rounded-2xl bg-violet-500/10 transition-transform duration-300 group-hover:scale-110 hover:bg-violet-500/15"
          aria-label="Create new notebook"
        >
          <Plus className="size-7 text-violet-600 dark:text-violet-400" />
        </Button>
        <div className="space-y-1">
          <CardTitle className="text-base font-semibold">
            Create New Notebook
          </CardTitle>
          <CardDescription>
            Start organizing your papers
          </CardDescription>
        </div>
      </CardContent>
    </Card>
  )
}
