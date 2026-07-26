import * as React from "react"
import { Check, ChevronDown, Loader2, Plus, Trash2, X } from "lucide-react"
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
import { Textarea } from "@/components/ui/textarea"
import {
  useGenerateQuestionPaper,
  useSampleBlueprints,
} from "@/hooks/use-sample-blueprints"
import { fetchSampleBlueprint } from "@/lib/api"
import type { NotebookListItem, SelectedChapter } from "@/lib/types/notebook"
import {
  blueprintAllocatedMarks,
  classGradeToNumber,
  DURATION_OPTIONS,
  QUESTION_TYPE_LABELS,
  rematchBlueprintChapters,
  sectionAllocatedMarks,
  type BlueprintSection,
  type ChapterAllocation,
  type QuestionPaperBlueprint,
  type QuestionType,
} from "@/lib/types/generation"
import { cn } from "@/lib/utils"

type GeneratePaperDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  notebook: NotebookListItem
  schoolName: string | null
}

const EMPTY_BLUEPRINT = (): QuestionPaperBlueprint => ({
  school_name: null,
  exam_title: null,
  subject: "Mathematics",
  grade: 10,
  total_marks: 40,
  duration_minutes: 90,
  exam_date: null,
  general_instructions: [],
  sections: [],
  blooms_targets: null,
})

function cloneBlueprint(bp: QuestionPaperBlueprint): QuestionPaperBlueprint {
  return structuredClone(bp)
}

type SelectFieldProps<T extends string | number> = {
  label: string
  value: T | ""
  placeholder: string
  disabled?: boolean
  options: { value: T; label: string }[]
  onChange: (value: T) => void
}

