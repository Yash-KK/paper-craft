import { useInfiniteQuery } from "@tanstack/react-query"

import { fetchNotebookChatMessages } from "@/lib/api"
import { queryKeys } from "@/lib/query-keys"

const PAGE_SIZE = 5

export function useNotebookChatMessages(notebookId: string, enabled = true) {
  return useInfiniteQuery({
    queryKey: queryKeys.notebookChatMessages(notebookId),
    queryFn: ({ pageParam }) =>
      fetchNotebookChatMessages(notebookId, {
        cursor: pageParam,
        size: PAGE_SIZE,
      }),
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (lastPage) => lastPage.next_page ?? undefined,
    enabled: enabled && Boolean(notebookId),
  })
}
