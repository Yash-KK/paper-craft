import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { MathJaxContext } from "better-react-mathjax"
import { Loader2 } from "lucide-react"

import { ScrollArea } from "@/components/ui/scroll-area"
import { ChatComposer } from "@/features/chat/components/chat-composer"
import { ChatEmptyState } from "@/features/chat/components/chat-empty-state"
import { ChatMessageBubble } from "@/features/chat/components/chat-message"
import { ScrollToBottomButton } from "@/features/chat/components/scroll-to-bottom-button"
import { isPersistedChatMessageId } from "@/features/chat/lib/chat-stream-utils"
import { useChatSelectionOptional } from "@/providers/chat-selection-provider"
import { useChatStream } from "@/features/chat/hooks/use-chat-stream"
import { MATHJAX_CONFIG } from "@/features/chat/lib/mathjax-config"
import type { PersistedMessage } from "@/features/chat/types/chat"
import { useNotebookChatMessages } from "@/hooks/use-notebook-chat-messages"

const NEAR_BOTTOM_PX = 96

type ChatPanelProps = {
  notebookId: string
  notebookName: string
}

export function ChatPanel({ notebookId, notebookName }: ChatPanelProps) {
  const {
    data,
    error,
    isPending,
    isError,
    hasNextPage,
    isFetchingNextPage,
    fetchNextPage,
  } = useNotebookChatMessages(notebookId)

  const initialMessages = useMemo(() => data?.pages[0]?.items ?? [], [data])

  if (isPending) {
    return (
      <div className="flex h-full items-center justify-center gap-2 text-sm text-muted-foreground">
        <Loader2 className="size-4 animate-spin" />
        Fetching…
      </div>
    )
  }

  if (isError) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 px-4 text-center">
        <p className="text-sm font-medium">Unable to load messages</p>
        <p className="text-xs text-muted-foreground">
          {error instanceof Error ? error.message : "Please try again."}
        </p>
      </div>
    )
  }

  return (
    <ChatPanelReady
      key={notebookId}
      notebookId={notebookId}
      notebookName={notebookName}
      initialMessages={initialMessages}
      hasNextPage={Boolean(hasNextPage)}
      isFetchingNextPage={isFetchingNextPage}
      fetchNextPage={fetchNextPage}
    />
  )
}

type ChatPanelReadyProps = {
  notebookId: string
  notebookName: string
  initialMessages: PersistedMessage[]
  hasNextPage: boolean
  isFetchingNextPage: boolean
  fetchNextPage: ReturnType<typeof useNotebookChatMessages>["fetchNextPage"]
}

