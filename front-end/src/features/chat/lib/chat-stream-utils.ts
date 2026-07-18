import type {
  ChatMessage,
  PersistedMessage,
  SSEEvent,
} from "@/features/chat/types/chat"

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

/** Map backend EventSourceResponse frames (`event` + plain `data`) to UI events. */
export function fromWireEvent(event: string, data: string): SSEEvent | null {
  switch (event) {
    case "token":
      return data ? { type: "token", content: data } : null
    case "tool_start":
      return data ? { type: "tool_start", tool: data, input: "" } : null
    case "tool_end":
      return data ? { type: "tool_end", tool: data, output: "" } : null
    case "done":
      return { type: "done" }
    case "error":
      return {
        type: "error",
        message: data || "The chat service could not generate a response",
      }
    default:
      return null
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
          toolCall.status === "running" &&
          (!event.tool || toolCall.tool === event.tool)
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
