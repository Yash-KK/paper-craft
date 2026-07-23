import type { Board, ClassGrade, Subject } from "@/lib/types/notebook"

export const queryKeys = {
  notebooks: ["notebooks"] as const,
  notebookChat: (notebookId: string) =>
    ["notebooks", notebookId, "chat"] as const,
  boards: ["chapters", "boards"] as const,
  grades: (board: Board) => ["chapters", "grades", board] as const,
  subjects: (board: Board, grade: ClassGrade) =>
    ["chapters", "subjects", board, grade] as const,
  chapters: (board: Board, grade: ClassGrade, subject: Subject) =>
    ["chapters", "list", board, grade, subject] as const,
}
