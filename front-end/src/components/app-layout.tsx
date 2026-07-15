import { LogOut, UserPen } from "lucide-react"
import { Link, Outlet } from "react-router-dom"

import { AuthStatus, useAuth } from "@/components/auth-provider"
import { ModeToggle } from "@/components/mode-toggle"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

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

  return (
    <div className="flex min-h-svh flex-col">
      <header className="flex items-center justify-between gap-2 border-b px-4 py-3 sm:px-6">
        <Link
          to="/"
          className="font-heading text-base font-semibold sm:text-lg"
        >
          PaperCraft
        </Link>
        <div className="flex items-center gap-2">
          {status === AuthStatus.Authenticated && user && (
            <>
              <Button
                variant="ghost"
                size="icon"
                aria-label="Edit profile"
                render={<Link to="/profile-update" />}
              >
                <UserPen />
              </Button>
              <DropdownMenu>
                <DropdownMenuTrigger
                  render={
                    <Button
                      variant="ghost"
                      size="icon"
                      className="rounded-full"
                      aria-label="Account menu"
                    />
                  }
                >
                  <Avatar>
                    {user.avatar_url && (
                      <AvatarImage src={user.avatar_url} alt={user.full_name} />
                    )}
                    <AvatarFallback>{initials(user.full_name)}</AvatarFallback>
                  </Avatar>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="min-w-48">
                  <DropdownMenuLabel className="flex flex-col gap-0.5">
                    <span className="truncate text-sm font-medium text-foreground">
                      {user.full_name}
                    </span>
                    <span className="truncate font-normal">{user.email}</span>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem render={<Link to="/profile-update" />}>
                    <UserPen />
                    Edit profile
                  </DropdownMenuItem>
                  <DropdownMenuItem variant="destructive" onClick={logout}>
                    <LogOut />
                    Log out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </>
          )}
          <ModeToggle />
        </div>
      </header>

      <main className="flex flex-1 flex-col">
        <Outlet />
      </main>
    </div>
  )
}
