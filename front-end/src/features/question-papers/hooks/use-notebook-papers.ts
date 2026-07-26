import { useQuery } from "@tanstack/react-query"

import { fetchNotebookPapers } from "@/lib/api"
import { queryKeys } from "@/lib/query-keys"
import {
  isActiveGenerationStatus,
  paperHasActiveGeneration,
} from "@/lib/types/generation"
import { GENERATION_POLL_MS } from "@/features/question-papers/lib/question-paper-utils"

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

export function usePaperHasActiveGeneration(
  notebookId: string,
  paperId: string | null
): boolean {
  const { data } = useNotebookPapers(notebookId, Boolean(paperId))
  if (!paperId || !data) return false
  const paper = data.find((item) => item.id === paperId)
  if (!paper) return false
  return paper.versions.some((version) =>
    isActiveGenerationStatus(version.status)
  )
}
