import { Plus, Trash2, X } from "lucide-react"

import { MenuSelect } from "@/components/ui/menu-select"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import type { SelectedChapter } from "@/lib/types/notebook"
import {
  QUESTION_TYPE_LABELS,
  SECTION_QUESTION_TYPES,
  sectionAllocatedMarks,
  sectionLetter,
  type BlueprintSection,
  type ChapterAllocation,
  type QuestionType,
} from "@/lib/types/generation"

type MarkingSchemeSectionProps = {
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

export function MarkingSchemeSection({
  index,
  section,
  chapters,
  onChange,
  onUpdateAllocation,
  onAddChapter,
  onRemoveAllocation,
  onRemove,
}: MarkingSchemeSectionProps) {
  const total = sectionAllocatedMarks(section)
  const availableToAdd = chapters.filter(
    (chapter) =>
      !section.chapter_allocations.some(
        (alloc) => alloc.chapter_number === chapter.chapter_number
      )
  )

  function handleTypeChange(question_type: QuestionType) {
    const shouldRename =
      section.section_name === QUESTION_TYPE_LABELS[section.question_type] ||
      section.section_name === section.question_type
    onChange({
      question_type,
      section_name: shouldRename
        ? QUESTION_TYPE_LABELS[question_type]
        : section.section_name,
    })
  }

  return (
    <div className="space-y-3 rounded-xl border bg-background p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="flex min-w-0 flex-1 items-start gap-3">
          <span className="mt-6 flex size-8 shrink-0 items-center justify-center rounded-full bg-violet-600 text-xs font-semibold text-white">
            {sectionLetter(index)}
          </span>
          <div className="grid min-w-0 flex-1 gap-3 sm:grid-cols-3">
            <div className="grid gap-2">
              <Label>Section Name</Label>
              <Input
                value={section.section_name}
                onChange={(e) => onChange({ section_name: e.target.value })}
              />
            </div>
            <MenuSelect
              label="Question Type"
              value={section.question_type}
              placeholder="Type"
              options={SECTION_QUESTION_TYPES.map((type) => ({
                value: type,
                label: QUESTION_TYPE_LABELS[type],
              }))}
              onChange={handleTypeChange}
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
              className="flex items-center gap-1 rounded-full border border-violet-500/20 bg-violet-500/10 px-2.5 py-1.5 text-xs text-violet-800 dark:text-violet-200"
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
                className="h-6 w-7 border-0 bg-transparent p-0 text-center text-xs shadow-none focus-visible:ring-0"
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
