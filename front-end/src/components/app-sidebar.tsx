import { useState } from "react"
import {
  ArrowLeft,
  LogOut,
  NotebookText,
  PanelLeftClose,
  UserPen,
} from "lucide-react"
import { Link, matchPath, useLocation } from "react-router-dom"

import { useAuth } from "@/providers/auth-provider"
import { ConfirmDialog } from "@/components/confirm-dialog"
import { ModeToggle } from "@/components/mode-toggle"
import { NotebookStats } from "@/components/notebooks/notebook-stats"
import { QuestionPapersSidebar } from "@/components/notebooks/question-papers-sidebar"
import { useSidebar } from "@/providers/sidebar-provider"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { useNotebooks } from "@/hooks/use-notebooks"
import type { UserProfile } from "@/lib/api"

function initials(name: string): string {
  return name
    .split(" ")
    .map((part) => part[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase()
}

type AppSidebarProps = {
  user: UserProfile
}

export function AppSidebar({ user }: AppSidebarProps) {
  const { logout } = useAuth()
  const sidebar = useSidebar()
  const location = useLocation()
  const { notebooks } = useNotebooks(true)
  const [logoutConfirmOpen, setLogoutConfirmOpen] = useState(false)

  const notebookMatch =
    matchPath("/notebooks/:notebookId/generate", location.pathname) ??
    matchPath("/notebooks/:notebookId", location.pathname)
  const activeNotebook = notebookMatch
    ? notebooks.find((n) => n.id === notebookMatch.params.notebookId)
    : undefined

  return (
    <div className="flex h-full flex-col overflow-hidden bg-muted/20">
      <div className="flex h-16 shrink-0 items-center justify-between gap-2 border-b px-4">
        <Link
          to="/dashboard"
          className="flex min-w-0 items-center gap-2 font-heading text-lg font-semibold"
        >
          <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-violet-600 text-white shadow-sm">
            <NotebookText className="size-5" />
          </span>
          <span className="truncate">PaperCraft</span>
        </Link>
        <Button
          type="button"
          variant="ghost"
          size="icon-sm"
          className="shrink-0 text-muted-foreground"
          aria-label="Close sidebar"
          onClick={() => sidebar?.setSidebarOpen(false)}
        >
          <PanelLeftClose className="size-4" />
        </Button>
      </div>

      <div className="min-h-0 flex-1">
        {notebookMatch && activeNotebook ? (
          <div className="flex h-full min-h-0 flex-col">
            <div className="shrink-0 px-3 py-3">
              <Button
                variant="ghost"
                size="sm"
                className="w-full justify-start gap-2 text-muted-foreground"
                render={<Link to="/dashboard" />}
              >
                <ArrowLeft className="size-4" />
                Back to notebooks
              </Button>
            </div>
            <Separator />
            <QuestionPapersSidebar
              notebook={activeNotebook}
              className="min-h-0 flex-1"
            />
          </div>
        ) : notebookMatch ? (
          <div className="space-y-4 p-4">
            <p className="text-sm text-muted-foreground">Loading notebook…</p>
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

      <div className="shrink-0 border-t p-3">
        <div className="flex items-center gap-3 rounded-xl px-2 py-2">
          <Avatar className="size-9">
            {user.avatar_url && (
              <AvatarImage src={user.avatar_url} alt={user.full_name} />
            )}
            <AvatarFallback>{initials(user.full_name)}</AvatarFallback>
          </Avatar>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">{user.full_name}</p>
            <p className="truncate text-xs text-muted-foreground">{user.email}</p>
          </div>
          <ModeToggle />
        </div>
        <div className="mt-1 grid grid-cols-2 gap-1">
          <Button
            variant="ghost"
            size="sm"
            className="justify-start gap-2"
            render={<Link to="/profile-update" />}
          >
            <UserPen className="size-4" />
            Profile
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="justify-start gap-2 text-destructive hover:bg-destructive/10 hover:text-destructive"
            onClick={() => setLogoutConfirmOpen(true)}
          >
            <LogOut className="size-4" />
            Log out
          </Button>
        </div>
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
  )
}
