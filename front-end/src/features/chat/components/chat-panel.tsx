import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { MathJaxContext } from "better-react-mathjax"
import { Loader2 } from "lucide-react"

import { ChatComposer } from "@/features/chat/components/chat-composer"
import { ChatEmptyState } from "@/features/chat/components/chat-empty-state"
import { ChatMessageBubble } from "@/features/chat/components/chat-message"
import { useChatStream } from "@/features/chat/hooks/use-chat-stream"
import { useNotebookChatMessages } from "@/hooks/use-notebook-chat-messages"

const mathJaxConfig = {
  loader: { load: ["input/tex", "output/chtml"] },
  tex: {
    inlineMath: [
      ["$", "$"],
      ["\\(", "\\)"],
    ],
    displayMath: [
      ["$$", "$$"],
      ["\\[", "\\]"],
    ],
    processEscapes: true,
    packages: { "[+]": ["ams"] },
  },
}

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
  const historyReady = !isPending && !isError

  const {
    messages,
    isStreaming,
    enabledTools,
    setEnabledTools,
    sendMessage,
    stopStream,
    prependOlderMessages,
  } = useChatStream(notebookId, [])

  const scrollRef = useRef<HTMLDivElement>(null)
  const topSentinelRef = useRef<HTMLDivElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const stickToBottomRef = useRef(true)
  const loadingOlderRef = useRef(false)
  const primedRef = useRef(false)
  const [isFetchingOlder, setIsFetchingOlder] = useState(false)

  useEffect(() => {
    if (!historyReady || primedRef.current) return
    if (initialMessages.length) {
      prependOlderMessages(initialMessages)
    }
    primedRef.current = true
  }, [historyReady, initialMessages, prependOlderMessages])

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

  useEffect(() => {
    if (stickToBottomRef.current) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages, isStreaming])

  useEffect(() => {
    const viewport = scrollRef.current
    const sentinel = topSentinelRef.current
    if (!viewport || !sentinel || !historyReady) return

    const onScroll = () => {
      const distanceFromBottom =
        viewport.scrollHeight - viewport.scrollTop - viewport.clientHeight
      stickToBottomRef.current = distanceFromBottom < 96
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
  }, [historyReady, loadOlder])

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

  const showFetchingOlder = isFetchingOlder || isFetchingNextPage

  return (
    <MathJaxContext config={mathJaxConfig}>
      <div className="flex h-full min-h-0 flex-col overflow-hidden bg-background">
        <div ref={scrollRef} className="min-h-0 flex-1 overflow-y-auto">
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

            {messages.map((message) => (
              <ChatMessageBubble key={message.id} message={message} />
            ))}

            <div ref={bottomRef} />
          </div>
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
