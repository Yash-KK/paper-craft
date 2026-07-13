import { useEffect, useState } from "react"

import { LoginCard } from "@/components/login-card"
import { ModeToggle } from "@/components/mode-toggle"
import { Button } from "@/components/ui/button"
import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from "@/components/ui/avatar"
import {
  clearToken,
  fetchCurrentUser,
  setToken,
  type UserProfile,
} from "@/lib/api"

type Status = "loading" | "authenticated" | "unauthenticated"

function initials(name: string): string {
  return name
    .split(" ")
    .map((part) => part[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase()
}

export function App() {
  const [status, setStatus] = useState<Status>("loading")
  const [user, setUser] = useState<UserProfile | null>(null)
  const [authError] = useState(
    () => new URLSearchParams(window.location.search).get("auth_error") === "true"
  )

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const token = params.get("token")

    if (token) {
      setToken(token)
    }

    // Strip auth params from the URL so tokens don't linger in history.
    if (token || params.has("auth_error")) {
      window.history.replaceState({}, "", window.location.pathname)
    }

    let active = true
    fetchCurrentUser()
      .then((profile) => {
        if (!active) return
        if (profile) {
          setUser(profile)
          setStatus("authenticated")
        } else {
          setStatus("unauthenticated")
        }
      })
      .catch(() => {
        if (!active) return
        setStatus("unauthenticated")
      })

    return () => {
      active = false
    }
  }, [])

  function handleLogout() {
    clearToken()
    setUser(null)
    setStatus("unauthenticated")
  }

  return (
    <div className="flex min-h-svh flex-col">
      <header className="flex items-center justify-between gap-2 border-b px-4 py-3 sm:px-6">
        <span className="font-heading text-base font-semibold sm:text-lg">
          PaperCraft
        </span>
        <div className="flex items-center gap-2">
          {status === "authenticated" && user && (
            <>
              <Avatar>
                {user.avatar_url && (
                  <AvatarImage src={user.avatar_url} alt={user.full_name} />
                )}
                <AvatarFallback>{initials(user.full_name)}</AvatarFallback>
              </Avatar>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                Log out
              </Button>
            </>
          )}
          <ModeToggle />
        </div>
      </header>

      <main className="flex flex-1 items-center justify-center p-4 sm:p-6">
        {status === "loading" && (
          <p className="text-sm text-muted-foreground">Loading…</p>
        )}

        {status === "unauthenticated" && <LoginCard authError={authError} />}

        {status === "authenticated" && user && (
          <div className="flex flex-col items-center gap-3 text-center">
            <h1 className="font-heading text-2xl font-semibold sm:text-3xl">
              Welcome to PaperCraft
            </h1>
            <p className="text-sm text-muted-foreground sm:text-base">
              {user.full_name}
            </p>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
