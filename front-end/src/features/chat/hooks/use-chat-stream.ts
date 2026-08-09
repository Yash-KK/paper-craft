import { useCallback, useRef, useState } from "react"
import { useQueryClient, type InfiniteData } from "@tanstack/react-query"
import { fetchEventSource } from "@microsoft/fetch-event-source"
import { toast } from "sonner"

import {
  applyStreamEvent,
  fromWireEvent,
  makeId,
  mergeLatestPersistedPage,
  toUiMessages,
} from "@/features/chat/lib/chat-stream-utils"
import type {
  ChatMessage,
  ChatMessagesPage,
  ChatToolId,
  PersistedMessage,
} from "@/features/chat/types/chat"
import { DEFAULT_CHAT_MESSAGE_LIMIT } from "@/components/usage-limit-indicator"
import { API_URL, getToken, parseApiError } from "@/lib/api"
import { queryKeys } from "@/lib/query-keys"
import { useAuth } from "@/providers/auth-provider"

export function useChatStream(
  notebookId: string,
  initialMessages: PersistedMessage[] = []
) {
  const queryClient = useQueryClient()
  const { user, refreshUser } = useAuth()
  const [messages, setMessages] = useState<ChatMessage[]>(() =>
    toUiMessages(initialMessages)
  )
  const [isStreaming, setIsStreaming] = useState(false)
  const [enabledTools, setEnabledTools] = useState<ChatToolId[]>([])
  const abortRef = useRef<AbortController | null>(null)
  const atChatLimit =
    (user?.chat_message_usage ?? 0) >=
    (user?.chat_message_limit ?? DEFAULT_CHAT_MESSAGE_LIMIT)

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
      const content = question.trim()
      if (isStreaming || !content || atChatLimit) return

      setMessages((prev) => [
        ...prev,
        {
          id: makeId(),
          role: "user",
          content,
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
      let accepted = false

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
              content,
              enabled_tools: enabledTools,
            }),
            signal: controller.signal,
            openWhenHidden: true,
            async onopen(response) {
              if (response.ok) {
                accepted = true
                void refreshUser()
                return
              }
              throw new Error(await parseApiError(response))
            },
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
          const message =
            err instanceof Error
              ? err.message
              : "Connection error — please try again."
          if (!accepted) {
            toast.error(message)
            setMessages((prev) => prev.slice(0, -2))
          } else {
            patchLast((m) => ({
              ...m,
              content: m.content || message,
              isStreaming: false,
            }))
          }
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
    [
      atChatLimit,
      enabledTools,
      isStreaming,
      notebookId,
      patchLast,
      refreshUser,
      syncFromLatestPage,
    ]
  )

  const stopStream = useCallback(() => {
    abortRef.current?.abort()
    patchLast((m) => ({ ...m, isStreaming: false }))
    setIsStreaming(false)
  }, [patchLast])

  const prependOlderMessages = useCallback((older: PersistedMessage[]) => {
    const incoming = toUiMessages(older)
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
    atChatLimit,
  }
}
