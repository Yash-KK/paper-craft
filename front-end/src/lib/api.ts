export const API_URL = import.meta.env.VITE_API_URL

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
