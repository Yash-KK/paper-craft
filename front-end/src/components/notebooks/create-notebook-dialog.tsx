import * as React from "react"
import { Check, Loader2 } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  createNotebook,
  fetchChapters,
  fetchGrades,
  fetchSubjects,
} from "@/lib/api"
import { NOTEBOOK_COLORS } from "@/lib/types/notebook"
import type { ClassGrade, Subject } from "@/lib/types/notebook"
import { cn } from "@/lib/utils"

type CreateNotebookDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  onCreated: () => void
}

const selectClassName =
  "h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-input/30"

const EMPTY_FORM = {
  name: "",
  classGrade: "" as ClassGrade | "",
  subject: "" as Subject | "",
  chapters: [] as number[],
  colorHex: NOTEBOOK_COLORS[0],
}

export function CreateNotebookDialog({
  open,
  onOpenChange,
  onCreated,
}: CreateNotebookDialogProps) {
  const [form, setForm] = React.useState(EMPTY_FORM)
  const [grades, setGrades] = React.useState<ClassGrade[]>([])
  const [subjects, setSubjects] = React.useState<Subject[]>([])
  const [catalog, setCatalog] = React.useState<
    { chapter_number: number; chapter_name: string }[]
  >([])
  const [loadingGrades, setLoadingGrades] = React.useState(false)
  const [loadingSubjects, setLoadingSubjects] = React.useState(false)
  const [loadingChapters, setLoadingChapters] = React.useState(false)
  const [submitting, setSubmitting] = React.useState(false)

  function handleOpenChange(next: boolean) {
    if (!next) {
      setForm(EMPTY_FORM)
      setSubjects([])
      setCatalog([])
    }
    onOpenChange(next)
  }

  React.useEffect(() => {
    if (!open) return

    setLoadingGrades(true)
    fetchGrades()
      .then(setGrades)
      .catch((err) =>
        toast.error(err instanceof Error ? err.message : "Failed to load classes")
      )
      .finally(() => setLoadingGrades(false))
  }, [open])

  async function handleClassChange(grade: ClassGrade | "") {
    setForm((f) => ({ ...f, classGrade: grade, subject: "", chapters: [] }))
    setSubjects([])
    setCatalog([])

    if (!grade) return

    setLoadingSubjects(true)
    try {
      setSubjects(await fetchSubjects(grade))
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to load subjects")
    } finally {
      setLoadingSubjects(false)
    }
  }

  async function handleSubjectChange(subject: Subject | "") {
    setForm((f) => ({ ...f, subject, chapters: [] }))
    setCatalog([])

    if (!form.classGrade || !subject) return

    setLoadingChapters(true)
    try {
      setCatalog(await fetchChapters(form.classGrade, subject))
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to load chapters")
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
        color_hex: form.colorHex,
        selected_chapter_numbers: form.chapters,
      })
      toast.success("Notebook created successfully.")
      onCreated()
      handleOpenChange(false)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to create notebook")
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-lg">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Create a New Notebook</DialogTitle>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="notebook-name">Notebook Name</Label>
              <Input
                id="notebook-name"
                placeholder="e.g. Mid-Term Prep — Math"
                value={form.name}
                onChange={(e) =>
                  setForm((f) => ({ ...f, name: e.target.value }))
                }
              />
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="grid gap-2">
                <Label htmlFor="class-grade">Select Class</Label>
                <select
                  id="class-grade"
                  className={selectClassName}
                  value={form.classGrade}
                  disabled={loadingGrades}
                  onChange={(e) =>
                    void handleClassChange(e.target.value as ClassGrade | "")
                  }
                >
                  <option value="">
                    {loadingGrades ? "Loading…" : "Select class"}
                  </option>
                  {grades.map((grade) => (
                    <option key={grade} value={grade}>
                      {grade}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="subject">Subject</Label>
                <select
                  id="subject"
                  className={selectClassName}
                  value={form.subject}
                  disabled={!form.classGrade || loadingSubjects}
                  onChange={(e) =>
                    void handleSubjectChange(e.target.value as Subject | "")
                  }
                >
                  <option value="">
                    {loadingSubjects ? "Loading…" : "Select subject"}
                  </option>
                  {subjects.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid gap-2">
              <Label>
                Chapters to include
                <span className="ml-1 font-normal text-muted-foreground">
                  (You can add more later)
                </span>
              </Label>
              <div className="grid max-h-48 gap-2 overflow-y-auto sm:grid-cols-2">
                {!form.classGrade || !form.subject ? (
                  <p className="text-sm text-muted-foreground sm:col-span-2">
                    Select class and subject first
                  </p>
                ) : loadingChapters ? (
                  <p className="text-sm text-muted-foreground sm:col-span-2">
                    Loading chapters…
                  </p>
                ) : catalog.length === 0 ? (
                  <p className="text-sm text-muted-foreground sm:col-span-2">
                    No chapters available
                  </p>
                ) : (
                  catalog.map((chapter) => {
                    const selected = form.chapters.includes(chapter.chapter_number)
                    return (
                      <button
                        key={chapter.chapter_number}
                        type="button"
                        onClick={() => toggleChapter(chapter.chapter_number)}
                        className={cn(
                          "rounded-full border px-3 py-1.5 text-left text-xs transition-colors",
                          selected
                            ? "border-violet-500 bg-violet-500/10 text-violet-700 dark:text-violet-300"
                            : "border-border hover:bg-muted"
                        )}
                      >
                        Chapter {chapter.chapter_number}: {chapter.chapter_name}
                      </button>
                    )
                  })
                )}
              </div>
            </div>

            <div className="grid gap-2">
              <Label>Notebook Color</Label>
              <div className="flex flex-wrap gap-2">
                {NOTEBOOK_COLORS.map((color) => (
                  <button
                    key={color}
                    type="button"
                    aria-label={`Color ${color}`}
                    onClick={() => setForm((f) => ({ ...f, colorHex: color }))}
                    className="flex size-8 items-center justify-center rounded-full"
                    style={{ backgroundColor: color }}
                  >
                    {form.colorHex === color && (
                      <Check className="size-4 text-white" />
                    )}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              disabled={submitting}
              onClick={() => handleOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={submitting}>
              {submitting && <Loader2 className="animate-spin" />}
              Create Notebook
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
