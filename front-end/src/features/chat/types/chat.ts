export type ChatRole = "user" | "assistant" | "system" | "tool"

export type Citation = {
  id: string
  title: string
  snippet: string
  book_code?: string
  chapter_number?: number
  chapter_name?: string
  score?: number
}

export type ToolEvent = {
  tool_call_id: string
  tool_name: string
  status: "pending" | "running" | "completed" | "failed"
  args?: Record<string, unknown>
  result?: unknown
  error?: string
}

export type ChatMessageContent =
  | { type: "text"; text: string }
  | { type: "reasoning"; text: string }
  | {
      type: "tool-call"
      toolCallId: string
      toolName: string
      args: Record<string, unknown>
      result?: unknown
    }

export type ChatMessage = {
  id: string
  role: ChatRole
  content: ChatMessageContent[]
  created_at?: string
  citations?: Citation[]
}

export type ConversationSummary = {
  id: string
  notebook_id: string
  title: string | null
  updated_at: string
}

export type ChatRunRequest = {
  notebook_id: string
  conversation_id: string | null
  client_message_id: string
  message: {
    role: "user"
    content: string
  }
  metadata?: {
    retrieve?: boolean
    top_k?: number
    tools_enabled?: boolean
  }
}

export type ChatStreamEvent =
  | {
      type: "run.started"
      event_id: string
      conversation_id: string
      run_id: string
    }
  | {
      type: "message.delta"
      event_id: string
      message_id: string
      delta: string
    }
  | {
      type: "message.completed"
      event_id: string
      message_id: string
      content: string
      citations?: Citation[]
    }
  | {
      type: "citation"
      event_id: string
      citation: Citation
    }
  | {
      type: "retrieved_sources"
      event_id: string
      sources: Citation[]
    }
  | {
      type: "tool.started" | "tool.completed" | "tool.failed"
      event_id: string
      tool: ToolEvent
    }
  | {
      type: "run.completed"
      event_id: string
      run_id: string
      conversation_id: string
    }
  | {
      type: "run.error"
      event_id: string
      run_id: string
      error: string
    }

export type ChatTransport = {
  streamRun: (
    request: ChatRunRequest,
    options?: { signal?: AbortSignal }
  ) => AsyncIterable<ChatStreamEvent>
}
