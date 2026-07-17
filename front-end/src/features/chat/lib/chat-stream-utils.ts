import type { ChatMessage, PersistedMessage, SSEEvent } from "@/features/chat/types/chat"

export function makeId(): string {
  return Math.random().toString(36).slice(2)
}

export function fromPersisted(message: PersistedMessage): ChatMessage | null {
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

export function applyStreamEvent(
  event: SSEEvent,
  patchLast: (updater: (message: ChatMessage) => ChatMessage) => void,
  setIsStreaming: (value: boolean) => void
): void {
  switch (event.type) {
    case "thinking":
      break

    case "token":
      patchLast((message) => ({
        ...message,
        content: message.content + event.content,
      }))
      break

    case "tool_start":
      patchLast((message) => ({
        ...message,
        toolCalls: [
          ...message.toolCalls,
          {
            id: makeId(),
            tool: event.tool,
            input: event.input,
            status: "running" as const,
          },
        ],
      }))
      break

    case "tool_end":
      patchLast((message) => ({
        ...message,
        toolCalls: message.toolCalls.map((toolCall) =>
          toolCall.status === "running"
            ? { ...toolCall, output: event.output, status: "done" as const }
            : toolCall
        ),
      }))
      break

    case "done":
      patchLast((message) => ({ ...message, isStreaming: false }))
      setIsStreaming(false)
      break

    case "error":
      patchLast((message) => ({
        ...message,
        content: message.content || `⚠ ${event.message}`,
        isStreaming: false,
      }))
      setIsStreaming(false)
      break
  }
}

export function parseSseChunk(
  chunk: string,
  onEvent: (event: SSEEvent) => void
): string {
  const lines = chunk.split("\n")
  const remainder = lines.pop() ?? ""

  for (const line of lines) {
    if (!line.startsWith("data: ")) continue
    const raw = line.slice(6).trim()
    if (!raw) continue
    try {
      onEvent(JSON.parse(raw) as SSEEvent)
    } catch {
      // skip malformed JSON
    }
  }

  return remainder
}
