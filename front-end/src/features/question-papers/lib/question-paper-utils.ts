import {
  isActiveGenerationStatus,
  type QuestionPaperStatus,
  type QuestionPaperSummary,
  type QuestionPaperVersionSummary,
} from "@/lib/types/generation"

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i

export function isPersistedMessageId(id: string): boolean {
  return UUID_RE.test(id)
}

export function versionHref(
  notebookId: string,
  paperId: string,
  versionNumber: number
): string {
  return `/notebooks/${notebookId}/papers/${paperId}/versions/${versionNumber}`
}

export function latestVersionNumber(
  paper: QuestionPaperSummary
): number | null {
  if (paper.latest_version) return paper.latest_version.version_number
  if (paper.versions.length === 0) return null
  return paper.versions[paper.versions.length - 1]?.version_number ?? null
}

export function paperHref(
  notebookId: string,
  paper: QuestionPaperSummary
): string | null {
  const versionNumber = latestVersionNumber(paper)
  if (versionNumber == null) return null
  return versionHref(notebookId, paper.id, versionNumber)
}

export function formatRelativeTime(iso: string): string {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return iso

  const deltaMs = date.getTime() - Date.now()
  const absSeconds = Math.round(Math.abs(deltaMs) / 1000)
  const formatter = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" })

  if (absSeconds < 60) return formatter.format(Math.round(deltaMs / 1000), "second")
  const absMinutes = Math.round(absSeconds / 60)
  if (absMinutes < 60) {
    return formatter.format(Math.round(deltaMs / (60 * 1000)), "minute")
  }
  const absHours = Math.round(absMinutes / 60)
  if (absHours < 24) {
    return formatter.format(Math.round(deltaMs / (60 * 60 * 1000)), "hour")
  }
  const absDays = Math.round(absHours / 24)
  if (absDays < 30) {
    return formatter.format(Math.round(deltaMs / (24 * 60 * 60 * 1000)), "day")
  }
  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  })
}

export function statusBadgeClass(status: QuestionPaperStatus): string {
  switch (status) {
    case "ready":
      return "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300"
    case "pending":
      return "bg-amber-500/10 text-amber-700 dark:text-amber-300"
    case "running":
      return "bg-sky-500/10 text-sky-700 dark:text-sky-300"
    case "failed":
      return "bg-destructive/10 text-destructive"
  }
}

export function canCreateNewVersion(paper: QuestionPaperSummary): boolean {
  if (paperHasActive(paper)) return false
  return paper.versions.some((version) => version.status === "ready")
}

export function paperHasActive(paper: QuestionPaperSummary): boolean {
  return paper.versions.some((version) =>
    isActiveGenerationStatus(version.status)
  )
}

export function readyBaseVersion(
  paper: QuestionPaperSummary
): QuestionPaperVersionSummary | null {
  const ready = paper.versions.filter((version) => version.status === "ready")
  if (ready.length === 0) return null
  return ready.reduce((latest, version) =>
    version.version_number > latest.version_number ? version : latest
  )
}

export const GENERATION_POLL_MS = 5000
