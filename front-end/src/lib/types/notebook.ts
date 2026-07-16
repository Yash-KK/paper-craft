export type ClassGrade = "Class 9" | "Class 10"
export type Subject = "Mathematics"

export type SelectedChapter = {
  book_code: string
  chapter_number: number
  chapter_name: string
}

export type NotebookListItem = {
  id: string
  name: string
  class_grade: ClassGrade | null
  subject: Subject | null
  color_hex: string | null
  selected_chapters: SelectedChapter[]
  updated_at: string
}

export type ChapterCatalogItem = {
  chapter_number: number
  chapter_name: string
  book_code: string
}

export type NotebookCreatePayload = {
  name: string
  class_grade: ClassGrade
  subject: Subject
  color_hex?: string | null
  selected_chapter_numbers: number[]
}

export const NOTEBOOK_COLORS = [
  "#7c3aed",
  "#14b8a6",
  "#f59e0b",
  "#ec4899",
  "#22c55e",
  "#d946ef",
] as const
