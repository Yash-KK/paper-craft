import * as React from "react"
import { ArrowLeft, CheckCircle2, Loader2 } from "lucide-react"
import { Link, useNavigate } from "react-router-dom"

import { AuthStatus, useAuth } from "@/providers/auth-provider"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Skeleton } from "@/components/ui/skeleton"
import {
  UnauthorizedError,
  updateCurrentUser,
  type ProfileUpdatePayload,
  type UserProfile,
} from "@/lib/api"
import type { Board } from "@/lib/types/notebook"
import { BOARDS } from "@/lib/types/notebook"

type FormState = {
  board: Board | ""
  school_name: string
  phone_number: string
}

type FormErrors = Partial<Record<keyof FormState, string>>

const EMPTY_FORM: FormState = {
  board: "",
  school_name: "",
  phone_number: "",
}

function initials(name: string): string {
  return name
    .split(" ")
    .map((part) => part[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase()
}

function validate(values: FormState): FormErrors {
  const errors: FormErrors = {}

  if (values.school_name.trim().length > 255) {
    errors.school_name = "School name must be 255 characters or fewer."
  }

  const phone = values.phone_number.trim()
  if (phone) {
    if (phone.length > 20) {
      errors.phone_number = "Phone number must be 20 characters or fewer."
    } else if (!/^[+]?[\d\s().-]{6,}$/.test(phone)) {
      errors.phone_number = "Enter a valid phone number."
    }
  }

  return errors
}

function toPayload(values: FormState): ProfileUpdatePayload {
  const trim = (value: string) => {
    const next = value.trim()
    return next.length > 0 ? next : null
  }
  return {
    board: values.board || null,
    school_name: trim(values.school_name),
    phone_number: trim(values.phone_number),
  }
}

function toFormState(user: UserProfile): FormState {
  return {
    board: user.board ?? "",
    school_name: user.school_name ?? "",
    phone_number: user.phone_number ?? "",
  }
}

export function ProfileUpdatePage() {
  const { status, user, setUser } = useAuth()
  const navigate = useNavigate()

  const [form, setForm] = React.useState<FormState>(EMPTY_FORM)
  const [initial, setInitial] = React.useState<FormState>(EMPTY_FORM)
  const [syncedUserId, setSyncedUserId] = React.useState<string | null>(null)
  const [errors, setErrors] = React.useState<FormErrors>({})
  const [submitting, setSubmitting] = React.useState(false)
  const [submitError, setSubmitError] = React.useState<string | null>(null)
  const [success, setSuccess] = React.useState(false)

  React.useEffect(() => {
    if (status === AuthStatus.Unauthenticated) {
      navigate("/", { replace: true })
    }
  }, [status, navigate])

  if (user && user.user_id !== syncedUserId) {
    const next = toFormState(user)
    setForm(next)
    setInitial(next)
    setSyncedUserId(user.user_id)
  }

  const isDirty = React.useMemo(
    () =>
      (Object.keys(form) as (keyof FormState)[]).some(
        (key) => form[key] !== initial[key]
      ),
    [form, initial]
  )

  function handleChange(field: keyof FormState) {
    return (event: React.ChangeEvent<HTMLInputElement>) => {
      const value = event.target.value
      setForm((prev) => ({ ...prev, [field]: value }))
      setErrors((prev) => ({ ...prev, [field]: undefined }))
      setSubmitError(null)
      setSuccess(false)
    }
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const nextErrors = validate(form)
    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors)
      return
    }

    setSubmitting(true)
    setSubmitError(null)
    setSuccess(false)

    try {
      const updated = await updateCurrentUser(toPayload(form))
      setUser(updated)
      const next = toFormState(updated)
      setForm(next)
      setInitial(next)
      setSuccess(true)
    } catch (error) {
      if (error instanceof UnauthorizedError) {
        navigate("/", { replace: true })
        return
      }
      setSubmitError(
        error instanceof Error
          ? error.message
          : "Something went wrong. Please try again."
      )
    } finally {
      setSubmitting(false)
    }
  }

  const isLoading = status === AuthStatus.Loading || !user

  return (
    <div className="mx-auto w-full max-w-lg px-4 py-8 sm:py-10">
      <Button
        variant="ghost"
        size="sm"
        className="mb-4 -ml-2 text-muted-foreground"
        render={<Link to="/" />}
      >
        <ArrowLeft />
        Back
      </Button>

      {isLoading ? (
        <ProfileFormSkeleton />
      ) : (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Edit profile</CardTitle>
            <CardDescription>
              Update your personal details. Changes are saved to your account.
            </CardDescription>
          </CardHeader>

          <form onSubmit={handleSubmit} noValidate>
            <CardContent className="flex flex-col gap-5 p-2">
              <div className="flex items-center gap-4">
                <Avatar className="size-16">
                  {user.avatar_url && (
                    <AvatarImage src={user.avatar_url} alt={user.full_name} />
                  )}
                  <AvatarFallback className="text-base">
                    {initials(user.full_name)}
                  </AvatarFallback>
                </Avatar>
                <div className="min-w-0">
                  <p className="truncate font-medium">{user.full_name}</p>
                  <p className="truncate text-sm text-muted-foreground">
                    {user.email}
                  </p>
                </div>
              </div>

              {/* Read-only account fields (not editable via this endpoint). */}
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="flex flex-col gap-2">
                  <Label htmlFor="full_name">Full name</Label>
                  <Input id="full_name" value={user.full_name} disabled />
                </div>
                <div className="flex flex-col gap-2">
                  <Label htmlFor="role">Role</Label>
                  <Input
                    id="role"
                    value={user.role}
                    disabled
                    className="capitalize"
                  />
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <Label htmlFor="board">Board</Label>
                <select
                  id="board"
                  className="flex h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                  value={form.board}
                  onChange={(event) => {
                    const value = event.target.value as Board | ""
                    setForm((prev) => ({ ...prev, board: value }))
                    setErrors((prev) => ({ ...prev, board: undefined }))
                    setSubmitError(null)
                    setSuccess(false)
                  }}
                >
                  <option value="">Select board</option>
                  {BOARDS.map((board) => (
                    <option key={board} value={board}>
                      {board}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex flex-col gap-2">
                <Label htmlFor="school_name">School name</Label>
                <Input
                  id="school_name"
                  value={form.school_name}
                  onChange={handleChange("school_name")}
                  placeholder="e.g. Springfield High School"
                  maxLength={255}
                  aria-invalid={!!errors.school_name}
                  aria-describedby={
                    errors.school_name ? "school_name-error" : undefined
                  }
                />
                {errors.school_name && (
                  <p
                    id="school_name-error"
                    className="text-sm text-destructive"
                  >
                    {errors.school_name}
                  </p>
                )}
              </div>

              <div className="flex flex-col gap-2">
                <Label htmlFor="phone_number">Phone number</Label>
                <Input
                  id="phone_number"
                  type="tel"
                  inputMode="tel"
                  value={form.phone_number}
                  onChange={handleChange("phone_number")}
                  placeholder="e.g. +1 555 123 4567"
                  maxLength={20}
                  aria-invalid={!!errors.phone_number}
                  aria-describedby={
                    errors.phone_number ? "phone_number-error" : undefined
                  }
                />
                {errors.phone_number && (
                  <p
                    id="phone_number-error"
                    className="text-sm text-destructive"
                  >
                    {errors.phone_number}
                  </p>
                )}
              </div>

              {submitError && (
                <p
                  role="alert"
                  className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive"
                >
                  {submitError}
                </p>
              )}

              {success && (
                <p
                  role="status"
                  className="flex items-center gap-2 rounded-md bg-emerald-500/10 px-3 py-2 text-sm text-emerald-600 dark:text-emerald-400"
                >
                  <CheckCircle2 className="size-4 shrink-0" />
                  Profile updated successfully.
                </p>
              )}
            </CardContent>

            <CardFooter className="justify-end gap-2">
              <Button variant="outline" render={<Link to="/" />}>
                Cancel
              </Button>
              <Button type="submit" disabled={submitting || !isDirty}>
                {submitting && <Loader2 className="animate-spin" />}
                {submitting ? "Saving…" : "Save changes"}
              </Button>
            </CardFooter>
          </form>
        </Card>
      )}
    </div>
  )
}

function ProfileFormSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-5 w-32" />
        <Skeleton className="h-4 w-64" />
      </CardHeader>
      <CardContent className="flex flex-col gap-5">
        <div className="flex items-center gap-4">
          <Skeleton className="size-16 rounded-full" />
          <div className="flex flex-col gap-2">
            <Skeleton className="h-4 w-36" />
            <Skeleton className="h-3 w-48" />
          </div>
        </div>
        {Array.from({ length: 3 }).map((_, index) => (
          <div key={index} className="flex flex-col gap-2">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-8 w-full" />
          </div>
        ))}
      </CardContent>
      <CardFooter className="justify-end gap-2">
        <Skeleton className="h-8 w-20" />
        <Skeleton className="h-8 w-28" />
      </CardFooter>
    </Card>
  )
}
