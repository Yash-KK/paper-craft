import {
  AssistantRuntimeProvider,
  useLocalRuntime,
  type ChatModelAdapter,
  type ThreadMessageLike,
} from "@assistant-ui/react"
import { useQueryClient } from "@tanstack/react-query"
import * as React from "react"

import type {
  ChatMessage,
  ChatSession,
} from "@/features/chat/types/chat"
import { sendNotebookChatMessage } from "@/lib/api"
import { queryKeys } from "@/lib/query-keys"

type ChatRuntimeProviderProps = {
  notebookId: string
  messages: ChatMessage[]
  children: React.ReactNode
}

function createAdapter({
  notebookId,
  onTurnCompleted,
}: {
  notebookId: string
  onTurnCompleted: (session: ChatSession) => void
}): ChatModelAdapter {
  return {
    async run({ messages, abortSignal }) {
      const lastUser = [...messages].reverse().find((m) => m.role === "user")

      const text =
        lastUser?.content
          .filter((c): c is { type: "text"; text: string } => c.type === "text")
          .map((c) => c.text)
          .join("\n") ?? ""

      if (!text.trim()) {
        throw new Error("Message cannot be blank")
      }

      const turn = await sendNotebookChatMessage(
        notebookId,
        text,
        abortSignal
      )
      onTurnCompleted({
        id: turn.session_id,
        notebook_id: notebookId,
        title: null,
        created_at: turn.user_message.created_at,
        updated_at: turn.assistant_message.created_at,
        messages: [turn.user_message, turn.assistant_message],
      })

      return {
        content: [
          {
            type: "text" as const,
            text: turn.assistant_message.content,
          },
        ],
      }
    },
  }
}

export function ChatRuntimeProvider({
  notebookId,
  messages,
  children,
}: ChatRuntimeProviderProps) {
  const queryClient = useQueryClient()
  const onTurnCompleted = React.useCallback(
    (turnSession: ChatSession) => {
      queryClient.setQueryData<ChatSession>(
        queryKeys.notebookChat(notebookId),
        (current) =>
          current
            ? {
                ...current,
                updated_at: turnSession.updated_at,
                messages: [...current.messages, ...turnSession.messages],
              }
            : turnSession
      )
    },
    [notebookId, queryClient]
  )

  const adapter = React.useMemo(
    () => createAdapter({ notebookId, onTurnCompleted }),
    [notebookId, onTurnCompleted]
  )

  const initialMessages = React.useMemo<ThreadMessageLike[]>(
    () =>
      messages.flatMap((message) =>
        message.role === "user" || message.role === "assistant"
          ? [{ role: message.role, content: message.content }]
          : []
      ),
    [messages]
  )
  const runtime = useLocalRuntime(adapter, { initialMessages })

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      {children}
    </AssistantRuntimeProvider>
  )
}
