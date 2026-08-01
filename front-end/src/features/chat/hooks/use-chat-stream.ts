import { useCallback, useRef, useState } from "react"
import { useQueryClient, type InfiniteData } from "@tanstack/react-query"
import { fetchEventSource } from "@microsoft/fetch-event-source"

import {
  applyStreamEvent,
  fromPersisted,
  fromWireEvent,
  makeId,
  mergeLatestPersistedPage,
} from "@/features/chat/lib/chat-stream-utils"
import type {
  ChatMessage,
  ChatMessagesPage,
  ChatToolId,
  PersistedMessage,
} from "@/features/chat/types/chat"
import { API_URL, getToken } from "@/lib/api"
import { queryKeys } from "@/lib/query-keys"

export function useChatStream(
  notebookId: string,
  initialMessages: PersistedMessage[] = []
) {
  const queryClient = useQueryClient()
  const [messages, setMessages] = useState<ChatMessage[]>(() =>
    initialMessages.flatMap((message) => {
      const ui = fromPersisted(message)
      return ui ? [ui] : []
    })
  )
  const [isStreaming, setIsStreaming] = useState(false)
  const [enabledTools, setEnabledTools] = useState<ChatToolId[]>([])
  const abortRef = useRef<AbortController | null>(null)

  const patchLast = useCallback((updater: (m: ChatMessage) => ChatMessage) => {
    setMessages((prev) => {
      if (!prev.length) return prev
      const next = [...prev]
      next[next.length - 1] = updater({ ...next[next.length - 1] })
      return next
    })
  }, [])

  const syncFromLatestPage = useCallback(async () => {
    await queryClient.refetchQueries({
      queryKey: queryKeys.notebookChatMessages(notebookId),
    })
    const cached = queryClient.getQueryData<InfiniteData<ChatMessagesPage>>(
      queryKeys.notebookChatMessages(notebookId)
    )
    const latestPage = cached?.pages[0]?.items
    if (!latestPage?.length) return
    setMessages((prev) => mergeLatestPersistedPage(prev, latestPage))
  }, [notebookId, queryClient])

  const sendMessage = useCallback(
    async (question: string) => {
      if (isStreaming || !question.trim()) return

      setMessages((prev) => [
        ...prev,
        {
          id: makeId(),
          role: "user",
          content: question.trim(),
          toolCalls: [],
          isStreaming: false,
        },
        {
          id: makeId(),
          role: "assistant",
          content: "",
          toolCalls: [],
          isStreaming: true,
        },
      ])
      setIsStreaming(true)

      const controller = new AbortController()
      abortRef.current = controller
      let finished = false

      try {
        await fetchEventSource(
          `${API_URL}/api/v1/notebooks/${notebookId}/chat/messages`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${getToken()}`,
            },
            body: JSON.stringify({
              content: question.trim(),
              enabled_tools: enabledTools,
            }),
            signal: controller.signal,
            openWhenHidden: true,
            onmessage(ev) {
              const event = fromWireEvent(ev.event, ev.data)
              if (!event) return

              applyStreamEvent(event, patchLast, setIsStreaming)

              if (event.type === "done" || event.type === "error") {
                finished = true
                controller.abort()
              }
            },
            onclose() {
              if (finished) return
              throw new Error("Stream closed unexpectedly")
            },
            onerror(err) {
              throw err
            },
          }
        )
      } catch (err) {
        if ((err as Error).name !== "AbortError") {
          patchLast((m) => ({
            ...m,
            content: m.content || "Connection error — please try again.",
            isStreaming: false,
          }))
        }
      } finally {
        setIsStreaming(false)
        if (finished) {
          try {
            await syncFromLatestPage()
          } catch {
            // Optimistic messages remain until the next successful refetch.
          }
        }
      }
    },
    [enabledTools, isStreaming, notebookId, patchLast, syncFromLatestPage]
  )

  const stopStream = useCallback(() => {
    abortRef.current?.abort()
    patchLast((m) => ({ ...m, isStreaming: false }))
    setIsStreaming(false)
  }, [patchLast])

  const prependOlderMessages = useCallback((older: PersistedMessage[]) => {
    const incoming = older.flatMap((message) => {
      const ui = fromPersisted(message)
      return ui ? [ui] : []
    })
    if (incoming.length === 0) return

    setMessages((prev) => {
      const existingIds = new Set(prev.map((message) => message.id))
      const fresh = incoming.filter((message) => !existingIds.has(message.id))
      return fresh.length ? [...fresh, ...prev] : prev
    })
  }, [])

  return {
    messages,
    isStreaming,
    enabledTools,
    setEnabledTools,
    sendMessage,
    stopStream,
    prependOlderMessages,
  }
}
