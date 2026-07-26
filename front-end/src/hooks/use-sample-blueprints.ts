import { useMutation, useQuery } from "@tanstack/react-query"
import { toast } from "sonner"

import { fetchSampleBlueprints, generateQuestionPaper } from "@/lib/api"
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

export function useGenerateQuestionPaper() {
  return useMutation({
    mutationFn: generateQuestionPaper,
    onSuccess: () => toast.success("Question paper generated."),
    onError: (err) => {
      toast.error(
        err instanceof Error ? err.message : "Failed to generate question paper"
      )
    },
  })
}