function ChatPanelReady({
  notebookId,
  notebookName,
  initialMessages,
  hasNextPage,
  isFetchingNextPage,
  fetchNextPage,
}: ChatPanelReadyProps) {
  const selection = useChatSelectionOptional()
  const {
    messages,
    isStreaming,
    enabledTools,
    setEnabledTools,
    sendMessage,
    stopStream,
    prependOlderMessages,
  } = useChatStream(notebookId, initialMessages)

  const scrollRef = useRef<HTMLDivElement>(null)
  const topSentinelRef = useRef<HTMLDivElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const stickToBottomRef = useRef(true)
  const loadingOlderRef = useRef(false)
  const [initialScrollDone, setInitialScrollDone] = useState(false)
  const [isFetchingOlder, setIsFetchingOlder] = useState(false)
  const [showScrollToBottom, setShowScrollToBottom] = useState(false)

  const scrollToBottom = useCallback(() => {
    stickToBottomRef.current = true
    setShowScrollToBottom(false)
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [])

  const loadOlder = useCallback(async () => {
    if (!hasNextPage || isFetchingNextPage || loadingOlderRef.current) return

    const viewport = scrollRef.current
    if (!viewport) return

    loadingOlderRef.current = true
    setIsFetchingOlder(true)
    const previousHeight = viewport.scrollHeight
    const previousTop = viewport.scrollTop

    try {
      const result = await fetchNextPage()
      const pages = result.data?.pages
      const older = pages?.[pages.length - 1]?.items ?? []
      if (older.length) {
        prependOlderMessages(older)
        requestAnimationFrame(() => {
          viewport.scrollTop =
            viewport.scrollHeight - previousHeight + previousTop
        })
      }
    } finally {
      loadingOlderRef.current = false
      setIsFetchingOlder(false)
    }
  }, [fetchNextPage, hasNextPage, isFetchingNextPage, prependOlderMessages])

  // Animate down to the latest messages when the notebook first opens.
  // Gate on state (not a ref) so React Strict Mode cleanup → re-run still finishes.
  useEffect(() => {
    if (initialScrollDone) return

    const viewport = scrollRef.current
    if (!viewport) return

    let cancelled = false
    let fallback = 0

    const finish = () => {
      if (!cancelled) setInitialScrollDone(true)
    }

    const run = () => {
      if (cancelled) return

      stickToBottomRef.current = true
      setShowScrollToBottom(false)

      if (viewport.scrollHeight <= viewport.clientHeight) {
        finish()
        return
      }

      viewport.scrollTo({ top: viewport.scrollHeight, behavior: "smooth" })
      // `scrollend` is not in every browser yet, so cap the wait with a timer.
      viewport.addEventListener("scrollend", finish, { once: true })
      fallback = window.setTimeout(finish, 800)
    }

    // Double rAF: wait until ScrollArea has laid out message content.
    const raf = requestAnimationFrame(() => {
      requestAnimationFrame(run)
    })

    return () => {
      cancelled = true
      cancelAnimationFrame(raf)
      viewport.removeEventListener("scrollend", finish)
      window.clearTimeout(fallback)
    }
  }, [messages, initialScrollDone])

  useEffect(() => {
    if (!initialScrollDone || !stickToBottomRef.current) return
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isStreaming, initialScrollDone])

  useEffect(() => {
    const viewport = scrollRef.current
    const sentinel = topSentinelRef.current
    if (!viewport || !sentinel || !initialScrollDone) {
      return
    }

    const onScroll = () => {
      const distanceFromBottom =
        viewport.scrollHeight - viewport.scrollTop - viewport.clientHeight
      const nearBottom = distanceFromBottom < NEAR_BOTTOM_PX
      stickToBottomRef.current = nearBottom
      setShowScrollToBottom((prev) => {
        const next = !nearBottom
        return prev === next ? prev : next
      })
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          void loadOlder()
        }
      },
      {
        root: viewport,
        rootMargin: "80px 0px 0px 0px",
        threshold: 0,
      }
    )

    viewport.addEventListener("scroll", onScroll, { passive: true })
    observer.observe(sentinel)
    return () => {
      viewport.removeEventListener("scroll", onScroll)
      observer.disconnect()
    }
  }, [initialScrollDone, loadOlder])

  const showFetchingOlder = isFetchingOlder || isFetchingNextPage

  return (
    <MathJaxContext config={MATHJAX_CONFIG}>
      <div className="flex h-full min-h-0 flex-col overflow-hidden bg-background">
        <div className="relative min-h-0 flex-1">
          <ScrollArea className="h-full" viewportRef={scrollRef}>
            <div className="min-h-full space-y-4 px-4 py-4">
              <div ref={topSentinelRef} className="h-px w-full" aria-hidden />

              {showFetchingOlder ? (
                <div className="flex items-center justify-center gap-2 py-2 text-xs text-muted-foreground">
                  <Loader2 className="size-3.5 animate-spin" />
                  Fetching…
                </div>
              ) : hasNextPage ? (
                <p className="py-1 text-center text-[11px] text-muted-foreground/80">
                  Scroll up for older messages
                </p>
              ) : messages.length > 0 ? (
                <p className="py-1 text-center text-[11px] text-muted-foreground/80">
                  Beginning of conversation
                </p>
              ) : null}

              {messages.length === 0 && (
                <ChatEmptyState
                  notebookName={notebookName}
                  onSend={(prompt) => void sendMessage(prompt)}
                />
              )}

              {messages.map((message) => {
                const selectable =
                  Boolean(selection) &&
                  !message.isStreaming &&
                  isPersistedChatMessageId(message.id)
                return (
                  <ChatMessageBubble
                    key={message.id}
                    message={message}
                    selectable={selectable}
                    selected={selection?.isSelected(message.id) ?? false}
                    onToggleSelect={
                      selectable
                        ? () => selection?.toggle(message.id)
                        : undefined
                    }
                  />
                )
              })}

              <div ref={bottomRef} />
            </div>
          </ScrollArea>

          <ScrollToBottomButton
            visible={showScrollToBottom}
            onClick={scrollToBottom}
          />
        </div>

        <ChatComposer
          isStreaming={isStreaming}
          enabledTools={enabledTools}
          onEnabledToolsChange={setEnabledTools}
          onSend={(question) => void sendMessage(question)}
          onStop={stopStream}
        />
      </div>
    </MathJaxContext>
  )
}
