import { useQuery } from "@tanstack/react-query"

import { fetchNotebookChat } from "@/lib/api"
import { queryKeys } from "@/lib/query-keys"

export function useNotebookChat(notebookId: string, enabled = true) {
  return useQuery({
    queryKey: queryKeys.notebookChat(notebookId),
    queryFn: () => fetchNotebookChat(notebookId),
    enabled: enabled && Boolean(notebookId),
  })
}
