import type {
  Board,
  ClassGrade,
  SelectedChapter,
  Subject,
} from "@/lib/types/notebook"

export type BlueprintKind = "EXAM" | "REVISION_SHEET"

export type QuestionType =
  | "MCQ"
  | "ASSERTION_REASON"
  | "VSA"
  | "SA"
  | "LA"
  | "CASE_STUDY"
  | "FILL_IN_THE_BLANK"
  | "TRUE_FALSE"
  | "OTHER"

export type BloomsLevel =
  | "REMEMBERING"
  | "UNDERSTANDING"
  | "APPLYING"
  | "ANALYSING"
  | "EVALUATING"
  | "CREATING"

export type ChapterAllocation = {
  chapter_number: number | null
  chapter_name: string
  question_count: number
  blooms_level: BloomsLevel | null
  has_internal_choice: boolean
  is_assertion_reason: boolean
  marks?: number | null
}

export type BlueprintSubPart = {
  label: string
  marks?: number | null
}

export type BlueprintSection = {
  section_name: string
  question_type: QuestionType
  marks_each: number | null
  chapter_allocations: ChapterAllocation[]
  section_instructions: string | null
  sub_parts?: BlueprintSubPart[]
  section_total_marks?: number | null
  question_count?: number
}

export type QuestionPaperBlueprint = {
  kind: BlueprintKind
  school_name: string | null
  exam_title: string | null
  subject: string
  grade: number
  total_marks: number | null
  duration_minutes: number | null
  exam_date: string | null
  general_instructions: string[]
  learning_outcomes: string[]
  generation_rules: string[]
  sections: BlueprintSection[]
  blooms_targets: Partial<Record<BloomsLevel, number>> | null
  metadata?: Record<string, unknown>
  allocated_marks?: number | null
  is_mark_based?: boolean
}

export type SampleBlueprintSummary = {
  id: string
  slug: string
  label: string
  kind: BlueprintKind
  total_marks: number | null
  board: Board | null
  subject: Subject | null
  grade: ClassGrade | null
  format_reference_uri: string | null
}

export type SampleBlueprintDetail = SampleBlueprintSummary & {
  blueprint: QuestionPaperBlueprint
}

export type GeneratePaperPayload = {
  blueprint: QuestionPaperBlueprint
  selected_chapters: SelectedChapter[]
  subject: string
  grade: number
  teacher_instructions?: string | null
  format_reference_uri?: string | null
  format_reference?: File | null
}

export type GenerationResult = {
  blueprint: QuestionPaperBlueprint
  final_paper: Record<string, unknown>
  final_answer_key: Record<string, unknown>
  generated_items: Record<string, unknown>[]
  format_reference_uri: string
  format_reference_is_default: boolean
}

export const QUESTION_TYPE_LABELS: Record<QuestionType, string> = {
  MCQ: "MCQ",
  ASSERTION_REASON: "Assertion-Reason",
  VSA: "VSA",
  SA: "SA",
  LA: "LA",
  CASE_STUDY: "CBQ",
  FILL_IN_THE_BLANK: "Fill in the Blank",
  TRUE_FALSE: "True / False",
  OTHER: "Other",
}

export const SECTION_QUESTION_TYPES: QuestionType[] = [
  "MCQ",
  "ASSERTION_REASON",
  "VSA",
  "SA",
  "LA",
  "CASE_STUDY",
]

export const DURATION_OPTIONS: { label: string; minutes: number }[] = [
  { label: "1 Hour", minutes: 60 },
  { label: "1.5 Hours", minutes: 90 },
  { label: "2 Hours", minutes: 120 },
  { label: "2.5 Hours", minutes: 150 },
  { label: "3 Hours", minutes: 180 },
]

export function isMarkBasedBlueprint(
  blueprint: Pick<QuestionPaperBlueprint, "kind" | "total_marks">
): boolean {
  return blueprint.kind === "EXAM" || blueprint.total_marks != null
}

export function sectionAllocatedMarks(
  section: BlueprintSection
): number | null {
  if (
    section.marks_each == null &&
    section.chapter_allocations.every((alloc) => alloc.marks == null)
  ) {
    return null
  }

  let total = 0
  for (const alloc of section.chapter_allocations) {
    const perQuestion = alloc.marks ?? section.marks_each
    if (perQuestion == null) return null
    total += alloc.question_count * perQuestion
  }
  return total
}

export function sectionQuestionCount(section: BlueprintSection): number {
  return section.chapter_allocations.reduce(
    (sum, alloc) => sum + alloc.question_count,
    0
  )
}

export function blueprintAllocatedMarks(
  blueprint: QuestionPaperBlueprint
): number | null {
  const totals = blueprint.sections.map(sectionAllocatedMarks)
  if (totals.some((total) => total == null)) return null
  return totals.reduce<number>((sum, total) => sum + (total ?? 0), 0)
}

export function blueprintQuestionCount(
  blueprint: QuestionPaperBlueprint
): number {
  return blueprint.sections.reduce(
    (sum, section) => sum + sectionQuestionCount(section),
    0
  )
}

