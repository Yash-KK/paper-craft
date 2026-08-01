import type {
  ChatMessage,
  PersistedMessage,
  SSEEvent,
} from "@/features/chat/types/chat"

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i

export function isPersistedChatMessageId(id: string): boolean {
  return UUID_RE.test(id)
}

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

export function toUiMessages(messages: PersistedMessage[]): ChatMessage[] {
  return messages.flatMap((message) => {
    const ui = fromPersisted(message)
    return ui ? [ui] : []
  })
}

/** Replace trailing optimistic messages with the newest persisted page. */
export function mergeLatestPersistedPage(
  prev: ChatMessage[],
  persistedPage: PersistedMessage[]
): ChatMessage[] {
  const fromServer = toUiMessages(persistedPage)
  if (fromServer.length === 0) return prev

  const temps: ChatMessage[] = []
  for (let i = prev.length - 1; i >= 0; i -= 1) {
    if (isPersistedChatMessageId(prev[i].id)) break
    temps.unshift(prev[i])
  }
  if (temps.length === 0) return prev

  const serverTail = fromServer.slice(-temps.length)
  const matches =
    serverTail.length === temps.length &&
    serverTail.every((message, index) => message.role === temps[index].role)
  if (!matches) return prev

  const serverIds = new Set(fromServer.map((message) => message.id))
  const older = prev.filter(
    (message) =>
      isPersistedChatMessageId(message.id) && !serverIds.has(message.id)
  )
  return [...older, ...fromServer]
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
    case "token":
      patchLast((message) => ({
        ...message,
        content: message.content + event.content,
      }))
      break

    case "tool_start":
      patchLast((message) => ({
        ...message,
        content: "",
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
