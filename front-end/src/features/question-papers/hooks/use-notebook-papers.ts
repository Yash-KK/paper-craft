import { useQuery } from "@tanstack/react-query"

import { GENERATION_POLL_MS } from "@/features/question-papers/lib/question-paper-utils"
import { fetchNotebookPapers } from "@/lib/api"
import { queryKeys } from "@/lib/query-keys"
import { paperHasActiveGeneration } from "@/lib/types/generation"

export function useNotebookPapers(notebookId: string, enabled = true) {
  return useQuery({
    queryKey: queryKeys.notebookPapers(notebookId),
    queryFn: () => fetchNotebookPapers(notebookId),
    enabled: enabled && Boolean(notebookId),
    staleTime: 0,
    refetchInterval: (query) => {
      const papers = query.state.data
      if (!papers?.length) return false
      return papers.some(paperHasActiveGeneration) ? GENERATION_POLL_MS : false
    },
  })
}
