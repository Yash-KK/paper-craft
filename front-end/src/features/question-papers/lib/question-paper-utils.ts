import {
  isActiveGenerationStatus,
  paperHasActiveGeneration,
  type QuestionPaperSummary,
} from "@/lib/types/generation"
import { isPersistedChatMessageId } from "@/features/chat/lib/chat-stream-utils"

export function isPersistedMessageId(id: string): boolean {
  return isPersistedChatMessageId(id)
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
