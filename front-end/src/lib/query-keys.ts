import type { ClassGrade, Subject } from "@/lib/types/notebook"

export const queryKeys = {
  notebooks: ["notebooks"] as const,
  notebookChat: (notebookId: string) =>
    ["notebooks", notebookId, "chat"] as const,
  grades: ["chapters", "grades"] as const,
  subjects: (grade: ClassGrade) => ["chapters", "subjects", grade] as const,
  chapters: (grade: ClassGrade, subject: Subject) =>
    ["chapters", "list", grade, subject] as const,
}
