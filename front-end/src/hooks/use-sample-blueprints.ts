import { useMutation, useQuery } from "@tanstack/react-query"
import { toast } from "sonner"

import { fetchSampleBlueprints, generateQuestionPaper } from "@/lib/api"
import { queryKeys } from "@/lib/query-keys"

export function useSampleBlueprints(enabled = true) {
  return useQuery({
    queryKey: queryKeys.sampleBlueprints,
    queryFn: fetchSampleBlueprints,
    enabled,
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
