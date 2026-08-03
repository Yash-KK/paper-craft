import { memo, useEffect } from "react"
import { PanelLeft } from "lucide-react"
import { matchPath, Outlet, useLocation } from "react-router-dom"

import { AppSidebar } from "@/components/layout/app-sidebar"
import { Button } from "@/components/ui/button"
import { AuthStatus, useAuth } from "@/providers/auth-provider"
import {
  ChatSelectionProvider,
  useChatSelectionOptional,
} from "@/providers/chat-selection-provider"
import {
  useSidebarActions,
  useSidebarOpen,
} from "@/components/layout/sidebar-store"

export function AppLayout() {
  return (
    <ChatSelectionProvider>
      <div className="flex h-svh overflow-hidden">
        <SidebarSlot />
        <PageColumn />
      </div>
    </ChatSelectionProvider>
  )
}

function SidebarSlot() {
  const { status, user } = useAuth()
  const sidebarOpen = useSidebarOpen()
  if (status !== AuthStatus.Authenticated || !user || !sidebarOpen) return null

  return (
    <aside className="w-72 shrink-0 border-r md:w-80">
      <AppSidebar user={user} />
    </aside>
  )
}

/** Stable route host — does not subscribe to sidebar open state. */
const PageColumn = memo(function PageColumn() {
  useClearSelectionOnNotebookChange()

  return (
    <div className="flex min-w-0 flex-1 flex-col">
      <SidebarOpenBar />
      <main className="flex min-h-0 flex-1 flex-col overflow-y-auto">
        <Outlet />
      </main>
    </div>
  )
})

function SidebarOpenBar() {
  const { status } = useAuth()
  const sidebarOpen = useSidebarOpen()
  const { openSidebar } = useSidebarActions()
  const { pathname } = useLocation()
  const onNotebook =
    Boolean(matchPath("/notebooks/:notebookId/generate", pathname)) ||
    Boolean(matchPath("/notebooks/:notebookId", pathname))

  if (status !== AuthStatus.Authenticated || sidebarOpen || onNotebook) {
    return null
  }

  return (
    <div className="flex h-12 shrink-0 items-center border-b px-3">
      <Button
        type="button"
        variant="ghost"
        size="icon-sm"
        aria-label="Open sidebar"
        onClick={openSidebar}
      >
        <PanelLeft className="size-4" />
      </Button>
    </div>
  )
}

function useClearSelectionOnNotebookChange() {
  const { pathname } = useLocation()
  const clear = useChatSelectionOptional()?.clear
  const notebookId =
    matchPath("/notebooks/:notebookId/generate", pathname)?.params.notebookId ??
    matchPath("/notebooks/:notebookId", pathname)?.params.notebookId

  useEffect(() => {
    clear?.()
  }, [notebookId, clear])
}
