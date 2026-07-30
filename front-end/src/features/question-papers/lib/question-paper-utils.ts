import {
  isActiveGenerationStatus,
  paperHasActiveGeneration,
  type QuestionPaperSummary,
} from "@/lib/types/generation"

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i

export function isPersistedMessageId(id: string): boolean {
  return UUID_RE.test(id)
}

export function canCreateNewVersion(paper: QuestionPaperSummary): boolean {
  if (paperHasActiveGeneration(paper)) return false
  return paper.versions.some((version) => version.status === "ready")
}

export function nextVersionNumber(paper: QuestionPaperSummary): number {
  if (paper.versions.length === 0) return 1
  return Math.max(...paper.versions.map((version) => version.version_number)) + 1
}

export const GENERATION_POLL_MS = 5000

export { isActiveGenerationStatus }