export function classGradeToNumber(classGrade: string | null): number {
  const match = classGrade?.match(/\d+/)
  return match ? Number(match[0]) : 10
}

export function sectionLetter(index: number): string {
  return String.fromCharCode(65 + (index % 26))
}

function normalizeName(name: string): string {
  return name.toLowerCase().replace(/\s+/g, " ").trim()
}

function matchSelectedChapter(
  alloc: ChapterAllocation,
  selected: SelectedChapter[]
): SelectedChapter | null {
  const needle = normalizeName(alloc.chapter_name)
  if (!needle || needle === "selected chapter") return null
  return (
    selected.find((ch) => {
      const name = normalizeName(ch.chapter_name)
      return name === needle || name.includes(needle) || needle.includes(name)
    }) ?? null
  )
}

/**
 * Preserve the sample's complete scheme while assigning every question
 * to a chapter selected on the notebook. Exact chapter-name matches are kept;
 * otherwise allocations go to the currently least-loaded selected chapter
 * (by marks when mark-based, otherwise by question count).
 */
export function rematchBlueprintChapters(
  blueprint: QuestionPaperBlueprint,
  selectedChapters: SelectedChapter[]
): QuestionPaperBlueprint {
  if (selectedChapters.length === 0) return blueprint

  const assignedLoad = new Map(selectedChapters.map((chapter) => [chapter, 0]))
  const useMarks = isMarkBasedBlueprint(blueprint)

  return {
    ...blueprint,
    sections: blueprint.sections.map((section) => ({
      ...section,
      chapter_allocations: section.chapter_allocations.map((alloc) => {
        const matched =
          matchSelectedChapter(alloc, selectedChapters) ??
          selectedChapters.reduce((leastLoaded, chapter) =>
            (assignedLoad.get(chapter) ?? 0) <
            (assignedLoad.get(leastLoaded) ?? 0)
              ? chapter
              : leastLoaded
          )
        const allocationLoad = useMarks
          ? alloc.question_count * (alloc.marks ?? section.marks_each ?? 0)
          : alloc.question_count

        assignedLoad.set(
          matched,
          (assignedLoad.get(matched) ?? 0) + allocationLoad
        )

        return {
          ...alloc,
          chapter_number: matched.chapter_number,
          chapter_name: matched.chapter_name,
        }
      }),
    })),
  }
}

export function hasForeignChapterAllocations(
  blueprint: QuestionPaperBlueprint,
  selectedChapters: SelectedChapter[]
): boolean {
  const allowed = new Set(selectedChapters.map((ch) => ch.chapter_number))
  return blueprint.sections.some((section) =>
    section.chapter_allocations.some(
      (alloc) =>
        alloc.chapter_number == null || !allowed.has(alloc.chapter_number)
    )
  )
}

export type ChapterAllocationGroup = {
  key: string
  allocation: ChapterAllocation
  allocationIndexes: number[]
  questionCount: number
}

export function groupChapterAllocations(
  allocations: ChapterAllocation[]
): ChapterAllocationGroup[] {
  const groups = new Map<string, ChapterAllocationGroup>()

  allocations.forEach((allocation, allocationIndex) => {
    const key = `${allocation.chapter_number ?? "unknown"}:${normalizeName(allocation.chapter_name)}`
    const group = groups.get(key)
    if (group) {
      group.allocationIndexes.push(allocationIndex)
      group.questionCount += allocation.question_count
    } else {
      groups.set(key, {
        key,
        allocation,
        allocationIndexes: [allocationIndex],
        questionCount: allocation.question_count,
      })
    }
  })

  return [...groups.values()]
}

export function updateGroupedQuestionCount(
  allocations: ChapterAllocation[],
  allocationIndexes: number[],
  questionCount: number
): ChapterAllocation[] {
  const targets = new Set(allocationIndexes)
  let remaining = Math.max(1, questionCount)
  let firstUpdatedIndex = -1
  const updated: ChapterAllocation[] = []

  allocations.forEach((allocation, allocationIndex) => {
    if (!targets.has(allocationIndex)) {
      updated.push(allocation)
      return
    }
    if (remaining === 0) return
    if (firstUpdatedIndex === -1) firstUpdatedIndex = updated.length

    const count = Math.min(allocation.question_count, remaining)
    remaining -= count
    updated.push({ ...allocation, question_count: count })
  })

  if (remaining > 0 && firstUpdatedIndex >= 0) {
    updated[firstUpdatedIndex] = {
      ...updated[firstUpdatedIndex],
      question_count: updated[firstUpdatedIndex].question_count + remaining,
    }
  }

  return updated
}

export function emptyBlueprint(
  partial?: Partial<QuestionPaperBlueprint>
): QuestionPaperBlueprint {
  return {
    kind: "EXAM",
    school_name: null,
    exam_title: null,
    subject: "Mathematics",
    grade: 10,
    total_marks: 40,
    duration_minutes: 90,
    exam_date: null,
    general_instructions: [],
    learning_outcomes: [],
    generation_rules: [],
    sections: [],
    blooms_targets: null,
    metadata: {},
    ...partial,
  }
}
