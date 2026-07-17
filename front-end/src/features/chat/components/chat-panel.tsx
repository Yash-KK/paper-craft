import { Loader2, Send, Square } from "lucide-react"
import { useEffect, useRef, useState, type KeyboardEvent, type ReactNode } from "react"

import { ScrollArea } from "@/components/ui/scroll-area"
import { ToolCallCard } from "@/features/chat/components/tool-card"
import { useChatStream } from "@/features/chat/hooks/use-chat-stream"
import type { PersistedMessage } from "@/features/chat/types/chat"

type ChatPanelProps = {
  notebookId: string
  notebookName: string
  initialMessages: PersistedMessage[]
}

function renderContent(text: string) {
  const lines = text.split("\n")
  const elements: ReactNode[] = []

  lines.forEach((line, i) => {
    const isBullet = /^[-*•]\s/.test(line)
    const content = line.replace(/^[-*•]\s/, "")
    const parts: ReactNode[] = []
    const pattern = /(\*\*[^*]+\*\*|`[^`]+`)/g
    let last = 0
    let match: RegExpExecArray | null
    let part = 0

    while ((match = pattern.exec(content)) !== null) {
      if (match.index > last) parts.push(content.slice(last, match.index))
      const token = match[0]
      if (token.startsWith("**")) {
        parts.push(<strong key={`${i}-${part}`}>{token.slice(2, -2)}</strong>)
      } else {
        parts.push(
          <code
            key={`${i}-${part}`}
            className="rounded bg-muted px-1 py-0.5 font-mono text-xs text-violet-700"
          >
            {token.slice(1, -1)}
          </code>
        )
      }
      last = match.index + token.length
      part += 1
    }
    if (last < content.length) parts.push(content.slice(last))

    if (isBullet) {
      elements.push(
        <li key={i} className="ml-4 list-disc">
          {parts}
        </li>
      )
    } else if (content.trim()) {
      elements.push(
        <p key={i} className="mb-1">
          {parts}
        </p>
      )
    } else {
      elements.push(<br key={i} />)
    }
  })

  return <div className="text-sm leading-relaxed">{elements}</div>
}

export function ChatPanel({
  notebookId,
  notebookName,
  initialMessages,
}: ChatPanelProps) {
  const { messages, isStreaming, sendMessage, stopStream } = useChatStream(
    notebookId,
    initialMessages
  )
  const [input, setInput] = useState("")
  const bottomRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isStreaming])

  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = "auto"
    el.style.height = `${Math.min(el.scrollHeight, 120)}px`
  }, [input])

  const handleSend = () => {
    const q = input.trim()
    if (!q || isStreaming) return
    setInput("")
    void sendMessage(q)
  }

  const handleKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden bg-background">
      <ScrollArea className="min-h-0 flex-1">
        <div className="min-h-full space-y-4 px-4 py-4">
          {messages.length === 0 && (
            <div className="flex min-h-[60vh] flex-col items-center justify-center pb-8 text-center select-none">
            <h2 className="font-heading mb-2 text-xl font-semibold">
              Chat with {notebookName}
            </h2>
            <p className="mb-5 max-w-sm text-sm text-muted-foreground">
              Ask for explanations or worked examples grounded in this
              notebook&apos;s chapters.
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {[
                "Explain the key concepts in this notebook",
                "Walk me through a worked example",
              ].map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => void sendMessage(s)}
                  className="rounded-full border bg-card px-3 py-1.5 text-xs text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                >
                  {s}
                </button>
              ))}
            </div>
            </div>
          )}

          {messages.map((msg) => {
            const hasRunningTools = msg.toolCalls.some(
              (tc) => tc.status === "running"
            )
            const showThinking =
              msg.role === "assistant" &&
              msg.isStreaming &&
              msg.content === "" &&
              !hasRunningTools

            return (
              <div
                key={msg.id}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.role === "user" ? (
                  <div className="max-w-[82%] rounded-2xl rounded-tr-sm bg-violet-600 px-4 py-2.5 text-sm leading-relaxed text-white">
                    {msg.content}
                  </div>
                ) : (
                  <div className="max-w-[92%] space-y-1">
                    {msg.toolCalls.map((tc) => (
                      <ToolCallCard key={tc.id} tc={tc} />
                    ))}

                    {showThinking && (
                      <div className="flex items-center gap-2 px-1 py-1.5 text-xs text-violet-500">
                        <Loader2 size={13} className="animate-spin" />
                        <span>Thinking…</span>
                      </div>
                    )}

                    {msg.content !== "" && (
                      <div className="rounded-2xl rounded-tl-sm border bg-card px-4 py-3">
                        {renderContent(msg.content)}
                        {msg.isStreaming && (
                          <span className="ml-0.5 inline-block h-4 w-0.5 animate-pulse bg-violet-500 align-text-bottom" />
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}

          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      <div className="shrink-0 border-t px-4 py-3">
        <div className="mx-auto flex max-w-4xl items-end gap-2 rounded-xl border bg-muted/40 px-3 py-2 focus-within:border-violet-300 focus-within:ring-1 focus-within:ring-violet-200">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Ask a question…"
            disabled={isStreaming}
            className="max-h-[120px] min-h-[24px] flex-1 resize-none bg-transparent text-sm leading-relaxed outline-none placeholder:text-muted-foreground disabled:opacity-50"
          />

          {isStreaming ? (
            <button
              type="button"
              onClick={stopStream}
              className="mb-0.5 shrink-0 rounded-lg bg-red-500 p-1.5 text-white hover:bg-red-400"
              title="Stop"
            >
              <Square size={13} />
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSend}
              disabled={!input.trim()}
              className="mb-0.5 shrink-0 rounded-lg bg-violet-600 p-1.5 text-white hover:bg-violet-500 disabled:opacity-30"
              title="Send"
            >
              <Send size={13} />
            </button>
          )}
        </div>
        {isStreaming ? (
          <p className="mt-1.5 flex items-center justify-center gap-1.5 text-center text-xs text-violet-500">
            <Loader2 size={11} className="animate-spin" />
            <span>Agent is thinking…</span>
          </p>
        ) : (
          <p className="mt-1.5 text-center text-xs text-muted-foreground">
            <kbd className="rounded bg-muted px-1 font-mono">Enter</kbd> send ·{" "}
            <kbd className="rounded bg-muted px-1 font-mono">Shift+Enter</kbd>{" "}
            new line
          </p>
        )}
      </div>
    </div>
  )
}
