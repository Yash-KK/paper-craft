export const API_URL = import.meta.env.VITE_API_URL

import type {
  Board,
  ChapterCatalogItem,
  ClassGrade,
  NotebookCreatePayload,
  NotebookListItem,
  NotebookUpdatePayload,
  Subject,
} from "@/lib/types/notebook"
import type {
  GenerateNewVersionPayload,
  GeneratePaperPayload,
  GenerationResult,
  QuestionPaperSummary,
  QuestionPaperVersionDetail,
  QuestionPaperVersionSummary,
  SampleBlueprintDetail,
  SampleBlueprintSummary,
} from "@/lib/types/generation"
import type { ChatMessagesPage, ChatSession } from "@/features/chat/types/chat"

export type {
  Board,
  ChapterCatalogItem,
  ClassGrade,
  NotebookCreatePayload,
  NotebookListItem,
  NotebookUpdatePayload,
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
  board: Board | null
  school_name: string | null
  phone_number: string | null
  avatar_url: string | null
  settings: Record<string, unknown>
  question_paper_limit: number
  question_paper_usage: number
  version_limit: number
  chat_message_limit: number
  chat_message_usage: number
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
  board?: Board | null
  school_name: string | null
  phone_number: string | null
}

export class UnauthorizedError extends Error {
  constructor(message = "Your session has expired. Please sign in again.") {
    super(message)
    this.name = "UnauthorizedError"
  }
}

