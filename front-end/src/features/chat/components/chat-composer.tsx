import { Loader2, Send, Square } from "lucide-react"
import { useEffect, useRef, useState, type KeyboardEvent } from "react"

type ChatComposerProps = {
  isStreaming: boolean
  onSend: (question: string) => void
  onStop: () => void
}

export function ChatComposer({
  isStreaming,
  onSend,
  onStop,
}: ChatComposerProps) {
  const [input, setInput] = useState("")
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = "auto"
    el.style.height = `${Math.min(el.scrollHeight, 120)}px`
  }, [input])

  const handleSend = () => {
    const question = input.trim()
    if (!question || isStreaming) return
    setInput("")
    onSend(question)
  }

  const handleKey = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="shrink-0 border-t px-4 py-3">
      <div className="mx-auto flex max-w-4xl items-end gap-2 rounded-xl border bg-muted/40 px-3 py-2 focus-within:border-violet-300 focus-within:ring-1 focus-within:ring-violet-200">
        <textarea
          ref={textareaRef}
          rows={1}
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask a question…"
          disabled={isStreaming}
          className="max-h-[120px] min-h-[24px] flex-1 resize-none bg-transparent text-sm leading-relaxed outline-none placeholder:text-muted-foreground disabled:opacity-50"
        />

        {isStreaming ? (
          <button
            type="button"
            onClick={onStop}
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
          <kbd className="rounded bg-muted px-1 font-mono">Shift+Enter</kbd> new
          line
        </p>
      )}
    </div>
  )
}
