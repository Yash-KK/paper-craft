/* eslint-disable react-refresh/only-export-components */
import * as React from "react"

type SidebarContextValue = {
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
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
    () => ({ sidebarOpen: open, setSidebarOpen: onOpenChange }),
    [open, onOpenChange]
  )
  return (
    <SidebarContext.Provider value={value}>{children}</SidebarContext.Provider>
  )
}

export function useSidebar() {
  return React.useContext(SidebarContext)
}
