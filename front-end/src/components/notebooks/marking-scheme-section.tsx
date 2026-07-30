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
  groupChapterAllocations,
  sectionAllocatedMarks,
  sectionLetter,
  type BlueprintSection,
  type QuestionType,
} from "@/lib/types/generation"
import { cn } from "@/lib/utils"

type MarkingSchemeSectionProps = {
  index: number
  section: BlueprintSection
  chapters: SelectedChapter[]
  showMarks?: boolean
  onChange: (patch: Partial<BlueprintSection>) => void
  onUpdateChapterQuestionCount: (
    allocationIndexes: number[],
    questionCount: number
  ) => void
  onAddChapter: (chapter: SelectedChapter) => void
  onRemoveChapter: (allocationIndexes: number[]) => void
  onRemove: () => void
}

export function MarkingSchemeSection({
  index,
  section,
  chapters,
  showMarks = true,
  onChange,
  onUpdateChapterQuestionCount,
  onAddChapter,
  onRemoveChapter,
  onRemove,
}: MarkingSchemeSectionProps) {
  const total = sectionAllocatedMarks(section)
  const questionCount = section.chapter_allocations.reduce(
    (sum, alloc) => sum + alloc.question_count,
    0
  )
  const chapterGroups = groupChapterAllocations(section.chapter_allocations)
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
          <div
            className={cn(
              "grid min-w-0 flex-1 gap-3",
              showMarks ? "sm:grid-cols-3" : "sm:grid-cols-2"
            )}
          >
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
            {showMarks ? (
              <div className="grid gap-2">
                <Label>Marks Each</Label>
                <Input
                  type="number"
                  min={0.5}
                  step={0.5}
                  value={section.marks_each ?? ""}
                  onChange={(e) =>
                    onChange({
                      marks_each:
                        e.target.value === ""
                          ? null
                          : Number(e.target.value) || 0,
                    })
                  }
                />
              </div>
            ) : null}
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

      {section.section_instructions ? (
        <p className="pl-0 text-xs text-muted-foreground sm:pl-11">
          {section.section_instructions}
        </p>
      ) : null}

      <div className="space-y-2 pl-0 sm:pl-11">
        <Label>Chapter Distribution</Label>
        <div className="flex flex-wrap gap-2">
          {chapterGroups.map((group) => (
            <div
              key={group.key}
              className="flex items-center gap-1 rounded-full border border-violet-500/20 bg-violet-500/10 px-2.5 py-1.5 text-xs text-violet-800 dark:text-violet-200"
            >
              <span className="font-medium">
                {group.allocation.chapter_number != null
                  ? `Ch ${group.allocation.chapter_number}`
                  : group.allocation.chapter_name}
                :
              </span>
              <Input
                type="number"
                min={1}
                aria-label={`Questions from ${group.allocation.chapter_name}`}
                className="h-6 w-8 border-0 bg-transparent p-0 text-center text-xs shadow-none"
                value={group.questionCount}
                onChange={(e) =>
                  onUpdateChapterQuestionCount(
                    group.allocationIndexes,
                    Math.max(1, Number(e.target.value) || 1)
                  )
                }
              />
              <span className="text-muted-foreground">Qs</span>
              <Button
                type="button"
                variant="ghost"
                size="icon-xs"
                className="text-muted-foreground hover:bg-violet-500/20 hover:text-foreground"
                aria-label="Remove chapter"
                onClick={() => onRemoveChapter(group.allocationIndexes)}
              >
                <X className="size-3.5" />
              </Button>
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
          {showMarks && total != null
            ? `${total} marks`
            : `${questionCount} questions`}
        </span>
      </div>
    </div>
  )
}