async function parseApiError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as {
      detail?: string | { msg: string }[]
    }
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
  const isFormData =
    typeof FormData !== "undefined" && init.body instanceof FormData
  if (init.body && !isFormData && !headers.has("Content-Type")) {
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

export async function updateNotebook(
  notebookId: string,
  payload: NotebookUpdatePayload
): Promise<NotebookListItem> {
  const response = await authFetch(`/api/v1/notebooks/${notebookId}`, {
    method: "PATCH",
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

export async function fetchNotebookChat(
  notebookId: string
): Promise<ChatSession> {
  const response = await authFetch(`/api/v1/notebooks/${notebookId}/chat`)
  if (!response.ok) throw new Error(await parseApiError(response))
  return (await response.json()) as ChatSession
}

export async function fetchNotebookChatMessages(
  notebookId: string,
  options?: { cursor?: string | null; size?: number }
): Promise<ChatMessagesPage> {
  const params = new URLSearchParams()
  if (options?.cursor) params.set("cursor", options.cursor)
  if (options?.size != null) params.set("size", String(options.size))
  const query = params.toString()
  const response = await authFetch(
    `/api/v1/notebooks/${notebookId}/chat/messages${query ? `?${query}` : ""}`
  )
  if (!response.ok) throw new Error(await parseApiError(response))
  return (await response.json()) as ChatMessagesPage
}

export async function fetchBoards(): Promise<Board[]> {
  const response = await authFetch("/api/v1/chapters/boards")
  if (!response.ok) throw new Error(await parseApiError(response))
  return (await response.json()) as Board[]
}

export async function fetchGrades(board: Board): Promise<ClassGrade[]> {
  const response = await authFetch(
    `/api/v1/chapters/grades?board=${encodeURIComponent(board)}`
  )
  if (!response.ok) throw new Error(await parseApiError(response))
  return (await response.json()) as ClassGrade[]
}

export async function fetchSubjects(
  board: Board,
  grade: ClassGrade
): Promise<Subject[]> {
  const params = new URLSearchParams({ board, grade })
  const response = await authFetch(`/api/v1/chapters/subjects?${params}`)
  if (!response.ok) throw new Error(await parseApiError(response))
  return (await response.json()) as Subject[]
}

export async function fetchChapters(
  board: Board,
  grade: ClassGrade,
  subject: Subject
): Promise<ChapterCatalogItem[]> {
  const params = new URLSearchParams({ board, grade, subject })
  const response = await authFetch(`/api/v1/chapters?${params}`)
  if (!response.ok) throw new Error(await parseApiError(response))
  return (await response.json()) as ChapterCatalogItem[]
}

export async function fetchSampleBlueprints(filters?: {
  board?: Board | null
  subject?: Subject | null
}): Promise<SampleBlueprintSummary[]> {
  const params = new URLSearchParams()
  if (filters?.board) params.set("board", filters.board)
  if (filters?.subject) params.set("subject", filters.subject)
  const query = params.toString()
  const response = await authFetch(
    `/api/v1/sample-blueprints${query ? `?${query}` : ""}`
  )
  if (!response.ok) throw new Error(await parseApiError(response))
  return (await response.json()) as SampleBlueprintSummary[]
}

export async function fetchSampleBlueprint(
  id: string
): Promise<SampleBlueprintDetail> {
  const response = await authFetch(`/api/v1/sample-blueprints/${id}`)
  if (!response.ok) throw new Error(await parseApiError(response))
  return (await response.json()) as SampleBlueprintDetail
}

export async function generateQuestionPaper(
  payload: GeneratePaperPayload
): Promise<GenerationResult> {
  const response = await authFetch("/api/v1/generation/papers", {
    method: "POST",
    body: JSON.stringify(payload),
  })
  if (!response.ok) throw new Error(await parseApiError(response))
  return (await response.json()) as GenerationResult
}

export async function fetchNotebookPapers(
  notebookId: string
): Promise<QuestionPaperSummary[]> {
  const response = await authFetch(
    `/api/v1/generation/notebooks/${notebookId}/papers`
  )
  if (!response.ok) throw new Error(await parseApiError(response))
  return (await response.json()) as QuestionPaperSummary[]
}

export async function deleteQuestionPaper(paperId: string): Promise<void> {
  const response = await authFetch(`/api/v1/generation/papers/${paperId}`, {
    method: "DELETE",
  })
  if (!response.ok) throw new Error(await parseApiError(response))
}

export async function createPaperVersion(
  paperId: string,
  payload: GenerateNewVersionPayload
): Promise<GenerationResult> {
  const response = await authFetch(
    `/api/v1/generation/papers/${paperId}/versions`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  )
  if (!response.ok) throw new Error(await parseApiError(response))
  return (await response.json()) as GenerationResult
}

export async function cancelPaperVersion(
  paperId: string,
  versionNumber: number
): Promise<QuestionPaperVersionSummary> {
  const response = await authFetch(
    `/api/v1/generation/papers/${paperId}/versions/${versionNumber}/cancel`,
    { method: "POST" }
  )
  if (!response.ok) throw new Error(await parseApiError(response))
  return (await response.json()) as QuestionPaperVersionSummary
}

export async function fetchPaperVersion(
  paperId: string,
  versionNumber: number
): Promise<QuestionPaperVersionDetail> {
  const response = await authFetch(
    `/api/v1/generation/papers/${paperId}/versions/${versionNumber}`
  )
  if (!response.ok) throw new Error(await parseApiError(response))
  return (await response.json()) as QuestionPaperVersionDetail
}

function filenameFromContentDisposition(
  header: string | null,
  fallback: string
): string {
  if (!header) return fallback
  const utfMatch = /filename\*=UTF-8''([^;]+)/i.exec(header)
  if (utfMatch?.[1]) {
    try {
      return decodeURIComponent(utfMatch[1].trim())
    } catch {
      return utfMatch[1].trim()
    }
  }
  const plainMatch = /filename="?([^";]+)"?/i.exec(header)
  return plainMatch?.[1]?.trim() || fallback
}

export async function fetchVersionExport(
  paperId: string,
  versionNumber: number
): Promise<{ blob: Blob; filename: string }> {
  const response = await authFetch(
    `/api/v1/generation/papers/${paperId}/versions/${versionNumber}/export`
  )
  if (!response.ok) throw new Error(await parseApiError(response))

  const blob = await response.blob()
  const filename = filenameFromContentDisposition(
    response.headers.get("Content-Disposition"),
    `question_paper_v${versionNumber}.docx`
  )
  return { blob, filename }
}

export async function downloadVersionExport(
  paperId: string,
  versionNumber: number
): Promise<void> {
  const { blob, filename } = await fetchVersionExport(paperId, versionNumber)
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement("a")
  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  URL.revokeObjectURL(url)
}
