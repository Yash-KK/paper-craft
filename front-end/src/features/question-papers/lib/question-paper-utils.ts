import {
  isActiveGenerationStatus,
  paperHasActiveGeneration,
  type QuestionPaperSummary,
} from "@/lib/types/generation"

export { isPersistedChatMessageId as isPersistedMessageId } from "@/features/chat/lib/chat-stream-utils"

export function canCreateNewVersion(
  paper: QuestionPaperSummary,
  versionLimit = Number.POSITIVE_INFINITY
): boolean {
  if (paper.versions.length >= versionLimit) return false
  if (paperHasActiveGeneration(paper)) return false
  return paper.versions.some((version) => version.status === "ready")
}

export function canCancelVersion(
  version: Pick<
    QuestionPaperSummary["versions"][number],
    "version_number" | "status"
  >
): boolean {
  return (
    version.version_number === 1 && isActiveGenerationStatus(version.status)
  )
}

export function nextVersionNumber(paper: QuestionPaperSummary): number {
  if (paper.versions.length === 0) return 1
  return (
    Math.max(...paper.versions.map((version) => version.version_number)) + 1
  )
}

export const GENERATION_POLL_MS = 5000

export { isActiveGenerationStatus }
