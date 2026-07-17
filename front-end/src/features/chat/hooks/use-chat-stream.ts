import { useCallback, useRef, useState } from "react"

import type {
  ChatMessage,
  PersistedMessage,
  SSEEvent,
  ToolCall,
} from "@/features/chat/types/chat"
import { API_URL, getToken } from "@/lib/api"

function makeId() {
  return Math.random().toString(36).slice(2)
}

function fromPersisted(message: PersistedMessage): ChatMessage | null {
  if (message.role !== "user" && message.role !== "assistant") return null
  return {
    id: message.id,
    role: message.role,
    content: message.content,
    toolCalls: (message.metadata.tool_calls ?? []).map((toolCall) => ({
      id: toolCall.id ?? makeId(),
      tool: toolCall.tool,
      input: toolCall.input,
      output: toolCall.output,
      status: "done" as const,
    })),
    isStreaming: false,
  }
}

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

  const applyEvent = useCallback(
    (event: SSEEvent) => {
      switch (event.type) {
        case "thinking":
          break

        case "token":
          patchLast((m) => ({ ...m, content: m.content + event.content }))
          break

        case "tool_start": {
          const tc: ToolCall = {
            id: makeId(),
            tool: event.tool,
            input: event.input,
            status: "running",
          }
          patchLast((m) => ({ ...m, toolCalls: [...m.toolCalls, tc] }))
          break
        }

        case "tool_end":
          patchLast((m) => ({
            ...m,
            toolCalls: m.toolCalls.map((tc) =>
              tc.status === "running"
                ? { ...tc, output: event.output, status: "done" }
                : tc
            ),
          }))
          break

        case "done":
          patchLast((m) => ({ ...m, isStreaming: false }))
          setIsStreaming(false)
          break

        case "error":
          patchLast((m) => ({
            ...m,
            content: m.content || `⚠ ${event.message}`,
            isStreaming: false,
          }))
          setIsStreaming(false)
          break
      }
    },
    [patchLast]
  )

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

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split("\n")
          buffer = lines.pop() ?? ""

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue
            const raw = line.slice(6).trim()
            if (!raw) continue
            try {
              applyEvent(JSON.parse(raw) as SSEEvent)
            } catch {
              // skip malformed JSON
            }
          }
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
    [applyEvent, isStreaming, notebookId, patchLast]
  )

  const stopStream = useCallback(() => {
    abortRef.current?.abort()
    patchLast((m) => ({ ...m, isStreaming: false }))
    setIsStreaming(false)
  }, [patchLast])

  return { messages, isStreaming, sendMessage, stopStream }
}
