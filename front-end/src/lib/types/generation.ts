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

export type BlueprintSection = {
  section_name: string
  question_type: QuestionType
  marks_each: number
  chapter_allocations: ChapterAllocation[]
  section_instructions: string | null
  section_total_marks?: number
}

export type QuestionPaperBlueprint = {
  school_name: string | null
  exam_title: string | null
  subject: string
  grade: number
  total_marks: number
  duration_minutes: number | null
  exam_date: string | null
  general_instructions: string[]
  sections: BlueprintSection[]
  blooms_targets: Partial<Record<BloomsLevel, number>> | null
  allocated_marks?: number
}

export type SampleBlueprintSummary = {
  id: string
  slug: string
  label: string
  total_marks: number
}

export type SampleBlueprintDetail = SampleBlueprintSummary & {
  blueprint: QuestionPaperBlueprint
}

export type SelectedChapterRef = {
  book_code: string
  chapter_number: number
  chapter_name: string
}

export type GeneratePaperPayload = {
  blueprint: QuestionPaperBlueprint
  selected_chapters: SelectedChapterRef[]
  subject: string
  grade: number
  teacher_instructions?: string | null
}

export type GenerationResult = {
  blueprint: QuestionPaperBlueprint
  final_paper: Record<string, unknown>
  final_answer_key: Record<string, unknown>
  generated_items: Record<string, unknown>[]
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

export function sectionAllocatedMarks(section: BlueprintSection): number {
  return section.chapter_allocations.reduce(
    (sum, alloc) => sum + alloc.question_count * (alloc.marks ?? section.marks_each),
    0
  )
}

export function blueprintAllocatedMarks(blueprint: QuestionPaperBlueprint): number {
  return blueprint.sections.reduce(
    (sum, section) => sum + sectionAllocatedMarks(section),
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
  selected: SelectedChapterRef[]
): SelectedChapterRef | null {
  if (alloc.chapter_number != null) {
    const byNumber = selected.find((ch) => ch.chapter_number === alloc.chapter_number)
    if (byNumber) return byNumber
  }

  const needle = normalizeName(alloc.chapter_name)
  return (
    selected.find((ch) => {
      const name = normalizeName(ch.chapter_name)
      return name === needle || name.includes(needle) || needle.includes(name)
    }) ?? null
  )
}

/** Keep only allocations that map onto the notebook's selected chapters. */
export function rematchBlueprintChapters(
  blueprint: QuestionPaperBlueprint,
  selectedChapters: SelectedChapterRef[]
): QuestionPaperBlueprint {
  return {
    ...blueprint,
    sections: blueprint.sections.map((section) => ({
      ...section,
      chapter_allocations: section.chapter_allocations.flatMap((alloc) => {
        const matched = matchSelectedChapter(alloc, selectedChapters)
        if (!matched) return []
        return [
          {
            ...alloc,
            chapter_number: matched.chapter_number,
            chapter_name: matched.chapter_name,
          },
        ]
      }),
    })),
  }
}

export function hasForeignChapterAllocations(
  blueprint: QuestionPaperBlueprint,
  selectedChapters: SelectedChapterRef[]
): boolean {
  const allowed = new Set(selectedChapters.map((ch) => ch.chapter_number))
  return blueprint.sections.some((section) =>
    section.chapter_allocations.some(
      (alloc) =>
        alloc.chapter_number == null || !allowed.has(alloc.chapter_number)
    )
  )
}

export function emptyBlueprint(partial?: Partial<QuestionPaperBlueprint>): QuestionPaperBlueprint {
  return {
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
    ...partial,
  }
}
