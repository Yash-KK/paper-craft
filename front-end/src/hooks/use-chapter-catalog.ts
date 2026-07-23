import { useQuery } from "@tanstack/react-query"

import {
  fetchBoards,
  fetchChapters,
  fetchGrades,
  fetchSubjects,
} from "@/lib/api"
import { queryKeys } from "@/lib/query-keys"
import type { Board, ClassGrade, Subject } from "@/lib/types/notebook"

export function useBoards(enabled: boolean) {
  return useQuery({
    queryKey: queryKeys.boards,
    queryFn: fetchBoards,
    enabled,
  })
}

export function useGrades(board: Board | "", enabled = true) {
  return useQuery({
    queryKey: queryKeys.grades(board as Board),
    queryFn: () => fetchGrades(board as Board),
    enabled: enabled && Boolean(board),
  })
}

export function useSubjects(
  board: Board | "",
  grade: ClassGrade | "",
  enabled = true
) {
  return useQuery({
    queryKey: queryKeys.subjects(board as Board, grade as ClassGrade),
    queryFn: () => fetchSubjects(board as Board, grade as ClassGrade),
    enabled: enabled && Boolean(board) && Boolean(grade),
  })
}

export function useChapters(
  board: Board | "",
  grade: ClassGrade | "",
  subject: Subject | "",
  enabled = true
) {
  return useQuery({
    queryKey: queryKeys.chapters(
      board as Board,
      grade as ClassGrade,
      subject as Subject
    ),
    queryFn: () =>
      fetchChapters(board as Board, grade as ClassGrade, subject as Subject),
    enabled: enabled && Boolean(board) && Boolean(grade) && Boolean(subject),
  })
}
