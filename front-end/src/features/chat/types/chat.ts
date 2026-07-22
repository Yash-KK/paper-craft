export type ToolCall = {
  id: string
  tool: string
  input: string
  output?: string
  status: "running" | "done"
}

export type ChatToolId = "retrieve_context" | "web_search"

export type ChatMessage = {
  id: string
  role: "user" | "assistant"
  content: string
  toolCalls: ToolCall[]
  isStreaming: boolean
}

export type SSEEvent =
  | { type: "thinking" }
  | { type: "token"; content: string }
  | { type: "tool_start"; tool: string; input: string }
  | { type: "tool_end"; tool: string; output: string }
  | {
      type: "done"
      session_id?: string
      user_message?: PersistedMessage
      assistant_message?: PersistedMessage
    }
  | { type: "error"; message: string }

export type PersistedMessage = {
  id: string
  session_id: string
  role: "user" | "assistant" | "system" | "tool"
  content: string
  metadata: {
    tool_calls?: Array<{
      id?: string
      tool: string
      input: string
      output?: string
      status?: "running" | "done"
    }>
    [key: string]: unknown
  }
  created_at: string
}

export type ChatSession = {
  id: string
  notebook_id: string
  title: string | null
  created_at: string
  updated_at: string
  messages: PersistedMessage[]
}
