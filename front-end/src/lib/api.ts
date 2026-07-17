export const API_URL = import.meta.env.VITE_API_URL

import type {
  ChapterCatalogItem,
  ClassGrade,
  NotebookCreatePayload,
  NotebookListItem,
  Subject,
} from "@/lib/types/notebook"

export type {
  ChapterCatalogItem,
  ClassGrade,
  NotebookCreatePayload,
  NotebookListItem,
  Subject,
} from "@/lib/types/notebook"

const TOKEN_KEY = "papercraft_token"

export function getToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  sessionStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  sessionStorage.removeItem(TOKEN_KEY)
}

export function loginWithGoogle(): void {
  window.location.href = `${API_URL}/auth/login`
}

export type UserProfile = {
  id: string | null
  user_id: string
  email: string
  full_name: string
  role: string
  school_name: string | null
  phone_number: string | null
  avatar_url: string | null
  settings: Record<string, unknown>
}

export async function fetchCurrentUser(): Promise<UserProfile | null> {
  const token = getToken()
  if (!token) {
    return null
  }

  const response = await fetch(`${API_URL}/api/v1/users/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })

  if (response.status === 401) {
    clearToken()
    return null
  }

  if (!response.ok) {
    throw new Error(`Failed to fetch user (${response.status})`)
  }

  return (await response.json()) as UserProfile
}

export type ProfileUpdatePayload = {
  school_name: string | null
  phone_number: string | null
  avatar_url: string | null
}

export class UnauthorizedError extends Error {
  constructor(message = "Your session has expired. Please sign in again.") {
    super(message)
    this.name = "UnauthorizedError"
  }
}

async function parseApiError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: string | { msg: string }[] }
    if (typeof data.detail === "string") return data.detail
    if (Array.isArray(data.detail) && data.detail[0]?.msg) {
      return data.detail[0].msg
    }
  } catch {
    // ignore parse errors
  }
  return `Request failed (${response.status})`
}

export async function authFetch(
  path: string,
  init: RequestInit = {}
): Promise<Response> {
  const token = getToken()
  if (!token) throw new UnauthorizedError()

  const headers = new Headers(init.headers)
  headers.set("Authorization", `Bearer ${token}`)
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json")
  }

  const response = await fetch(`${API_URL}${path}`, { ...init, headers })

  if (response.status === 401) {
    clearToken()
    throw new UnauthorizedError()
  }

  return response
}

export async function updateCurrentUser(
  updates: ProfileUpdatePayload
): Promise<UserProfile> {
  const token = getToken()
  if (!token) {
    throw new UnauthorizedError()
  }

  const response = await fetch(`${API_URL}/api/v1/users/me`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(updates),
  })

  if (response.status === 401) {
    clearToken()
    throw new UnauthorizedError()
  }

  if (!response.ok) {
    throw new Error(`Failed to update profile (${response.status})`)
  }

  return (await response.json()) as UserProfile
}

export async function fetchNotebooks(): Promise<NotebookListItem[]> {
  const response = await authFetch("/api/v1/notebooks")
  if (!response.ok) throw new Error(await parseApiError(response))
  return (await response.json()) as NotebookListItem[]
}

export async function createNotebook(
  payload: NotebookCreatePayload
): Promise<NotebookListItem> {
  const response = await authFetch("/api/v1/notebooks", {
    method: "POST",
    body: JSON.stringify(payload),
  })
  if (!response.ok) throw new Error(await parseApiError(response))
  return (await response.json()) as NotebookListItem
}

export async function deleteNotebook(notebookId: string): Promise<void> {
  const response = await authFetch(`/api/v1/notebooks/${notebookId}`, {
    method: "DELETE",
  })
  if (!response.ok) throw new Error(await parseApiError(response))
}

export async function fetchGrades(): Promise<ClassGrade[]> {
  const response = await authFetch("/api/v1/chapters/grades")
  if (!response.ok) throw new Error(await parseApiError(response))
  return (await response.json()) as ClassGrade[]
}

export async function fetchSubjects(grade: ClassGrade): Promise<Subject[]> {
  const response = await authFetch(
    `/api/v1/chapters/subjects?grade=${encodeURIComponent(grade)}`
  )
  if (!response.ok) throw new Error(await parseApiError(response))
  return (await response.json()) as Subject[]
}

export async function fetchChapters(
  grade: ClassGrade,
  subject: Subject
): Promise<ChapterCatalogItem[]> {
  const params = new URLSearchParams({ grade, subject })
  const response = await authFetch(`/api/v1/chapters?${params}`)
  if (!response.ok) throw new Error(await parseApiError(response))
  return (await response.json()) as ChapterCatalogItem[]
}
