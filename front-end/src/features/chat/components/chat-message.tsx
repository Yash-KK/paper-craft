import { Loader2 } from "lucide-react"

import { ChatMarkdown } from "@/features/chat/components/chat-markdown"
import { ToolCallCard } from "@/features/chat/components/tool-card"
import type { ChatMessage } from "@/features/chat/types/chat"

export function ChatMessageBubble({ message }: { message: ChatMessage }) {
  const hasRunningTools = message.toolCalls.some(
    (tc) => tc.status === "running"
  )
  const showThinking =
    message.role === "assistant" &&
    message.isStreaming &&
    message.content === "" &&
    !hasRunningTools

  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[82%] rounded-2xl rounded-tr-sm bg-violet-600 px-4 py-2.5 text-sm leading-relaxed text-white">
          {message.content}
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-[92%] space-y-1">
        {message.toolCalls.map((tc) => (
          <ToolCallCard key={tc.id} tc={tc} />
        ))}

        {showThinking && (
          <div className="flex items-center gap-2 px-1 py-1.5 text-xs text-violet-500">
            <Loader2 size={13} className="animate-spin" />
            <span>Thinking…</span>
          </div>
        )}

        {message.content !== "" && (
          <div className="rounded-2xl rounded-tl-sm border bg-card px-4 py-3">
            <ChatMarkdown text={message.content} />
          </div>
        )}
      </div>
    </div>
  )
}
