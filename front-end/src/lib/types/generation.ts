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

export type GeneratePaperPayload = {
  blueprint: QuestionPaperBlueprint
  selected_chapters: {
    book_code: string
    chapter_number: number
    chapter_name: string
  }[]
  subject: string
  grade: number
  teacher_instructions?: string | null
  use_sample_as_context?: boolean
  sample_text?: string | null
}

export type GenerationResult = {
  blueprint: QuestionPaperBlueprint
  final_paper: Record<string, unknown>
  final_answer_key: Record<string, unknown>
  generated_items: Record<string, unknown>[]
  sample_text_used: boolean
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

export const DURATION_OPTIONS: { label: string; minutes: number }[] = [
  { label: "1 Hour", minutes: 60 },
  { label: "1.5 Hours", minutes: 90 },
  { label: "2 Hours", minutes: 120 },
  { label: "2.5 Hours", minutes: 150 },
  { label: "3 Hours", minutes: 180 },
]

export function sectionAllocatedMarks(section: BlueprintSection): number {
  return section.chapter_allocations.reduce((sum, a) => {
    const marks = a.marks ?? section.marks_each
    return sum + a.question_count * marks
  }, 0)
}

export function blueprintAllocatedMarks(
  blueprint: QuestionPaperBlueprint
): number {
  return blueprint.sections.reduce(
    (sum, section) => sum + sectionAllocatedMarks(section),
    0
  )
}

export function classGradeToNumber(classGrade: string | null): number {
  if (!classGrade) return 10
  const match = classGrade.match(/\d+/)
  return match ? Number(match[0]) : 10
}

function normalizeName(name: string): string {
  return name.toLowerCase().replace(/\s+/g, " ").trim()
}

export function rematchBlueprintChapters(
  blueprint: QuestionPaperBlueprint,
  selectedChapters: {
    book_code: string
    chapter_number: number
    chapter_name: string
  }[]
): QuestionPaperBlueprint {
  const byName = new Map(
    selectedChapters.map((ch) => [normalizeName(ch.chapter_name), ch])
  )

  return {
    ...blueprint,
    sections: blueprint.sections.map((section) => ({
      ...section,
      chapter_allocations: section.chapter_allocations.map((alloc) => {
        const exact = byName.get(normalizeName(alloc.chapter_name))
        if (exact) {
          return {
            ...alloc,
            chapter_number: exact.chapter_number,
            chapter_name: exact.chapter_name,
          }
        }
        const needle = normalizeName(alloc.chapter_name)
        const fuzzy = selectedChapters.find((ch) => {
          const catalog = normalizeName(ch.chapter_name)
          return catalog.includes(needle) || needle.includes(catalog)
        })
        if (fuzzy) {
          return {
            ...alloc,
            chapter_number: fuzzy.chapter_number,
            chapter_name: fuzzy.chapter_name,
          }
        }
        return { ...alloc, chapter_number: null }
      }),
    })),
  }
}
