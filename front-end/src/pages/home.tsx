import { Navigate } from "react-router-dom"

import { AuthStatus, useAuth } from "@/components/auth-provider"
import { LoginCard } from "@/components/login-card"

export function HomePage() {
  const { status, user, authError } = useAuth()

  if (status === AuthStatus.Authenticated && user) {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <div className="flex flex-1 items-center justify-center p-4 sm:p-6">
      {status === AuthStatus.Loading && (
        <p className="text-sm text-muted-foreground">Loading…</p>
      )}

      {status === AuthStatus.Unauthenticated && (
        <LoginCard authError={authError} />
      )}
    </div>
  )
}
