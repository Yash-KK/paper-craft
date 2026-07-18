import { Loader2 } from "lucide-react"

import { ChatMarkdown } from "@/features/chat/components/chat-markdown"
import { ToolCallCard } from "@/features/chat/components/tool-card"
import type { ChatMessage } from "@/features/chat/types/chat"

type ChatMessageBubbleProps = {
  message: ChatMessage
}

export function ChatMessageBubble({ message }: ChatMessageBubbleProps) {
  const hasRunningTools = message.toolCalls.some(
    (toolCall) => toolCall.status === "running"
  )
  const showThinking =
    message.role === "assistant" &&
    message.isStreaming &&
    message.content === "" &&
    !hasRunningTools

  return (
    <div
      className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
    >
      {message.role === "user" ? (
        <div className="max-w-[82%] rounded-2xl rounded-tr-sm bg-violet-600 px-4 py-2.5 text-sm leading-relaxed text-white">
          {message.content}
        </div>
      ) : (
        <div className="max-w-[92%] space-y-1">
          {message.toolCalls.map((toolCall) => (
            <ToolCallCard key={toolCall.id} tc={toolCall} />
          ))}

          {showThinking && (
            <div className="flex items-center gap-2 px-1 py-1.5 text-xs text-violet-500">
              <Loader2 size={13} className="animate-spin" />
              <span>Thinking…</span>
            </div>
          )}

          {message.content !== "" && (
            <div className="rounded-2xl rounded-tl-sm border bg-card px-4 py-3">
              <ChatMarkdown
                text={message.content}
                isStreaming={message.isStreaming}
              />
            </div>
          )}
        </div>
      )}
    </div>
  )
}
