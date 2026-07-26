import { useMutation, useQuery } from "@tanstack/react-query"
import { toast } from "sonner"

import {
  fetchSampleBlueprint,
  fetchSampleBlueprints,
  generateQuestionPaper,
} from "@/lib/api"
import { queryKeys } from "@/lib/query-keys"
import type { GeneratePaperPayload } from "@/lib/types/generation"

export function useSampleBlueprints(enabled = true) {
  return useQuery({
    queryKey: queryKeys.sampleBlueprints,
    queryFn: fetchSampleBlueprints,
    enabled,
  })
}

export function useSampleBlueprint(id: string | null) {
  return useQuery({
    queryKey: queryKeys.sampleBlueprint(id ?? ""),
    queryFn: () => fetchSampleBlueprint(id!),
    enabled: Boolean(id),
  })
}

export function useGenerateQuestionPaper() {
  return useMutation({
    mutationFn: (payload: GeneratePaperPayload) => generateQuestionPaper(payload),
    onSuccess: () => {
      toast.success("Question paper generated.")
    },
    onError: (err) => {
      toast.error(
        err instanceof Error ? err.message : "Failed to generate question paper"
      )
    },
  })
}
