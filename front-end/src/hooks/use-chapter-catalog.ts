import { useQuery } from "@tanstack/react-query"

import { fetchChapters, fetchGrades, fetchSubjects } from "@/lib/api"
import { queryKeys } from "@/lib/query-keys"
import type { ClassGrade, Subject } from "@/lib/types/notebook"

export function useGrades(enabled: boolean) {
  return useQuery({
    queryKey: queryKeys.grades,
    queryFn: fetchGrades,
    enabled,
  })
}

export function useSubjects(grade: ClassGrade | "", enabled = true) {
  return useQuery({
    queryKey: queryKeys.subjects(grade as ClassGrade),
    queryFn: () => fetchSubjects(grade as ClassGrade),
    enabled: enabled && Boolean(grade),
  })
}

export function useChapters(
  grade: ClassGrade | "",
  subject: Subject | "",
  enabled = true
) {
  return useQuery({
    queryKey: queryKeys.chapters(grade as ClassGrade, subject as Subject),
    queryFn: () => fetchChapters(grade as ClassGrade, subject as Subject),
    enabled: enabled && Boolean(grade) && Boolean(subject),
  })
}
