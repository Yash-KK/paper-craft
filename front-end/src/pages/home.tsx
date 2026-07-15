import { AuthStatus, useAuth } from "@/components/auth-provider"
import { LoginCard } from "@/components/login-card"

export function HomePage() {
  const { status, user, authError } = useAuth()

  return (
    <div className="flex flex-1 items-center justify-center p-4 sm:p-6">
      {status === AuthStatus.Loading && (
        <p className="text-sm text-muted-foreground">Loading…</p>
      )}

      {status === AuthStatus.Unauthenticated && (
        <LoginCard authError={authError} />
      )}

      {status === AuthStatus.Authenticated && user && (
        <div className="flex flex-col items-center gap-3 text-center">
          <h1 className="font-heading text-2xl font-semibold sm:text-3xl">
            Welcome to PaperCraft
          </h1>
          <p className="text-sm text-muted-foreground sm:text-base">
            {user.full_name}
          </p>
        </div>
      )}
    </div>
  )
}
