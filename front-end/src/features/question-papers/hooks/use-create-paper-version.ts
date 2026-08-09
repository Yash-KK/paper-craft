import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { createPaperVersion, generateQuestionPaper } from "@/lib/api"
import { queryKeys } from "@/lib/query-keys"
import type {
  GenerateNewVersionPayload,
  GeneratePaperPayload,
  GenerationResult,
} from "@/lib/types/generation"
import { useAuth } from "@/providers/auth-provider"

export function useGenerateQuestionPaper() {
  const queryClient = useQueryClient()
  const { refreshUser } = useAuth()

  return useMutation({
    mutationFn: (payload: GeneratePaperPayload) =>
      generateQuestionPaper(payload),
    onSuccess: (result: GenerationResult) => {
      toast.success("Question paper generation started.")
      void queryClient.invalidateQueries({
        queryKey: queryKeys.notebookPapers(result.notebook_id),
      })
      void queryClient.invalidateQueries({ queryKey: queryKeys.notebooks })
      void refreshUser()
    },
    onError: (err) => {
      toast.error(
        err instanceof Error ? err.message : "Failed to start generation"
      )
    },
  })
}

export function useCreatePaperVersion(paperId: string, notebookId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: GenerateNewVersionPayload) =>
      createPaperVersion(paperId, payload),
    onSuccess: (result: GenerationResult) => {
      toast.success(`Version ${result.version_number} queued.`)
      void queryClient.invalidateQueries({
        queryKey: queryKeys.notebookPapers(notebookId),
      })
      void queryClient.invalidateQueries({
        queryKey: queryKeys.paperVersion(paperId, result.version_number),
      })
    },
    onError: (err) => {
      toast.error(
        err instanceof Error ? err.message : "Failed to create a new version"
      )
    },
  })
}