function SelectField<T extends string | number>({
  label,
  value,
  placeholder,
  disabled,
  options,
  onChange,
}: SelectFieldProps<T>) {
  const selected = options.find((o) => o.value === value)
  return (
    <div className="grid gap-2">
      <Label>{label}</Label>
      <DropdownMenu>
        <DropdownMenuTrigger
          disabled={disabled}
          render={
            <Button
              variant="outline"
              className="h-10 w-full justify-between font-normal"
            />
          }
        >
          <span className="truncate">
            {selected?.label ?? placeholder}
          </span>
          <ChevronDown className="size-4 shrink-0 opacity-50" />
        </DropdownMenuTrigger>
        <DropdownMenuContent className="z-100 max-h-60 w-(--anchor-width)">
          {options.map((option) => (
            <DropdownMenuItem
              key={String(option.value)}
              onClick={() => onChange(option.value)}
            >
              {option.label}
              {value === option.value ? (
                <Check className="ml-auto size-4" />
              ) : null}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}

export function GeneratePaperDialog({
  open,
  onOpenChange,
  notebook,
  schoolName,
}: GeneratePaperDialogProps) {
  const { data: samples = [], isPending: samplesLoading } =
    useSampleBlueprints(open)
  const generateMutation = useGenerateQuestionPaper()

  const [selectedSampleId, setSelectedSampleId] = React.useState<string | null>(
    null
  )
  const [selectedSampleLabel, setSelectedSampleLabel] = React.useState<
    string | null
  >(null)
  const [loadingSample, setLoadingSample] = React.useState(false)
  const [blueprint, setBlueprint] = React.useState<QuestionPaperBlueprint>(
    EMPTY_BLUEPRINT
  )
  const [teacherInstructions, setTeacherInstructions] = React.useState("")

  const chapters = notebook.selected_chapters
  const sampleSelected = Boolean(selectedSampleId)

  React.useEffect(() => {
    if (!open) return
    setSelectedSampleId(null)
    setSelectedSampleLabel(null)
    setTeacherInstructions("")
    setBlueprint({
      ...EMPTY_BLUEPRINT(),
      school_name: schoolName,
      subject: notebook.subject ?? "Mathematics",
      grade: classGradeToNumber(notebook.class_grade),
    })
  }, [open, schoolName, notebook.subject, notebook.class_grade])

  async function applySample(id: string, label: string) {
    setLoadingSample(true)
    try {
      const detail = await fetchSampleBlueprint(id)
      const rematched = rematchBlueprintChapters(
        cloneBlueprint(detail.blueprint),
        chapters
      )
      setBlueprint({
        ...rematched,
        school_name: schoolName ?? rematched.school_name,
        subject: notebook.subject ?? rematched.subject,
        grade: classGradeToNumber(notebook.class_grade) || rematched.grade,
      })
      setSelectedSampleId(id)
      setSelectedSampleLabel(label)
      setTeacherInstructions("")
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Failed to load sample blueprint"
      )
    } finally {
      setLoadingSample(false)
    }
  }

  function updateSection(
    index: number,
    patch: Partial<BlueprintSection>
  ) {
    setBlueprint((prev) => ({
      ...prev,
      sections: prev.sections.map((section, i) =>
        i === index ? { ...section, ...patch } : section
      ),
    }))
  }

  function updateAllocation(
    sectionIndex: number,
    allocIndex: number,
    patch: Partial<ChapterAllocation>
  ) {
    setBlueprint((prev) => ({
      ...prev,
      sections: prev.sections.map((section, i) => {
        if (i !== sectionIndex) return section
        return {
          ...section,
          chapter_allocations: section.chapter_allocations.map((alloc, j) =>
            j === allocIndex ? { ...alloc, ...patch } : alloc
          ),
        }
      }),
    }))
  }

  function addChapterAllocation(sectionIndex: number, chapter: SelectedChapter) {
    setBlueprint((prev) => ({
      ...prev,
      sections: prev.sections.map((section, i) => {
        if (i !== sectionIndex) return section
        const existing = section.chapter_allocations.find(
          (a) => a.chapter_number === chapter.chapter_number
        )
        if (existing) {
          return {
            ...section,
            chapter_allocations: section.chapter_allocations.map((a) =>
              a.chapter_number === chapter.chapter_number
                ? { ...a, question_count: a.question_count + 1 }
                : a
            ),
          }
        }
        return {
          ...section,
          chapter_allocations: [
            ...section.chapter_allocations,
            {
              chapter_number: chapter.chapter_number,
              chapter_name: chapter.chapter_name,
              question_count: 1,
              blooms_level: null,
              has_internal_choice: false,
              is_assertion_reason: false,
              marks: null,
            },
          ],
        }
      }),
    }))
  }

  function removeAllocation(sectionIndex: number, allocIndex: number) {
    setBlueprint((prev) => ({
      ...prev,
      sections: prev.sections.map((section, i) => {
        if (i !== sectionIndex) return section
        return {
          ...section,
          chapter_allocations: section.chapter_allocations.filter(
            (_, j) => j !== allocIndex
          ),
        }
      }),
    }))
  }

  function addSection() {
    setBlueprint((prev) => ({
      ...prev,
      sections: [
        ...prev.sections,
        {
          section_name: "MCQ",
          question_type: "MCQ",
          marks_each: 1,
          chapter_allocations: [],
          section_instructions: null,
        },
      ],
    }))
  }

  function removeSection(index: number) {
    setBlueprint((prev) => ({
      ...prev,
      sections: prev.sections.filter((_, i) => i !== index),
    }))
  }

  const allocated = blueprintAllocatedMarks(blueprint)
  const marksMismatch = allocated !== blueprint.total_marks

  async function handleGenerate() {
    if (!sampleSelected) {
      toast.error("Select a sample blueprint first.")
      return
    }
    if (chapters.length === 0) {
      toast.error("Select at least one chapter on the notebook first.")
      return
    }
    if (blueprint.sections.length === 0) {
      toast.error("Add at least one section to the marking scheme.")
      return
    }

    await generateMutation.mutateAsync({
      blueprint,
      selected_chapters: chapters,
      subject: blueprint.subject,
      grade: blueprint.grade,
      teacher_instructions: teacherInstructions.trim() || null,
    })
    onOpenChange(false)
  }

  const durationValue = blueprint.duration_minutes ?? ""
  const classSubjectLocked = `${notebook.class_grade ?? "Class"} — ${notebook.subject ?? "Subject"}`

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[90vh] w-full max-w-3xl flex-col gap-0 overflow-hidden p-0 sm:max-w-3xl">
        <DialogHeader className="shrink-0 border-b px-6 py-4">
          <DialogTitle>Generate Question Paper</DialogTitle>
          <DialogDescription>
            Pick a sample blueprint, adjust the marking scheme, then add optional
            teacher instructions before generating.
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="min-h-0 flex-1">
          <div className="space-y-8 px-6 py-5">
            <section className="space-y-4">
              <h3 className="font-heading text-sm font-semibold tracking-wide uppercase">
                Paper Details
              </h3>

              <div className="grid gap-2">
                <Label>Sample Blueprints</Label>
                <DropdownMenu>
                  <DropdownMenuTrigger
                    disabled={samplesLoading || loadingSample}
                    render={
                      <Button
                        variant="outline"
                        className="h-10 w-full justify-between font-normal"
                      />
                    }
                  >
                    <span className="truncate">
                      {loadingSample
                        ? "Loading blueprint…"
                        : selectedSampleLabel ?? "Select a sample blueprint"}
                    </span>
                    {loadingSample ? (
                      <Loader2 className="size-4 shrink-0 animate-spin opacity-50" />
                    ) : (
                      <ChevronDown className="size-4 shrink-0 opacity-50" />
                    )}
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="z-100 max-h-60 w-(--anchor-width)">
                    {samples.length === 0 ? (
                      <DropdownMenuItem disabled>
                        No sample blueprints available
                      </DropdownMenuItem>
                    ) : (
                      samples.map((sample) => (
                        <DropdownMenuItem
                          key={sample.id}
                          onClick={() => void applySample(sample.id, sample.label)}
                        >
                          {sample.label}
                          {selectedSampleId === sample.id ? (
                            <Check className="ml-auto size-4" />
                          ) : null}
                        </DropdownMenuItem>
                      ))
                    )}
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="grid gap-2 sm:col-span-2">
                  <Label htmlFor="school-name">School Name</Label>
                  <Input
                    id="school-name"
                    value={blueprint.school_name ?? ""}
                    onChange={(e) =>
                      setBlueprint((prev) => ({
                        ...prev,
                        school_name: e.target.value || null,
                      }))
                    }
                    disabled={!sampleSelected}
                  />
                </div>

                <div className="grid gap-2 sm:col-span-2">
                  <Label>Class & Subject</Label>
                  <Input value={classSubjectLocked} disabled />
                  <p className="text-[11px] text-muted-foreground">Locked to this notebook</p>
                </div>

                <div className="grid gap-2 sm:col-span-2">
                  <Label htmlFor="exam-title">Exam Title</Label>
                  <Input
                    id="exam-title"
                    value={blueprint.exam_title ?? ""}
                    onChange={(e) =>
                      setBlueprint((prev) => ({
                        ...prev,
                        exam_title: e.target.value || null,
                      }))
                    }
                    disabled={!sampleSelected}
                  />
                </div>

                <SelectField
                  label="Duration"
                  value={durationValue}
                  placeholder="Select duration"
                  disabled={!sampleSelected}
                  options={DURATION_OPTIONS.map((d) => ({
                    value: d.minutes,
                    label: d.label,
                  }))}
                  onChange={(minutes) =>
                    setBlueprint((prev) => ({
                      ...prev,
                      duration_minutes: minutes,
                    }))
                  }
                />

                <div className="grid gap-2">
                  <Label htmlFor="total-marks">Total Marks</Label>
                  <Input
                    id="total-marks"
                    type="number"
                    min={1}
                    value={blueprint.total_marks}
                    onChange={(e) =>
                      setBlueprint((prev) => ({
                        ...prev,
                        total_marks: Number(e.target.value) || 0,
                      }))
                    }
                    disabled={!sampleSelected}
                  />
                </div>

                <div className="grid gap-2 sm:col-span-2">
                  <Label htmlFor="exam-date">Exam Date</Label>
                  <Input
                    id="exam-date"
                    type="date"
                    value={blueprint.exam_date ?? ""}
                    onChange={(e) =>
                      setBlueprint((prev) => ({
                        ...prev,
                        exam_date: e.target.value || null,
                      }))
                    }
                    disabled={!sampleSelected}
                  />
                </div>
              </div>
            </section>

            {sampleSelected ? (
              <>
                <section className="space-y-4">
                  <div className="flex items-center justify-between gap-3">
                    <h3 className="font-heading text-sm font-semibold tracking-wide uppercase">
                      Marking Scheme
                    </h3>
                    <span
                      className={cn(
                        "text-xs font-medium",
                        marksMismatch
                          ? "text-destructive"
                          : "text-emerald-600 dark:text-emerald-400"
                      )}
                    >
                      Total: {allocated}/{blueprint.total_marks}
                    </span>
                  </div>

                  <div className="space-y-4">
                    {blueprint.sections.map((section, sectionIndex) => (
                      <SectionCard
                        key={`${section.section_name}-${sectionIndex}`}
                        section={section}
                        chapters={chapters}
                        onChange={(patch) => updateSection(sectionIndex, patch)}
                        onUpdateAllocation={(allocIndex, patch) =>
                          updateAllocation(sectionIndex, allocIndex, patch)
                        }
                        onAddChapter={(ch) =>
                          addChapterAllocation(sectionIndex, ch)
                        }
                        onRemoveAllocation={(allocIndex) =>
                          removeAllocation(sectionIndex, allocIndex)
                        }
                        onRemove={() => removeSection(sectionIndex)}
                      />
                    ))}
                  </div>

                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="gap-1.5"
                    onClick={addSection}
                  >
                    <Plus className="size-3.5" />
                    Add Section
                  </Button>
                </section>

                <section className="space-y-3">
                  <h3 className="font-heading text-sm font-semibold tracking-wide uppercase">
                    Teacher Instructions
                  </h3>
                  <p className="text-xs text-muted-foreground">
                    Optional preferences for the AI. These do not change the
                    blueprint structure — they are added to the generation
                    prompt only.
                  </p>
                  <Textarea
                    value={teacherInstructions}
                    onChange={(e) => setTeacherInstructions(e.target.value)}
                    placeholder={
                      "Focus more on application-based questions.\nAvoid direct textbook questions.\nInclude at least one challenging numerical."
                    }
                    className="min-h-28"
                  />
                </section>
              </>
            ) : (
              <p className="rounded-lg border border-dashed px-4 py-8 text-center text-sm text-muted-foreground">
                Select a sample blueprint to auto-fill paper details and the
                marking scheme.
              </p>
            )}
          </div>
        </ScrollArea>

        <DialogFooter className="shrink-0 border-t px-6 py-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
          >
            Cancel
          </Button>
          <Button
            type="button"
            className="gap-2 bg-violet-600 text-white hover:bg-violet-600/90"
            disabled={
              !sampleSelected ||
              generateMutation.isPending ||
              chapters.length === 0
            }
            onClick={() => void handleGenerate()}
          >
            {generateMutation.isPending ? (
              <Loader2 className="size-4 animate-spin" />
            ) : null}
            Generate Paper
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

type SectionCardProps = {
  section: BlueprintSection
  chapters: SelectedChapter[]
  onChange: (patch: Partial<BlueprintSection>) => void
  onUpdateAllocation: (
    allocIndex: number,
    patch: Partial<ChapterAllocation>
  ) => void
  onAddChapter: (chapter: SelectedChapter) => void
  onRemoveAllocation: (allocIndex: number) => void
  onRemove: () => void
}

const SECTION_TYPES: QuestionType[] = [
  "MCQ",
  "VSA",
  "SA",
  "LA",
  "CASE_STUDY",
]

function SectionCard({
  section,
  chapters,
  onChange,
  onUpdateAllocation,
  onAddChapter,
  onRemoveAllocation,
  onRemove,
}: SectionCardProps) {
  const total = sectionAllocatedMarks(section)

  return (
    <div className="space-y-3 rounded-xl border bg-card p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="grid flex-1 gap-3 sm:grid-cols-3">
          <div className="grid gap-2">
            <Label>Section Name</Label>
            <Input
              value={section.section_name}
              onChange={(e) => onChange({ section_name: e.target.value })}
            />
          </div>
          <SelectField
            label="Question Type"
            value={section.question_type}
            placeholder="Type"
            options={SECTION_TYPES.map((t) => ({
              value: t,
              label: QUESTION_TYPE_LABELS[t],
            }))}
            onChange={(question_type) =>
              onChange({
                question_type,
                section_name:
                  section.section_name === QUESTION_TYPE_LABELS[section.question_type] ||
                  section.section_name === section.question_type
                    ? QUESTION_TYPE_LABELS[question_type]
                    : section.section_name,
              })
            }
          />
          <div className="grid gap-2">
            <Label>Marks Each</Label>
            <Input
              type="number"
              min={0.5}
              step={0.5}
              value={section.marks_each}
              onChange={(e) =>
                onChange({ marks_each: Number(e.target.value) || 0 })
              }
            />
          </div>
        </div>
        <Button
          type="button"
          variant="ghost"
          size="icon-sm"
          className="mt-6 shrink-0 text-muted-foreground"
          aria-label="Remove section"
          onClick={onRemove}
        >
          <Trash2 className="size-4" />
        </Button>
      </div>

      <div className="space-y-2">
        <Label>Chapter Distribution</Label>
        <div className="flex flex-wrap gap-2">
          {section.chapter_allocations.map((alloc, allocIndex) => (
            <div
              key={`${alloc.chapter_name}-${allocIndex}`}
              className="flex items-center gap-1.5 rounded-lg border bg-muted/40 px-2 py-1.5 text-xs"
            >
              <span className="font-medium">
                {alloc.chapter_number != null
                  ? `Ch ${alloc.chapter_number}`
                  : alloc.chapter_name}
                :
              </span>
              <Input
                type="number"
                min={1}
                className="h-7 w-14 px-1.5 text-xs"
                value={alloc.question_count}
                onChange={(e) =>
                  onUpdateAllocation(allocIndex, {
                    question_count: Math.max(1, Number(e.target.value) || 1),
                  })
                }
              />
              <span className="text-muted-foreground">Qs</span>
              <button
                type="button"
                className="rounded p-0.5 text-muted-foreground hover:bg-muted hover:text-foreground"
                aria-label="Remove chapter"
                onClick={() => onRemoveAllocation(allocIndex)}
              >
                <X className="size-3.5" />
              </button>
            </div>
          ))}

          <DropdownMenu>
            <DropdownMenuTrigger
              disabled={chapters.length === 0}
              render={
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="h-8 gap-1.5 text-xs"
                />
              }
            >
              <Plus className="size-3.5" />
              Add Chapter
            </DropdownMenuTrigger>
            <DropdownMenuContent className="z-100 max-h-60">
              {chapters
                .filter(
                  (chapter) =>
                    !section.chapter_allocations.some(
                      (a) => a.chapter_number === chapter.chapter_number
                    )
                )
                .map((chapter) => (
                  <DropdownMenuItem
                    key={chapter.chapter_number}
                    onClick={() => onAddChapter(chapter)}
                  >
                    Ch {chapter.chapter_number}: {chapter.chapter_name}
                  </DropdownMenuItem>
                ))}
              {chapters.every((chapter) =>
                section.chapter_allocations.some(
                  (a) => a.chapter_number === chapter.chapter_number
                )
              ) ? (
                <DropdownMenuItem disabled>All chapters added</DropdownMenuItem>
              ) : null}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      <div className="flex justify-end">
        <span className="rounded-md bg-emerald-500/10 px-2 py-1 text-xs font-medium text-emerald-700 dark:text-emerald-300">
          {total} marks
        </span>
      </div>
    </div>
  )
}
