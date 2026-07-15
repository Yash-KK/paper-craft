/* eslint-disable react-refresh/only-export-components */
import * as React from "react"
import { useNavigate } from "react-router-dom"

import {
  clearToken,
  fetchCurrentUser,
  setToken,
  type UserProfile,
} from "@/lib/api"

export const AuthStatus = {
  Loading: "loading",
  Authenticated: "authenticated",
  Unauthenticated: "unauthenticated",
} as const

export type AuthStatus = (typeof AuthStatus)[keyof typeof AuthStatus]

type AuthContextValue = {
  status: AuthStatus
  user: UserProfile | null
  authError: boolean
  setUser: (user: UserProfile) => void
  logout: () => void
}

const AuthContext = React.createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate()
  const [status, setStatus] = React.useState<AuthStatus>(AuthStatus.Loading)
  const [user, setUserState] = React.useState<UserProfile | null>(null)
  const [authError] = React.useState(
    () =>
      new URLSearchParams(window.location.search).get("auth_error") === "true"
  )

  React.useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const token = params.get("token")

    if (token) {
      setToken(token)
    }

    if (token || params.has("auth_error")) {
      navigate(window.location.pathname, { replace: true })
    }

    let active = true
    fetchCurrentUser()
      .then((profile) => {
        if (!active) return
        if (profile) {
          setUserState(profile)
          setStatus(AuthStatus.Authenticated)
        } else {
          setStatus(AuthStatus.Unauthenticated)
        }
      })
      .catch(() => {
        if (!active) return
        setStatus(AuthStatus.Unauthenticated)
      })

    return () => {
      active = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const setUser = React.useCallback((next: UserProfile) => {
    setUserState(next)
    setStatus(AuthStatus.Authenticated)
  }, [])

  const logout = React.useCallback(() => {
    clearToken()
    setUserState(null)
    setStatus(AuthStatus.Unauthenticated)
  }, [])

  const value = React.useMemo<AuthContextValue>(
    () => ({ status, user, authError, setUser, logout }),
    [status, user, authError, setUser, logout]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = React.useContext(AuthContext)

  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }

  return context
}
