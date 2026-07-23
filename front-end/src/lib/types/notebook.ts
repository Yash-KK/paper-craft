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
  is_available: boolean
}

export type NotebookCreatePayload = {
  name: string
  class_grade: ClassGrade
  subject: Subject
  selected_chapter_numbers: number[]
}

export type NotebookUpdatePayload = {
  name?: string
  class_grade?: ClassGrade
  subject?: Subject
  color_hex?: string
  selected_chapter_numbers?: number[]
}
