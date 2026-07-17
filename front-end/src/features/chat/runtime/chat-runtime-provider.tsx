import {
  AssistantRuntimeProvider,
  useLocalRuntime,
  type ChatModelAdapter,
} from "@assistant-ui/react"
import * as React from "react"

import { createMockChatTransport } from "@/features/chat/adapters/mock-chat-transport"
import type { ChatTransport } from "@/features/chat/types/chat"

type ChatRuntimeProviderProps = {
  notebookId: string
  notebookName: string
  children: React.ReactNode
  transport?: ChatTransport
}

function createAdapter(
  transport: ChatTransport,
  notebookId: string
): ChatModelAdapter {
  return {
    async *run({ messages, abortSignal }) {
      const lastUser = [...messages].reverse().find((m) => m.role === "user")

      const text =
        lastUser?.content
          .filter((c): c is { type: "text"; text: string } => c.type === "text")
          .map((c) => c.text)
          .join("\n") ?? ""

      let accumulated = ""

      for await (const event of transport.streamRun(
        {
          notebook_id: notebookId,
          conversation_id: null,
          client_message_id: crypto.randomUUID(),
          message: { role: "user", content: text },
          metadata: { retrieve: true, top_k: 4, tools_enabled: true },
        },
        { signal: abortSignal }
      )) {
        if (event.type === "message.delta") {
          accumulated += event.delta
          yield {
            content: [{ type: "text" as const, text: accumulated }],
          }
        }

        if (event.type === "message.completed") {
          accumulated = event.content
          yield {
            content: [{ type: "text" as const, text: accumulated }],
          }
        }

        if (event.type === "run.error") {
          throw new Error(event.error)
        }
      }

      if (!accumulated) {
        yield {
          content: [
            {
              type: "text" as const,
              text: "No response generated.",
            },
          ],
        }
      }
    },
  }
}

export function ChatRuntimeProvider({
  notebookId,
  notebookName,
  children,
  transport: transportOverride,
}: ChatRuntimeProviderProps) {
  const transport = React.useMemo(
    () =>
      transportOverride ??
      createMockChatTransport({ notebookId, notebookName }),
    [transportOverride, notebookId, notebookName]
  )

  const adapter = React.useMemo(
    () => createAdapter(transport, notebookId),
    [transport, notebookId]
  )

  const runtime = useLocalRuntime(adapter)

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      {children}
    </AssistantRuntimeProvider>
  )
}
