import { useQuery } from "@tanstack/react-query"

import { useGenerateQuestionPaper } from "@/features/question-papers/hooks/use-create-paper-version"
import { fetchSampleBlueprints } from "@/lib/api"
import { queryKeys } from "@/lib/query-keys"
import type { Board, Subject } from "@/lib/types/notebook"

export function useSampleBlueprints(filters?: {
  board?: Board | null
  subject?: Subject | null
  enabled?: boolean
}) {
  const board = filters?.board ?? null
  const subject = filters?.subject ?? null
  const enabled = filters?.enabled ?? true

  return useQuery({
    queryKey: queryKeys.sampleBlueprints(board, subject),
    queryFn: () => fetchSampleBlueprints({ board, subject }),
    enabled: enabled && Boolean(board && subject),
  })
}

export { useGenerateQuestionPaper }
