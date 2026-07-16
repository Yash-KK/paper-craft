import { FileText, Plus, TrendingUp } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import type { NotebookListItem } from "@/lib/types/notebook"
import {
  formatNotebookDate,
  NOTEBOOK_THEME_STYLES,
  notebookTheme,
} from "@/lib/notebook-utils"
import { cn } from "@/lib/utils"

type NotebookCardProps = {
  notebook: NotebookListItem
  index: number
}

export function NotebookCard({ notebook, index }: NotebookCardProps) {
  const theme = NOTEBOOK_THEME_STYLES[notebookTheme(notebook.color_hex, index)]
  const chapters = notebook.selected_chapters.map(
    (ch) => `Ch ${ch.chapter_number}`
  )
  const preview = chapters.slice(0, 4).join(", ")
  const extra = chapters.length > 4 ? ` +${chapters.length - 4} more` : ""

  return (
    <Card
      className={cn(
        "group gap-0 rounded-2xl py-0 ring-border/60 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl",
        theme.glow
      )}
    >
      <div className={cn("h-1.5 w-full shrink-0", theme.stripe)} />

      <CardHeader className="gap-3 pt-5">
        <div className="flex items-start justify-between gap-3">
          <div
            className={cn(
              "flex size-11 items-center justify-center rounded-xl",
              theme.iconBg
            )}
          >
            <FileText className={cn("size-5", theme.iconText)} />
          </div>
          {notebook.class_grade && (
            <Badge variant="secondary" className={theme.badge}>
              {notebook.class_grade}
            </Badge>
          )}
        </div>
        <CardTitle className="text-lg font-semibold">{notebook.name}</CardTitle>
        <CardDescription className="line-clamp-2">
          {notebook.subject ?? "Notebook"}
        </CardDescription>
      </CardHeader>

      {chapters.length > 0 && (
        <CardContent className="space-y-2 pb-4">
          <div className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
            <TrendingUp className="size-3.5" />
            Chapters
          </div>
          <p className="text-sm text-foreground/80">
            {preview}
            {extra}
          </p>
        </CardContent>
      )}

      <Separator />

      <CardFooter className="justify-between border-t-0 bg-transparent text-xs text-muted-foreground">
        <span>{chapters.length} chapters</span>
        <span>Updated {formatNotebookDate(notebook.updated_at)}</span>
      </CardFooter>
    </Card>
  )
}

export function CreateNotebookCard({ onClick }: { onClick?: () => void }) {
  return (
    <Card
      className="group min-h-[280px] justify-center rounded-2xl border-2 border-dashed bg-muted/20 py-0 ring-border/80 transition-all hover:border-violet-500/40 hover:bg-violet-500/5"
    >
      <CardContent className="flex flex-col items-center justify-center gap-4 py-10 text-center">
        <Button
          type="button"
          variant="ghost"
          size="icon-lg"
          onClick={onClick}
          className="size-14 rounded-2xl bg-violet-500/10 group-hover:scale-110"
          aria-label="Create new notebook"
        >
          <Plus className="size-7 text-violet-600 dark:text-violet-400" />
        </Button>
        <div className="space-y-1">
          <CardTitle className="text-base">Create New Notebook</CardTitle>
          <CardDescription>Start organizing your papers</CardDescription>
        </div>
      </CardContent>
    </Card>
  )
}
