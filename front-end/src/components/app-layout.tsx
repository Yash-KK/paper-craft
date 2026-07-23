import { useState } from "react"
import {
  ArrowLeft,
  BookOpenText,
  LogOut,
  PanelLeft,
  PanelLeftClose,
  UserPen,
} from "lucide-react"
import { Link, matchPath, Outlet, useLocation } from "react-router-dom"

import { AuthStatus, useAuth } from "@/components/auth-provider"
import { ConfirmDialog } from "@/components/confirm-dialog"
import { ModeToggle } from "@/components/mode-toggle"
import { NotebookStats } from "@/components/notebooks/notebook-stats"
import { QuestionPapersSidebar } from "@/components/notebooks/question-papers-sidebar"
import { SidebarProvider } from "@/components/sidebar-context"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { useNotebooks } from "@/hooks/use-notebooks"
import { cn } from "@/lib/utils"

function initials(name: string): string {
  return name
    .split(" ")
    .map((part) => part[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase()
}

export function AppLayout() {
  const { status, user, logout } = useAuth()
  const location = useLocation()
  const [logoutConfirmOpen, setLogoutConfirmOpen] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const authenticated = status === AuthStatus.Authenticated && Boolean(user)
  const { notebooks } = useNotebooks(authenticated)

  const notebookMatch = matchPath(
    "/notebooks/:notebookId",
    location.pathname
  )
  const activeNotebook = notebookMatch
    ? notebooks.find(
        (notebook) => notebook.id === notebookMatch.params.notebookId
      )
    : undefined
  const showCollapsedChrome =
    authenticated && !sidebarOpen && !notebookMatch

  return (
    <SidebarProvider open={sidebarOpen} onOpenChange={setSidebarOpen}>
      <div className="flex h-svh overflow-hidden">
        {authenticated && user ? (
          <aside
            className={cn(
              "flex h-full shrink-0 flex-col overflow-hidden border-r bg-muted/20 transition-[width,opacity] duration-200 ease-out",
              sidebarOpen
                ? "w-72 opacity-100 xl:w-80"
                : "pointer-events-none w-0 border-r-0 opacity-0"
            )}
            aria-hidden={!sidebarOpen}
          >
            <div className="flex h-16 w-72 shrink-0 items-center justify-between gap-2 border-b px-4 xl:w-80">
              <Link
                to="/dashboard"
                className="flex min-w-0 items-center gap-2 font-heading text-lg font-semibold"
                tabIndex={sidebarOpen ? undefined : -1}
              >
                <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-violet-600 text-white shadow-sm">
                  <BookOpenText className="size-5" />
                </span>
                <span className="truncate">PaperCraft</span>
              </Link>
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                className="shrink-0 text-muted-foreground"
                aria-label="Close sidebar"
                tabIndex={sidebarOpen ? undefined : -1}
                onClick={() => setSidebarOpen(false)}
              >
                <PanelLeftClose className="size-4" />
              </Button>
            </div>

            <div className="min-h-0 w-72 flex-1 xl:w-80">
              {notebookMatch ? (
                <div className="flex h-full min-h-0 flex-col">
                  <div className="shrink-0 px-3 py-3">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="w-full justify-start gap-2 text-muted-foreground"
                      render={<Link to="/dashboard" />}
                      tabIndex={sidebarOpen ? undefined : -1}
                    >
                      <ArrowLeft className="size-4" />
                      Back to notebooks
                    </Button>
                  </div>
                  <Separator />
                  <QuestionPapersSidebar
                    notebookName={activeNotebook?.name ?? "Notebook"}
                    className="min-h-0 flex-1"
                  />
                </div>
              ) : (
                <div className="space-y-4 p-4">
                  <div>
                    <p className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
                      Workspace
                    </p>
                    <h2 className="mt-1 font-heading text-sm font-semibold">
                      Notebook overview
                    </h2>
                  </div>
                  <NotebookStats notebooks={notebooks} compact />
                </div>
              )}
            </div>

            <div className="w-72 shrink-0 border-t p-3 xl:w-80">
              <div className="flex items-center gap-3 rounded-xl px-2 py-2">
                <Avatar className="size-9">
                  {user.avatar_url && (
                    <AvatarImage src={user.avatar_url} alt={user.full_name} />
                  )}
                  <AvatarFallback>{initials(user.full_name)}</AvatarFallback>
                </Avatar>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium">
                    {user.full_name}
                  </p>
                  <p className="truncate text-xs text-muted-foreground">
                    {user.email}
                  </p>
                </div>
                <ModeToggle />
              </div>
              <div className="mt-1 grid grid-cols-2 gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  className="justify-start gap-2"
                  render={<Link to="/profile-update" />}
                  tabIndex={sidebarOpen ? undefined : -1}
                >
                  <UserPen className="size-4" />
                  Profile
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="justify-start gap-2 text-destructive hover:bg-destructive/10 hover:text-destructive"
                  tabIndex={sidebarOpen ? undefined : -1}
                  onClick={() => setLogoutConfirmOpen(true)}
                >
                  <LogOut className="size-4" />
                  Log out
                </Button>
              </div>
            </div>
          </aside>
        ) : null}

        <div className="flex min-w-0 flex-1 flex-col">
          {!authenticated && (
            <header className="flex shrink-0 items-center justify-between gap-2 border-b px-4 py-3 sm:px-6">
              <Link
                to="/"
                className="font-heading text-base font-semibold sm:text-lg"
              >
                PaperCraft
              </Link>
              <ModeToggle />
            </header>
          )}

          {showCollapsedChrome && (
            <div className="flex h-12 shrink-0 items-center border-b px-3">
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                aria-label="Open sidebar"
                onClick={() => setSidebarOpen(true)}
              >
                <PanelLeft className="size-4" />
              </Button>
            </div>
          )}

          <main className="flex min-h-0 flex-1 flex-col overflow-y-auto">
            <Outlet />
          </main>
        </div>

        <ConfirmDialog
          open={logoutConfirmOpen}
          onOpenChange={setLogoutConfirmOpen}
          title="Log out?"
          description="You'll be signed out and need to log in again to continue."
          confirmLabel="Log out"
          cancelLabel="Cancel"
          confirmVariant="destructive"
          onConfirm={logout}
        />
      </div>
    </SidebarProvider>
  )
}
