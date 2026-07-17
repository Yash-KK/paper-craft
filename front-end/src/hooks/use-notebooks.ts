import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import {
  createNotebook,
  deleteNotebook,
  fetchNotebooks,
} from "@/lib/api"
import { queryKeys } from "@/lib/query-keys"
import type { NotebookCreatePayload } from "@/lib/types/notebook"

export function useNotebooks(enabled = true) {
  const query = useQuery({
    queryKey: queryKeys.notebooks,
    queryFn: fetchNotebooks,
    enabled,
  })

  return {
    notebooks: query.data ?? [],
    loading: query.isPending,
    error: query.error instanceof Error ? query.error.message : null,
  }
}

export function useCreateNotebook() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: NotebookCreatePayload) => createNotebook(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.notebooks })
      toast.success("Notebook created successfully.")
    },
    onError: (err) => {
      toast.error(
        err instanceof Error ? err.message : "Failed to create notebook"
      )
    },
  })
}

export function useDeleteNotebook() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (notebookId: string) => deleteNotebook(notebookId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.notebooks })
      toast.success("Notebook deleted.")
    },
    onError: (err) => {
      toast.error(
        err instanceof Error ? err.message : "Failed to delete notebook"
      )
    },
  })
}
