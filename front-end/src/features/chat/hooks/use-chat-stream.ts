import { useCallback, useRef, useState } from "react"

import {
  applyStreamEvent,
  fromPersisted,
  makeId,
  parseSseChunk,
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

      const userMsg: ChatMessage = {
        id: makeId(),
        role: "user",
        content: question.trim(),
        toolCalls: [],
        isStreaming: false,
      }
      const assistantMsg: ChatMessage = {
        id: makeId(),
        role: "assistant",
        content: "",
        toolCalls: [],
        isStreaming: true,
      }
      setMessages((prev) => [...prev, userMsg, assistantMsg])
      setIsStreaming(true)

      const controller = new AbortController()
      abortRef.current = controller

      try {
        const token = getToken()
        const response = await fetch(
          `${API_URL}/api/v1/notebooks/${notebookId}/chat/messages`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ content: question.trim() }),
            signal: controller.signal,
          }
        )

        if (!response.ok || !response.body) {
          throw new Error(`HTTP ${response.status}`)
        }

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ""

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer = parseSseChunk(
            buffer + decoder.decode(value, { stream: true }),
            (event) => applyStreamEvent(event, patchLast, setIsStreaming)
          )
        }
      } catch (err) {
        if ((err as Error).name !== "AbortError") {
          patchLast((m) => ({
            ...m,
            content: m.content || "Connection error — please try again.",
            isStreaming: false,
          }))
          setIsStreaming(false)
        }
      }
    },
    [isStreaming, notebookId, patchLast]
  )

  const stopStream = useCallback(() => {
    abortRef.current?.abort()
    patchLast((m) => ({ ...m, isStreaming: false }))
    setIsStreaming(false)
  }, [patchLast])

  return { messages, isStreaming, sendMessage, stopStream }
}
