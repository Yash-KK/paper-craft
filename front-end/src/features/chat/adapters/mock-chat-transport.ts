import { streamMockReply } from "@/features/chat/adapters/mock-responses"
import type {
  ChatRunRequest,
  ChatStreamEvent,
  ChatTransport,
} from "@/features/chat/types/chat"

function newId(prefix: string): string {
  return `${prefix}-${crypto.randomUUID()}`
}

/**
 * Mock transport that mirrors the future SSE Agentic RAG contract.
 * Swap this for a real `SseChatTransport` without changing the UI.
 */
export function createMockChatTransport(options: {
  notebookId: string
  notebookName: string
}): ChatTransport {
  const { notebookId, notebookName } = options

  return {
    async *streamRun(
      request: ChatRunRequest,
      opts?: { signal?: AbortSignal }
    ): AsyncIterable<ChatStreamEvent> {
      if (request.notebook_id !== notebookId) {
        yield {
          type: "run.error",
          event_id: newId("evt"),
          run_id: newId("run"),
          error: "Notebook mismatch",
        }
        return
      }

      const conversationId =
        request.conversation_id ?? newId("conv")
      const runId = newId("run")
      const messageId = newId("msg")

      try {
        yield* streamMockReply({
          userText: request.message.content,
          notebookName,
          conversationId,
          runId,
          messageId,
          signal: opts?.signal,
        })
      } catch (err) {
        if (err instanceof DOMException && err.name === "AbortError") {
          return
        }
        yield {
          type: "run.error",
          event_id: newId("evt"),
          run_id: runId,
          error: err instanceof Error ? err.message : "Mock run failed",
        }
      }
    },
  }
}
