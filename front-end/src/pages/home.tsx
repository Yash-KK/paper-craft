import { Navigate } from "react-router-dom"

import { AuthStatus, useAuth } from "@/components/auth-provider"
import { LandingIntro } from "@/components/landing-intro"
import { LoginCard } from "@/components/login-card"
import { Skeleton } from "@/components/ui/skeleton"

export function HomePage() {
  const { status, user, authError } = useAuth()

  if (status === AuthStatus.Authenticated && user) {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <div className="grid flex-1 grid-cols-1 lg:grid-cols-2">
      <div className="hidden items-center justify-center bg-muted/20 p-12 lg:flex xl:p-16">
        <LandingIntro className="w-full max-w-xl" />
      </div>

      <div className="flex items-center justify-center p-4 sm:p-8">
        {status === AuthStatus.Loading ? (
          <Skeleton className="h-52 w-full max-w-sm rounded-xl" />
        ) : (
          <LoginCard authError={authError} />
        )}
      </div>
    </div>
  )
}
