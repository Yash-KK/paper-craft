import * as React from "react"
import {
  Check,
  ChevronDown,
  FileText,
  ListChecks,
  Loader2,
  Plus,
  Sparkles,
  Trash2,
  X,
} from "lucide-react"
import { toast } from "sonner"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
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

type GeneratePaperFormProps = {
  notebook: NotebookListItem
  schoolName: string | null
  onGenerated?: () => void
  onCancel?: () => void
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
          <span className="truncate">{selected?.label ?? placeholder}</span>
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

const SECTION_TYPES: QuestionType[] = [
  "MCQ",
  "VSA",
  "SA",
  "LA",
  "CASE_STUDY",
]

function sectionLetter(index: number): string {
  return String.fromCharCode(65 + (index % 26))
}

export function GeneratePaperForm({
  notebook,
  schoolName,
  onGenerated,
  onCancel,
}: GeneratePaperFormProps) {
  const { data: samples = [], isPending: samplesLoading } = useSampleBlueprints()
  const generateMutation = useGenerateQuestionPaper()

  const [selectedSampleId, setSelectedSampleId] = React.useState<string | null>(
    null
  )
  const [selectedSampleLabel, setSelectedSampleLabel] = React.useState<
    string | null
  >(null)
  const [loadingSample, setLoadingSample] = React.useState(false)
  const [blueprint, setBlueprint] = React.useState<QuestionPaperBlueprint>(
    () => ({
      ...EMPTY_BLUEPRINT(),
      school_name: schoolName,
      subject: notebook.subject ?? "Mathematics",
      grade: classGradeToNumber(notebook.class_grade),
    })
  )
  const [teacherInstructions, setTeacherInstructions] = React.useState("")

  /** Only chapters chosen on the notebook — never the full catalog. */
  const chapters = notebook.selected_chapters
  const sampleSelected = Boolean(selectedSampleId)

  async function applySample(id: string, label: string) {
    if (chapters.length === 0) {
      toast.error("Select chapters on this notebook before applying a blueprint.")
      return
    }
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

  function updateSection(index: number, patch: Partial<BlueprintSection>) {
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

  function addChapterAllocation(
    sectionIndex: number,
    chapter: SelectedChapter
  ) {
    if (
      !chapters.some((c) => c.chapter_number === chapter.chapter_number)
    ) {
      toast.error("That chapter is not part of this notebook.")
      return
    }
    setBlueprint((prev) => ({
      ...prev,
      sections: prev.sections.map((section, i) => {
        if (i !== sectionIndex) return section
        if (
          section.chapter_allocations.some(
            (a) => a.chapter_number === chapter.chapter_number
          )
        ) {
          return section
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
          section_name: `Section ${sectionLetter(prev.sections.length)}`,
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
  const durationValue = blueprint.duration_minutes ?? ""
  const classSubjectLocked = `${notebook.class_grade ?? "Class"} — ${notebook.subject ?? "Subject"}`

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

    const invalidChapter = blueprint.sections.some((section) =>
      section.chapter_allocations.some(
        (alloc) =>
          alloc.chapter_number == null ||
          !chapters.some((c) => c.chapter_number === alloc.chapter_number)
      )
    )
    if (invalidChapter) {
      toast.error(
        "Marking scheme includes chapters outside this notebook. Remove them or rematch."
      )
      return
    }

    await generateMutation.mutateAsync({
      blueprint,
      selected_chapters: chapters,
      subject: blueprint.subject,
      grade: blueprint.grade,
      teacher_instructions: teacherInstructions.trim() || null,
    })
    onGenerated?.()
  }

  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col gap-6 px-4 py-6 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-1">
          <p className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
            Question paper
          </p>
          <h1 className="font-heading text-2xl font-semibold tracking-tight">
            Generate Paper
          </h1>
          <p className="text-sm text-muted-foreground">
            Choose a sample blueprint, review the scheme, then generate. Chapters
            are limited to this notebook&apos;s selection.
          </p>
        </div>
        <div className="flex shrink-0 gap-2">
          {onCancel ? (
            <Button type="button" variant="outline" onClick={onCancel}>
              Cancel
            </Button>
          ) : null}
          <Button
            type="button"
            className="gap-2 bg-emerald-600 text-white hover:bg-emerald-600/90"
            disabled={
              !sampleSelected ||
              generateMutation.isPending ||
              chapters.length === 0
            }
            onClick={() => void handleGenerate()}
          >
            {generateMutation.isPending ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <Sparkles className="size-4" />
            )}
            Generate Paper
          </Button>
        </div>
      </div>

      <div className="grid gap-2 rounded-2xl border bg-card p-4 sm:p-5">
        <Label>Sample Blueprint</Label>
        <DropdownMenu>
          <DropdownMenuTrigger
            disabled={samplesLoading || loadingSample || chapters.length === 0}
            render={
              <Button
                variant="outline"
                className="h-11 w-full justify-between font-normal sm:max-w-md"
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
        {chapters.length === 0 ? (
          <p className="text-xs text-destructive">
            Add chapters to this notebook before selecting a blueprint.
          </p>
        ) : (
          <p className="text-xs text-muted-foreground">
            Available chapters:{" "}
            {chapters
              .map((c) => `Ch ${c.chapter_number}`)
              .join(", ")}
          </p>
        )}
      </div>

      <section className="overflow-hidden rounded-2xl border bg-card">
        <div className="flex items-start gap-3 border-b bg-violet-500/10 px-4 py-3 sm:px-5">
          <span className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-xl bg-violet-600 text-white">
            <FileText className="size-4" />
          </span>
          <div>
            <h2 className="font-heading text-base font-semibold">Paper Details</h2>
            <p className="text-xs text-muted-foreground">
              Basic information for your paper.
            </p>
          </div>
        </div>

        <div className="grid gap-4 p-4 sm:grid-cols-2 sm:p-5">
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
            <div className="flex items-center gap-2">
              <Label>Class & Subject</Label>
              <Badge variant="secondary" className="h-5 px-1.5 text-[10px]">
                Locked
              </Badge>
            </div>
            <Input value={classSubjectLocked} disabled />
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
          <section className="overflow-hidden rounded-2xl border bg-card">
            <div className="flex items-start justify-between gap-3 border-b bg-violet-500/10 px-4 py-3 sm:px-5">
              <div className="flex items-start gap-3">
                <span className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-xl bg-violet-600 text-white">
                  <ListChecks className="size-4" />
                </span>
                <div>
                  <h2 className="font-heading text-base font-semibold">
                    Marking Scheme
                  </h2>
                  <p className="text-xs text-muted-foreground">
                    Sections, question types, and chapter distribution.
                  </p>
                </div>
              </div>
              <span
                className={cn(
                  "shrink-0 text-sm font-semibold",
                  marksMismatch
                    ? "text-destructive"
                    : "text-emerald-600 dark:text-emerald-400"
                )}
              >
                Total: {allocated}/{blueprint.total_marks}
              </span>
            </div>

            <div className="space-y-4 p-4 sm:p-5">
              {blueprint.sections.map((section, sectionIndex) => (
                <SectionCard
                  key={`${section.section_name}-${sectionIndex}`}
                  index={sectionIndex}
                  section={section}
                  chapters={chapters}
                  onChange={(patch) => updateSection(sectionIndex, patch)}
                  onUpdateAllocation={(allocIndex, patch) =>
                    updateAllocation(sectionIndex, allocIndex, patch)
                  }
                  onAddChapter={(ch) => addChapterAllocation(sectionIndex, ch)}
                  onRemoveAllocation={(allocIndex) =>
                    removeAllocation(sectionIndex, allocIndex)
                  }
                  onRemove={() => removeSection(sectionIndex)}
                />
              ))}

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
            </div>
          </section>

          <section className="overflow-hidden rounded-2xl border bg-card">
            <div className="border-b bg-violet-500/10 px-4 py-3 sm:px-5">
              <h2 className="font-heading text-base font-semibold">
                Teacher Instructions
              </h2>
              <p className="text-xs text-muted-foreground">
                Optional preferences for the AI. These do not change the
                blueprint — they are added to the generation prompt only.
              </p>
            </div>
            <div className="p-4 sm:p-5">
              <Textarea
                value={teacherInstructions}
                onChange={(e) => setTeacherInstructions(e.target.value)}
                placeholder={
                  "Focus more on application-based questions.\nAvoid direct textbook questions.\nInclude at least one challenging numerical."
                }
                className="min-h-32"
              />
            </div>
          </section>
        </>
      ) : (
        <div className="rounded-2xl border border-dashed px-4 py-16 text-center text-sm text-muted-foreground">
          Select a sample blueprint above to auto-fill paper details and the
          marking scheme. All fields stay editable afterward.
        </div>
      )}
    </div>
  )
}

type SectionCardProps = {
  index: number
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

function SectionCard({
  index,
  section,
  chapters,
  onChange,
  onUpdateAllocation,
  onAddChapter,
  onRemoveAllocation,
  onRemove,
}: SectionCardProps) {
  const total = sectionAllocatedMarks(section)
  const letter = sectionLetter(index)
  const availableToAdd = chapters.filter(
    (chapter) =>
      !section.chapter_allocations.some(
        (a) => a.chapter_number === chapter.chapter_number
      )
  )

  return (
    <div className="space-y-3 rounded-xl border bg-background p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="flex min-w-0 flex-1 items-start gap-3">
          <span className="mt-6 flex size-8 shrink-0 items-center justify-center rounded-full bg-violet-600 text-xs font-semibold text-white">
            {letter}
          </span>
          <div className="grid min-w-0 flex-1 gap-3 sm:grid-cols-3">
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
                    section.section_name ===
                      QUESTION_TYPE_LABELS[section.question_type] ||
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

      <div className="space-y-2 pl-0 sm:pl-11">
        <Label>Chapter Distribution</Label>
        <div className="flex flex-wrap gap-2">
          {section.chapter_allocations.map((alloc, allocIndex) => (
            <div
              key={`${alloc.chapter_name}-${allocIndex}`}
              className="flex items-center gap-1.5 rounded-full border border-violet-500/20 bg-violet-500/10 px-2.5 py-1.5 text-xs text-violet-800 dark:text-violet-200"
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
                className="h-6 w-12 border-0 bg-transparent px-1 text-xs shadow-none focus-visible:ring-0"
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
                className="rounded p-0.5 text-muted-foreground hover:bg-violet-500/20 hover:text-foreground"
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
                  className="h-8 gap-1.5 rounded-full text-xs"
                />
              }
            >
              <Plus className="size-3.5" />
              Add Chapter
            </DropdownMenuTrigger>
            <DropdownMenuContent className="z-100 max-h-60">
              {availableToAdd.map((chapter) => (
                <DropdownMenuItem
                  key={chapter.chapter_number}
                  onClick={() => onAddChapter(chapter)}
                >
                  Ch {chapter.chapter_number}: {chapter.chapter_name}
                </DropdownMenuItem>
              ))}
              {availableToAdd.length === 0 ? (
                <DropdownMenuItem disabled>
                  {chapters.length === 0
                    ? "No notebook chapters"
                    : "All notebook chapters added"}
                </DropdownMenuItem>
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
