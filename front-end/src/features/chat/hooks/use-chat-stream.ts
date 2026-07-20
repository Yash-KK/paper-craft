// chat/hooks/use-chat-stream.ts
import { useCallback, useRef, useState } from "react"
import { fetchEventSource } from "@microsoft/fetch-event-source"

import {
  applyStreamEvent,
  fromPersisted,
  fromWireEvent,
  makeId,
} from "@/features/chat/lib/chat-stream-utils"
import type { ChatMessage, PersistedMessage } from "@/features/chat/types/chat"
import { API_URL, getToken } from "@/lib/api"

export function useChatStream(
  notebookId: string,
  initialMessages: PersistedMessage[] = []
) {
  const [messages, setMessages] = useState<ChatMessage[]>(() =>
    initialMessages.flatMap((message) => {
      const ui = fromPersisted(message)
      return ui ? [ui] : []
    })
  )
  const [isStreaming, setIsStreaming] = useState(false)
  const [webSearch, setWebSearch] = useState(false)
  const abortRef = useRef<AbortController | null>(null)

  const patchLast = useCallback((updater: (m: ChatMessage) => ChatMessage) => {
    setMessages((prev) => {
      if (!prev.length) return prev
      const next = [...prev]
      next[next.length - 1] = updater({ ...next[next.length - 1] })
      return next
    })
  }, [])

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
              enabled_tools: webSearch ? ["web_search"] : [],
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
      }
    },
    [isStreaming, notebookId, patchLast, webSearch]
  )

  const stopStream = useCallback(() => {
    abortRef.current?.abort()
    patchLast((m) => ({ ...m, isStreaming: false }))
    setIsStreaming(false)
  }, [patchLast])

  return {
    messages,
    isStreaming,
    webSearch,
    setWebSearch,
    sendMessage,
    stopStream,
  }
}
