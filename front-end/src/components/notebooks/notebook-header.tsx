import { ChevronDown, ListPlus, Loader2, Notebook, PanelLeft } from "lucide-react"
import { toast } from "sonner"

import { useSidebarOptional } from "@/components/sidebar-context"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useChapters } from "@/hooks/use-chapter-catalog"
import { useUpdateNotebook } from "@/hooks/use-notebooks"
import type { NotebookListItem } from "@/lib/types/notebook"

type NotebookHeaderProps = {
  notebook: NotebookListItem
}

export function NotebookHeader({ notebook }: NotebookHeaderProps) {
  const sidebar = useSidebarOptional()
  const updateNotebook = useUpdateNotebook()
  const canEditChapters = Boolean(notebook.class_grade && notebook.subject)
  const chaptersQuery = useChapters(
    notebook.class_grade ?? "",
    notebook.subject ?? "",
    canEditChapters
  )

  const breadcrumb = [notebook.class_grade, notebook.subject]
    .filter(Boolean)
    .join(" / ")
  const selectedNumbers = notebook.selected_chapters.map(
    (chapter) => chapter.chapter_number
  )
  const catalog = chaptersQuery.data ?? []
  const saving = updateNotebook.isPending

  async function toggleChapter(chapterNumber: number) {
    const next = selectedNumbers.includes(chapterNumber)
      ? selectedNumbers.filter((n) => n !== chapterNumber)
      : [...selectedNumbers, chapterNumber].sort((a, b) => a - b)

    if (next.length === 0) {
      toast.error("Select at least one chapter")
      return
    }

    try {
      await updateNotebook.mutateAsync({
        notebookId: notebook.id,
        payload: { selected_chapter_numbers: next },
      })
    } catch {
      // Toast handled by mutation onError
    }
  }

  return (
    <header className="flex shrink-0 flex-wrap items-center gap-3 border-b bg-background px-4 py-3 sm:px-6">
      <div className="flex min-w-0 flex-1 items-center gap-3">
        {sidebar && !sidebar.sidebarOpen ? (
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            className="shrink-0 text-muted-foreground"
            aria-label="Open sidebar"
            onClick={() => sidebar.setSidebarOpen(true)}
          >
            <PanelLeft className="size-4" />
          </Button>
        ) : null}
        <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-violet-600 text-white shadow-sm">
          <Notebook className="size-5" />
        </span>
        <div className="min-w-0 flex-1">
          {breadcrumb ? (
            <p className="truncate text-xs text-muted-foreground">
              {breadcrumb}
            </p>
          ) : null}
          <div className="flex min-w-0 flex-wrap items-center gap-2">
            <h1 className="truncate font-heading text-base font-semibold tracking-tight sm:text-lg">
              {notebook.name}
            </h1>
            {notebook.selected_chapters.map((chapter) => (
              <Badge
                key={`${chapter.book_code}-${chapter.chapter_number}`}
                variant="outline"
                className="h-7 rounded-full border-violet-300 bg-violet-50 px-2.5 text-violet-700 dark:border-violet-700 dark:bg-violet-950/40 dark:text-violet-300"
                title={chapter.chapter_name}
              >
                Ch {chapter.chapter_number}
              </Badge>
            ))}
            <DropdownMenu>
              <DropdownMenuTrigger
                disabled={!canEditChapters || saving}
                render={
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="h-7 gap-1 rounded-full border-violet-300 px-2.5 text-violet-700 dark:border-violet-700 dark:text-violet-300"
                  />
                }
              >
                {saving || chaptersQuery.isFetching ? (
                  <Loader2 className="size-3.5 animate-spin" />
                ) : (
                  <ListPlus className="size-3.5" />
                )}
                Chapters
                <ChevronDown className="size-3.5 opacity-60" />
              </DropdownMenuTrigger>
              <DropdownMenuContent
                align="start"
                className="z-100 w-72 overflow-hidden p-0"
              >
                <DropdownMenuGroup>
                  <DropdownMenuLabel className="px-2.5 pt-2">
                    Add or remove chapters
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <ScrollArea className="h-56">
                    <div className="p-1">
                      {!canEditChapters ? (
                        <p className="px-2 py-1.5 text-sm text-muted-foreground">
                          Class and subject are required
                        </p>
                      ) : chaptersQuery.isPending ? (
                        <p className="flex items-center gap-2 px-2 py-1.5 text-sm text-muted-foreground">
                          <Loader2 className="size-3.5 animate-spin" />
                          Loading chapters…
                        </p>
                      ) : catalog.length === 0 ? (
                        <p className="px-2 py-1.5 text-sm text-muted-foreground">
                          No chapters available
                        </p>
                      ) : (
                        catalog.map((chapter) => {
                          const checked = selectedNumbers.includes(
                            chapter.chapter_number
                          )
                          return (
                            <DropdownMenuCheckboxItem
                              key={chapter.chapter_number}
                              checked={checked}
                              disabled={!chapter.is_available || saving}
                              onCheckedChange={() =>
                                void toggleChapter(chapter.chapter_number)
                              }
                            >
                              <span className="min-w-0">
                                <span className="block font-medium">
                                  Ch {chapter.chapter_number}
                                </span>
                                <span className="block truncate text-xs text-muted-foreground">
                                  {chapter.chapter_name}
                                </span>
                              </span>
                            </DropdownMenuCheckboxItem>
                          )
                        })
                      )}
                    </div>
                  </ScrollArea>
                </DropdownMenuGroup>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </header>
  )
}
