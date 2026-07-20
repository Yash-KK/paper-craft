import { Globe, Loader2, Plus, Send, Square } from "lucide-react"
import { useEffect, useRef, useState, type KeyboardEvent } from "react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Textarea } from "@/components/ui/textarea"

type ChatComposerProps = {
  isStreaming: boolean
  webSearch: boolean
  onWebSearchChange: (enabled: boolean) => void
  onSend: (question: string) => void
  onStop: () => void
}

export function ChatComposer({
  isStreaming,
  webSearch,
  onWebSearchChange,
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
    <div className="relative z-10 shrink-0 border-t bg-background px-4 py-3">
      <div className="mx-auto flex max-w-4xl flex-col gap-2 rounded-xl border bg-muted/40 p-3 focus-within:border-violet-300 focus-within:ring-1 focus-within:ring-violet-200">
        <Textarea
          ref={textareaRef}
          rows={1}
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask a question…"
          disabled={isStreaming}
          className="max-h-30 min-h-6 w-full resize-none border-0 bg-transparent p-0 shadow-none focus-visible:border-0 focus-visible:ring-0 disabled:bg-transparent dark:bg-transparent dark:disabled:bg-transparent"
        />

        <div className="flex items-center gap-1.5">
          <DropdownMenu>
            <DropdownMenuTrigger
              disabled={isStreaming}
              render={
                <Button
                  variant="ghost"
                  size="icon-xs"
                  className="text-muted-foreground"
                  title="Tools"
                  aria-label="Tools"
                />
              }
            >
              <Plus />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" side="top" sideOffset={8} className="min-w-44">
              <DropdownMenuGroup>
                <DropdownMenuLabel>Tools</DropdownMenuLabel>
                <DropdownMenuCheckboxItem
                  checked={webSearch}
                  onCheckedChange={(value) => onWebSearchChange(value === true)}
                >
                  Web Search
                </DropdownMenuCheckboxItem>
              </DropdownMenuGroup>
            </DropdownMenuContent>
          </DropdownMenu>

          {webSearch && (
            <Badge
              variant="secondary"
              className="h-7 cursor-pointer gap-1.5 overflow-visible rounded-full px-2.5 text-xs font-medium"
              onClick={() => !isStreaming && onWebSearchChange(false)}
              title="Remove Web Search"
            >
              <Globe />
              Web Search
            </Badge>
          )}

          <div className="ml-auto shrink-0">
            {isStreaming ? (
              <Button
                type="button"
                size="icon-xs"
                className="bg-red-500 text-white hover:bg-red-400"
                onClick={onStop}
                title="Stop"
              >
                <Square />
              </Button>
            ) : (
              <Button
                type="button"
                size="icon-xs"
                className="bg-violet-600 text-white hover:bg-violet-500"
                onClick={handleSend}
                disabled={!input.trim()}
                title="Send"
              >
                <Send />
              </Button>
            )}
          </div>
        </div>
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
