import { useQuery } from "@tanstack/react-query"

import { fetchPaperVersion } from "@/lib/api"
import { queryKeys } from "@/lib/query-keys"
import { isActiveGenerationStatus } from "@/lib/types/generation"
import { GENERATION_POLL_MS } from "@/features/question-papers/lib/question-paper-utils"

export function usePaperVersion(
  paperId: string,
  versionNumber: number,
  enabled = true
) {
  return useQuery({
    queryKey: queryKeys.paperVersion(paperId, versionNumber),
    queryFn: () => fetchPaperVersion(paperId, versionNumber),
    enabled: enabled && Boolean(paperId) && versionNumber > 0,
    staleTime: 0,
    refetchInterval: (query) => {
      const status = query.state.data?.status
      if (!status) return false
      return isActiveGenerationStatus(status) ? GENERATION_POLL_MS : false
    },
  })
}
