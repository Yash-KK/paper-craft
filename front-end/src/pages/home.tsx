import { BookOpenText } from "lucide-react"
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
      <div className="hidden items-center justify-center bg-muted/50 p-12 lg:flex xl:p-16">
        <LandingIntro className="w-full max-w-2xl" />
      </div>

      <div className="flex flex-col items-center justify-center gap-8 p-4 sm:p-8">
        <div className="flex items-center gap-2.5 lg:hidden">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-violet-600 text-white shadow-sm">
            <BookOpenText className="size-5" aria-hidden />
          </span>
          <p className="font-chicle text-2xl tracking-wide text-violet-600 dark:text-violet-400">
            PaperCraft
          </p>
        </div>

        {status === AuthStatus.Loading ? (
          <Skeleton className="h-52 w-full max-w-sm rounded-xl" />
        ) : (
          <LoginCard authError={authError} />
        )}
      </div>
    </div>
  )
}
