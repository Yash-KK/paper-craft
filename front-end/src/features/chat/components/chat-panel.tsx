import { useEffect, useRef } from "react"

import { ScrollArea } from "@/components/ui/scroll-area"
import { ChatComposer } from "@/features/chat/components/chat-composer"
import { ChatEmptyState } from "@/features/chat/components/chat-empty-state"
import { ChatMessageBubble } from "@/features/chat/components/chat-message"
import { useChatStream } from "@/features/chat/hooks/use-chat-stream"
import type { PersistedMessage } from "@/features/chat/types/chat"

type ChatPanelProps = {
  notebookId: string
  notebookName: string
  initialMessages: PersistedMessage[]
}

export function ChatPanel({
  notebookId,
  notebookName,
  initialMessages,
}: ChatPanelProps) {
  const {
    messages,
    isStreaming,
    webSearch,
    setWebSearch,
    sendMessage,
    stopStream,
  } = useChatStream(notebookId, initialMessages)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isStreaming])

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden bg-background">
      <ScrollArea className="min-h-0 flex-1">
        <div className="min-h-full space-y-4 px-4 py-4">
          {messages.length === 0 && (
            <ChatEmptyState
              notebookName={notebookName}
              onSend={(prompt) => void sendMessage(prompt)}
            />
          )}

          {messages.map((message) => (
            <ChatMessageBubble key={message.id} message={message} />
          ))}

          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      <ChatComposer
        isStreaming={isStreaming}
        webSearch={webSearch}
        onWebSearchChange={setWebSearch}
        onSend={(question) => void sendMessage(question)}
        onStop={stopStream}
      />
    </div>
  )
}
