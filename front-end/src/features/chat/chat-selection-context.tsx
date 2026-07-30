/* eslint-disable react-refresh/only-export-components */
import * as React from "react"

type ChatSelectionContextValue = {
  selectedIds: Set<string>
  isSelected: (id: string) => boolean
  toggle: (id: string) => void
  clear: () => void
  selectedCount: number
}

const ChatSelectionContext =
  React.createContext<ChatSelectionContextValue | null>(null)

export function ChatSelectionProvider({
  children,
}: {
  children: React.ReactNode
}) {
  const [selectedIds, setSelectedIds] = React.useState<Set<string>>(
    () => new Set()
  )

  const value = React.useMemo<ChatSelectionContextValue>(
    () => ({
      selectedIds,
      selectedCount: selectedIds.size,
      isSelected: (id) => selectedIds.has(id),
      toggle: (id) => {
        setSelectedIds((prev) => {
          const next = new Set(prev)
          if (next.has(id)) next.delete(id)
          else next.add(id)
          return next
        })
      },
      clear: () => setSelectedIds(new Set()),
    }),
    [selectedIds]
  )

  return (
    <ChatSelectionContext.Provider value={value}>
      {children}
    </ChatSelectionContext.Provider>
  )
}

export function useChatSelection() {
  const context = React.useContext(ChatSelectionContext)
  if (!context) {
    throw new Error("useChatSelection must be used within ChatSelectionProvider")
  }
  return context
}

export function useChatSelectionOptional() {
  return React.useContext(ChatSelectionContext)
}
