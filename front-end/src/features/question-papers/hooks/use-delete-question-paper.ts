import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { deleteQuestionPaper } from "@/lib/api"
import { queryKeys } from "@/lib/query-keys"

export function useDeleteQuestionPaper(notebookId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (paperId: string) => deleteQuestionPaper(paperId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: queryKeys.notebookPapers(notebookId),
      })
      toast.success("Question paper deleted.")
    },
    onError: (err) => {
      toast.error(
        err instanceof Error ? err.message : "Failed to delete question paper"
      )
    },
  })
}
