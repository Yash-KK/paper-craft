import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { cancelPaperVersion } from "@/lib/api"
import { queryKeys } from "@/lib/query-keys"

export function useCancelPaperVersion(notebookId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      paperId,
      versionNumber,
    }: {
      paperId: string
      versionNumber: number
    }) => cancelPaperVersion(paperId, versionNumber),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: queryKeys.notebookPapers(notebookId),
      })
      toast.success("Generation cancelled.")
    },
    onError: (err) => {
      toast.error(
        err instanceof Error ? err.message : "Failed to cancel generation"
      )
    },
  })
}
