import { useState, useEffect } from "react"
import { PanelLeft } from "lucide-react"
import { matchPath, Outlet, useLocation } from "react-router-dom"

import { AuthStatus, useAuth } from "@/components/auth-provider"
import { AppSidebar } from "@/components/app-sidebar"
import { SidebarProvider, useSidebar } from "@/components/sidebar-context"
import { Button } from "@/components/ui/button"
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"
import {
  ChatSelectionProvider,
  useChatSelectionOptional,
} from "@/features/chat/chat-selection-context"

export function AppLayout() {
  const { status, user } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const authenticated = status === AuthStatus.Authenticated && Boolean(user)

  return (
    <SidebarProvider open={sidebarOpen} onOpenChange={setSidebarOpen}>
      <ChatSelectionProvider>
        <div className="h-svh overflow-hidden">
          {authenticated && user && sidebarOpen ? (
            <ResizablePanelGroup orientation="horizontal" className="h-full">
              <ResizablePanel
                defaultSize="22"
                minSize="16"
                maxSize="40"
                className="border-r"
              >
                <AppSidebar user={user} />
              </ResizablePanel>
              <ResizableHandle withHandle />
              <ResizablePanel defaultSize="78">
                <AppMain />
              </ResizablePanel>
            </ResizablePanelGroup>
          ) : (
            <AppMain />
          )}
        </div>
      </ChatSelectionProvider>
    </SidebarProvider>
  )
}

function AppMain() {
  const { status } = useAuth()
  const sidebar = useSidebar()
  const location = useLocation()
  const selection = useChatSelectionOptional()
  const authenticated = status === AuthStatus.Authenticated
  const notebookMatch =
    matchPath("/notebooks/:notebookId/generate", location.pathname) ??
    matchPath("/notebooks/:notebookId", location.pathname)
  const notebookId = notebookMatch?.params.notebookId

  useEffect(() => {
    selection?.clear()
  }, [notebookId])

  return (
    <div className="flex h-full min-w-0 flex-1 flex-col">
      {authenticated && sidebar && !sidebar.sidebarOpen && !notebookMatch ? (
        <div className="flex h-12 shrink-0 items-center border-b px-3">
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            aria-label="Open sidebar"
            onClick={() => sidebar.setSidebarOpen(true)}
          >
            <PanelLeft className="size-4" />
          </Button>
        </div>
      ) : null}

      <main className="flex min-h-0 flex-1 flex-col overflow-y-auto">
        <Outlet />
      </main>
    </div>
  )
}
