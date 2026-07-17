export type ChatRole = "user" | "assistant" | "system" | "tool"

export type Citation = {
  id: string
  title: string
  snippet: string
  book_code?: string
  chapter_number?: number
  chapter_name?: string
  page_number?: number
  score?: number
}

export type ChatMessage = {
  id: string
  session_id: string
  role: ChatRole
  content: string
  metadata: {
    citations?: Citation[]
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
  messages: ChatMessage[]
}

export type ChatTurnResponse = {
  session_id: string
  user_message: ChatMessage
  assistant_message: ChatMessage
}
