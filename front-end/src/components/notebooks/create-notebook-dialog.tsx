import * as React from "react"
import { Check, ChevronDown, Loader2 } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  createNotebook,
  fetchChapters,
  fetchGrades,
  fetchSubjects,
} from "@/lib/api"
import type { ClassGrade, Subject } from "@/lib/types/notebook"
import { cn } from "@/lib/utils"

type CreateNotebookDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  onCreated: () => void
}

type FormState = {
  name: string
  classGrade: ClassGrade | ""
  subject: Subject | ""
  chapters: number[]
}

const EMPTY_FORM: FormState = {
  name: "",
  classGrade: "",
  subject: "",
  chapters: [],
}

type SelectFieldProps<T extends string> = {
  label: string
  value: T | ""
  placeholder: string
  disabled?: boolean
  loading?: boolean
  options: T[]
  onChange: (value: T) => void
}

function SelectField<T extends string>({
  label,
  value,
  placeholder,
  disabled,
  loading,
  options,
  onChange,
}: SelectFieldProps<T>) {
  return (
    <div className="grid gap-2">
      <Label>{label}</Label>
      <DropdownMenu>
        <DropdownMenuTrigger
          disabled={disabled || loading}
          render={
            <Button
              variant="outline"
              className="h-10 w-full justify-between font-normal"
            />
          }
        >
          <span className="truncate">
            {loading ? "Loading…" : value || placeholder}
          </span>
          <ChevronDown className="size-4 shrink-0 opacity-50" />
        </DropdownMenuTrigger>
        <DropdownMenuContent className="z-100 max-h-60 w-(--anchor-width)">
          {options.length === 0 ? (
            <DropdownMenuItem disabled>No options available</DropdownMenuItem>
          ) : (
            options.map((option) => (
              <DropdownMenuItem key={option} onClick={() => onChange(option)}>
                {option}
                {value === option ? <Check className="ml-auto size-4" /> : null}
              </DropdownMenuItem>
            ))
          )}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}

export function CreateNotebookDialog({
  open,
  onOpenChange,
  onCreated,
}: CreateNotebookDialogProps) {
  const [form, setForm] = React.useState<FormState>(EMPTY_FORM)
  const [grades, setGrades] = React.useState<ClassGrade[]>([])
  const [gradesError, setGradesError] = React.useState(false)
  const [subjects, setSubjects] = React.useState<Subject[]>([])
  const [catalog, setCatalog] = React.useState<
    { chapter_number: number; chapter_name: string }[]
  >([])
  const [loadingSubjects, setLoadingSubjects] = React.useState(false)
  const [loadingChapters, setLoadingChapters] = React.useState(false)
  const [submitting, setSubmitting] = React.useState(false)

  const loadingGrades = open && grades.length === 0 && !gradesError

  function handleOpenChange(next: boolean) {
    if (!next) {
      setForm(EMPTY_FORM)
      setGrades([])
      setGradesError(false)
      setSubjects([])
      setCatalog([])
    }
    onOpenChange(next)
  }

  React.useEffect(() => {
    if (!open) return

    let cancelled = false

    fetchGrades()
      .then((data) => {
        if (!cancelled) {
          setGrades(data)
          setGradesError(false)
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setGradesError(true)
          toast.error(
            err instanceof Error ? err.message : "Failed to load classes"
          )
        }
      })

    return () => {
      cancelled = true
    }
  }, [open])

  async function handleClassChange(grade: ClassGrade) {
    setForm((f) => ({ ...f, classGrade: grade, subject: "", chapters: [] }))
    setSubjects([])
    setCatalog([])

    setLoadingSubjects(true)
    try {
      setSubjects(await fetchSubjects(grade))
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Failed to load subjects"
      )
    } finally {
      setLoadingSubjects(false)
    }
  }

  async function handleSubjectChange(subject: Subject) {
    const grade = form.classGrade
    if (!grade) return

    setForm((f) => ({ ...f, subject, chapters: [] }))
    setCatalog([])

    setLoadingChapters(true)
    try {
      setCatalog(await fetchChapters(grade, subject))
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Failed to load chapters"
      )
    } finally {
      setLoadingChapters(false)
    }
  }

  function toggleChapter(chapterNumber: number) {
    setForm((f) => ({
      ...f,
      chapters: f.chapters.includes(chapterNumber)
        ? f.chapters.filter((n) => n !== chapterNumber)
        : [...f.chapters, chapterNumber],
    }))
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()

    const trimmed = form.name.trim()
    if (!trimmed) {
      toast.error("Notebook name is required")
      return
    }
    if (!form.classGrade || !form.subject) {
      toast.error("Class and subject are required")
      return
    }
    if (form.chapters.length === 0) {
      toast.error("Select at least one chapter")
      return
    }

    setSubmitting(true)
    try {
      await createNotebook({
        name: trimmed,
        class_grade: form.classGrade,
        subject: form.subject,
        selected_chapter_numbers: form.chapters,
      })
      toast.success("Notebook created successfully.")
      onCreated()
      handleOpenChange(false)
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Failed to create notebook"
      )
    } finally {
      setSubmitting(false)
    }
  }

  const chaptersReady = Boolean(form.classGrade && form.subject)

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="flex max-h-[min(92vh,52rem)] flex-col gap-0 overflow-hidden p-0 sm:max-w-2xl lg:max-w-3xl">
        <form onSubmit={handleSubmit} className="flex min-h-0 flex-1 flex-col">
          <DialogHeader className="gap-1 border-b px-6 py-5">
            <DialogTitle className="text-xl">Create a New Notebook</DialogTitle>
            <DialogDescription>
              Set up a notebook with the class, subject and chapters you want to
              work with.
            </DialogDescription>
          </DialogHeader>

          <ScrollArea className="min-h-0 flex-1">
            <div className="grid gap-6 px-6 py-6">
              <div className="grid gap-2">
                <Label htmlFor="notebook-name">Notebook Name</Label>
                <Input
                  id="notebook-name"
                  className="h-10"
                  placeholder="e.g. Mid-Term Prep"
                  value={form.name}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, name: e.target.value }))
                  }
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <SelectField
                  label="Select Class"
                  value={form.classGrade}
                  placeholder="Select class"
                  loading={loadingGrades}
                  disabled={loadingGrades}
                  options={grades}
                  onChange={handleClassChange}
                />
                <SelectField
                  label="Subject"
                  value={form.subject}
                  placeholder="Select subject"
                  loading={loadingSubjects}
                  disabled={!form.classGrade || loadingSubjects}
                  options={subjects}
                  onChange={handleSubjectChange}
                />
              </div>

              <div className="grid gap-3">
                <div className="flex items-baseline justify-between gap-2">
                  <Label>
                    Chapters to include
                    <span className="ml-1 font-normal text-muted-foreground">
                      (You can add more later)
                    </span>
                  </Label>
                  {form.chapters.length > 0 && (
                    <span className="text-xs text-muted-foreground">
                      {form.chapters.length} selected
                    </span>
                  )}
                </div>

                <div className="rounded-xl border bg-muted/30 ring-1 ring-border/60">
                  <ScrollArea className="h-56 sm:h-64 lg:h-72">
                    <div className="grid gap-2 p-4 sm:grid-cols-2">
                      {!chaptersReady ? (
                        <p className="text-sm text-muted-foreground sm:col-span-2">
                          Select class and subject first
                        </p>
                      ) : loadingChapters ? (
                        <p className="flex items-center gap-2 text-sm text-muted-foreground sm:col-span-2">
                          <Loader2 className="size-4 animate-spin" />
                          Loading chapters…
                        </p>
                      ) : catalog.length === 0 ? (
                        <p className="text-sm text-muted-foreground sm:col-span-2">
                          No chapters available
                        </p>
                      ) : (
                        catalog.map((chapter) => {
                          const selected = form.chapters.includes(
                            chapter.chapter_number
                          )
                          return (
                            <button
                              key={chapter.chapter_number}
                              type="button"
                              onClick={() =>
                                toggleChapter(chapter.chapter_number)
                              }
                              className={cn(
                                "rounded-lg border px-3 py-2.5 text-left text-sm transition-colors",
                                selected
                                  ? "border-primary bg-primary/10 text-primary dark:bg-primary/15"
                                  : "border-border bg-background hover:bg-muted dark:bg-card"
                              )}
                            >
                              <span className="font-medium">
                                Chapter {chapter.chapter_number}
                              </span>
                              <span className="mt-0.5 block text-xs text-muted-foreground">
                                {chapter.chapter_name}
                              </span>
                            </button>
                          )
                        })
                      )}
                    </div>
                  </ScrollArea>
                </div>
              </div>
            </div>
          </ScrollArea>

          <DialogFooter className="mb-0 border-t bg-muted/30 px-6 py-4">
            <Button
              type="button"
              variant="outline"
              disabled={submitting}
              onClick={() => handleOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={submitting} className="min-w-36">
              {submitting && <Loader2 className="animate-spin" />}
              Create Notebook
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
