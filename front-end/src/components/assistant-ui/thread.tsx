import {
  ActionBarPrimitive,
  AuiIf,
  ComposerPrimitive,
  MessagePrimitive,
  ThreadPrimitive,
} from "@assistant-ui/react"
import {
  ArrowDownIcon,
  ArrowUpIcon,
  CopyIcon,
  RefreshCwIcon,
  SquareIcon,
} from "lucide-react"

import { MarkdownText } from "@/components/assistant-ui/markdown-text"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

function ThreadWelcome({ notebookName }: { notebookName: string }) {
  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col items-center gap-6 px-4 py-16 text-center">
      <div className="space-y-2">
        <h2 className="font-heading text-2xl font-semibold tracking-tight">
          Chat with {notebookName}
        </h2>
        <p className="max-w-md text-sm text-muted-foreground">
          Ask for explanations, practice questions, or a full question paper.
          Responses are mocked until the Agentic RAG backend is connected.
        </p>
      </div>
      <div className="flex w-full flex-wrap justify-center gap-2">
        {[
          "Explain the key concepts in this notebook",
          "Generate 5 MCQs from selected chapters",
          "Draft a 20-mark question paper outline",
        ].map((prompt) => (
          <ThreadPrimitive.Suggestion
            key={prompt}
            prompt={prompt}
            send
            className="rounded-full border bg-card px-3 py-1.5 text-left text-xs text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            {prompt}
          </ThreadPrimitive.Suggestion>
        ))}
      </div>
    </div>
  )
}

function UserMessage() {
  return (
    <MessagePrimitive.Root className="mx-auto w-full max-w-5xl px-4 py-3">
      <div className="ml-auto max-w-[85%] rounded-2xl rounded-br-md bg-violet-600 px-4 py-2.5 text-sm whitespace-pre-wrap text-white dark:bg-violet-900">
        <MessagePrimitive.Parts />
      </div>
    </MessagePrimitive.Root>
  )
}

function AssistantMessage() {
  return (
    <MessagePrimitive.Root className="mx-auto w-full max-w-5xl px-4 py-3">
      <div className="mr-auto flex max-w-[92%] flex-col gap-2">
        <div className="rounded-2xl rounded-bl-md border bg-card px-4 py-3 text-sm shadow-sm ring-1 ring-foreground/5">
          <MessagePrimitive.Parts
            components={{
              Text: MarkdownText,
            }}
          />
        </div>
        <MessagePrimitive.Error>
          <p className="px-1 text-xs text-destructive">
            Something went wrong generating this reply.
          </p>
        </MessagePrimitive.Error>
        <ActionBarPrimitive.Root
          hideWhenRunning
          autohide="not-last"
          className="flex items-center gap-1 text-muted-foreground"
        >
          <ActionBarPrimitive.Copy asChild>
            <Button
              type="button"
              variant="ghost"
              size="icon-sm"
              className="size-7"
              aria-label="Copy message"
            >
              <CopyIcon className="size-3.5" />
            </Button>
          </ActionBarPrimitive.Copy>
          <ActionBarPrimitive.Reload asChild>
            <Button
              type="button"
              variant="ghost"
              size="icon-sm"
              className="size-7"
              aria-label="Regenerate"
            >
              <RefreshCwIcon className="size-3.5" />
            </Button>
          </ActionBarPrimitive.Reload>
        </ActionBarPrimitive.Root>
      </div>
    </MessagePrimitive.Root>
  )
}

function Composer() {
  return (
    <ComposerPrimitive.Root className="mx-auto flex w-full max-w-4xl flex-col gap-2 rounded-xl border bg-card p-2 shadow-sm ring-1 ring-foreground/5">
      <ComposerPrimitive.Input
        rows={1}
        autoFocus
        placeholder="Message this notebook…"
        className="max-h-40 min-h-11 w-full resize-none bg-transparent px-3 py-2.5 text-sm outline-none placeholder:text-muted-foreground"
      />
      <div className="flex items-center justify-between gap-2 px-1 pb-0.5">
        <p className="text-[11px] text-muted-foreground">
          Mock streaming · Enter to send
        </p>
        <AuiIf condition={(s) => !s.thread.isRunning}>
          <ComposerPrimitive.Send asChild>
            <Button
              type="button"
              size="icon"
              className="size-8 rounded-full bg-violet-600 text-white hover:bg-violet-600/90"
              aria-label="Send message"
            >
              <ArrowUpIcon className="size-4" />
            </Button>
          </ComposerPrimitive.Send>
        </AuiIf>
        <AuiIf condition={(s) => s.thread.isRunning}>
          <ComposerPrimitive.Cancel asChild>
            <Button
              type="button"
              size="icon"
              variant="secondary"
              className="size-8 rounded-full"
              aria-label="Stop generating"
            >
              <SquareIcon className="size-3.5 fill-current" />
            </Button>
          </ComposerPrimitive.Cancel>
        </AuiIf>
      </div>
    </ComposerPrimitive.Root>
  )
}

export function Thread({ notebookName }: { notebookName: string }) {
  return (
    <ThreadPrimitive.Root
      className={cn(
        "flex h-full min-h-0 flex-col overflow-hidden bg-background"
      )}
    >
      <ThreadPrimitive.Viewport className="relative flex min-h-0 flex-1 flex-col overflow-y-auto overscroll-contain">
        <AuiIf condition={(s) => s.thread.isEmpty}>
          <ThreadWelcome notebookName={notebookName} />
        </AuiIf>

        <ThreadPrimitive.Messages
          components={{
            UserMessage,
            AssistantMessage,
          }}
        />

        <ThreadPrimitive.ViewportFooter className="sticky bottom-0 z-10 mt-auto shrink-0 border-t bg-background/90 px-4 py-3 backdrop-blur supports-backdrop-filter:bg-background/75">
          <div className="relative mx-auto w-full max-w-5xl">
            <ThreadPrimitive.ScrollToBottom asChild>
              <Button
                type="button"
                variant="outline"
                size="icon-sm"
                className="absolute -top-12 right-0 size-8 rounded-full shadow-sm disabled:invisible"
                aria-label="Scroll to bottom"
              >
                <ArrowDownIcon className="size-4" />
              </Button>
            </ThreadPrimitive.ScrollToBottom>
            <Composer />
          </div>
        </ThreadPrimitive.ViewportFooter>
      </ThreadPrimitive.Viewport>
    </ThreadPrimitive.Root>
  )
}
