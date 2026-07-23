/* eslint-disable react-refresh/only-export-components */
import * as React from "react"

type SidebarContextValue = {
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
  toggleSidebar: () => void
}

const SidebarContext = React.createContext<SidebarContextValue | null>(null)

export function SidebarProvider({
  children,
  open,
  onOpenChange,
}: {
  children: React.ReactNode
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const value = React.useMemo(
    () => ({
      sidebarOpen: open,
      setSidebarOpen: onOpenChange,
      toggleSidebar: () => onOpenChange(!open),
    }),
    [open, onOpenChange]
  )

  return (
    <SidebarContext.Provider value={value}>{children}</SidebarContext.Provider>
  )
}

export function useSidebar() {
  const context = React.useContext(SidebarContext)
  if (!context) {
    throw new Error("useSidebar must be used within SidebarProvider")
  }
  return context
}

export function useSidebarOptional() {
  return React.useContext(SidebarContext)
}
