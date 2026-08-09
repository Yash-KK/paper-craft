import { BookOpen, Globe, Loader2, Plus, Send, Square } from "lucide-react"
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
import { UsageLimitIndicator } from "@/components/usage-limit-indicator"
import type { ChatToolId } from "@/features/chat/types/chat"

const TOOL_OPTIONS: ReadonlyArray<{
  id: ChatToolId
  label: string
  icon: typeof BookOpen
}> = [
  { id: "retrieve_context", label: "Textbook", icon: BookOpen },
  { id: "web_search", label: "Web Search", icon: Globe },
]

type ChatComposerProps = {
  isStreaming: boolean
  enabledTools: ChatToolId[]
  onEnabledToolsChange: (tools: ChatToolId[]) => void
  onSend: (question: string) => void
  onStop: () => void
  chatUsage?: number
  chatLimit?: number
}

export function ChatComposer({
  isStreaming,
  enabledTools,
  onEnabledToolsChange,
  onSend,
  onStop,
  chatUsage = 0,
  chatLimit = 5,
}: ChatComposerProps) {
  const [input, setInput] = useState("")
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const atLimit = chatUsage >= chatLimit

  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = "auto"
    el.style.height = `${Math.min(el.scrollHeight, 120)}px`
  }, [input])

  const handleSend = () => {
    const question = input.trim()
    if (!question || isStreaming || atLimit) return
    setInput("")
    onSend(question)
  }

  const handleKey = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      handleSend()
    }
  }

  const toggleTool = (id: ChatToolId, on: boolean) => {
    if (on) {
      if (!enabledTools.includes(id))
        onEnabledToolsChange([...enabledTools, id])
      return
    }
    onEnabledToolsChange(enabledTools.filter((t) => t !== id))
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
          placeholder={
            atLimit ? "Chat message limit reached" : "Ask a question…"
          }
          disabled={isStreaming || atLimit}
          className="max-h-30 min-h-6 w-full resize-none border-0 bg-transparent p-0 shadow-none focus-visible:border-0 focus-visible:ring-0 disabled:bg-transparent dark:bg-transparent dark:disabled:bg-transparent"
        />

        <div className="flex items-center gap-1.5">
          <DropdownMenu>
            <DropdownMenuTrigger
              disabled={isStreaming || atLimit}
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
            <DropdownMenuContent
              align="start"
              side="top"
              sideOffset={8}
              className="min-w-44"
            >
              <DropdownMenuGroup>
                <DropdownMenuLabel>Tools</DropdownMenuLabel>
                {TOOL_OPTIONS.map((tool) => (
                  <DropdownMenuCheckboxItem
                    key={tool.id}
                    checked={enabledTools.includes(tool.id)}
                    onCheckedChange={(value) =>
                      toggleTool(tool.id, value === true)
                    }
                  >
                    {tool.label}
                  </DropdownMenuCheckboxItem>
                ))}
              </DropdownMenuGroup>
            </DropdownMenuContent>
          </DropdownMenu>

          {TOOL_OPTIONS.filter((tool) => enabledTools.includes(tool.id)).map(
            (tool) => {
              const Icon = tool.icon
              return (
                <Badge
                  key={tool.id}
                  variant="secondary"
                  className="h-7 cursor-pointer gap-1.5 overflow-visible rounded-full px-2.5 text-xs font-medium"
                  onClick={() =>
                    !isStreaming && !atLimit && toggleTool(tool.id, false)
                  }
                  title={`Remove ${tool.label}`}
                >
                  <Icon />
                  {tool.label}
                </Badge>
              )
            }
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
                disabled={!input.trim() || atLimit}
                title={
                  atLimit
                    ? `Chat message limit reached (${chatUsage}/${chatLimit})`
                    : "Send"
                }
              >
                <Send />
              </Button>
            )}
          </div>
        </div>
      </div>
      <div className="mt-1.5 flex items-center justify-center gap-2">
        <UsageLimitIndicator
          usage={chatUsage}
          limit={chatLimit}
          resource="chat_message"
        />
        {isStreaming ? (
          <p className="flex items-center gap-1.5 text-xs text-violet-500">
            <Loader2 size={11} className="animate-spin" />
            <span>Agent is thinking…</span>
          </p>
        ) : (
          <p className="text-xs text-muted-foreground">
            PaperCraft can make mistakes
          </p>
        )}
      </div>
    </div>
  )
}
