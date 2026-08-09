import * as React from "react"
import { Check, Loader2 } from "lucide-react"

import { useChatSelectionOptional } from "@/providers/chat-selection-provider"
import { useAuth } from "@/providers/auth-provider"
import { useCreatePaperVersion } from "@/features/question-papers/hooks/use-create-paper-version"
import {
  canCreateNewVersion,
  isPersistedMessageId,
  nextVersionNumber,
} from "@/features/question-papers/lib/question-paper-utils"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { DEFAULT_VERSION_LIMIT } from "@/components/usage-limit-indicator"
import { useNotebookChatMessages } from "@/hooks/use-notebook-chat-messages"
import type { QuestionPaperSummary } from "@/lib/types/generation"

const INSTRUCTIONS_PLACEHOLDER = `Add any additional instructions...

Examples:
• Replace the first two MCQs with the selected questions.
• Don't change anything else.
• Increase the difficulty of Section B.
• Replace only the Case Study questions.`

type GenerateVersionDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  notebookId: string
  paper: QuestionPaperSummary
}

export function GenerateVersionDialog({
  open,
  onOpenChange,
  notebookId,
  paper,
}: GenerateVersionDialogProps) {
  const { user } = useAuth()
  const versionLimit = user?.version_limit ?? DEFAULT_VERSION_LIMIT
  const [teacherInstructions, setTeacherInstructions] = React.useState("")
  const selection = useChatSelectionOptional()
  const messagesQuery = useNotebookChatMessages(notebookId, open)
  const {
    data: messagesData,
    hasNextPage,
    isFetchingNextPage,
    fetchNextPage,
  } = messagesQuery
  const createVersion = useCreatePaperVersion(paper.id, notebookId)
  const versionNumber = nextVersionNumber(paper)
  const canGenerate = canCreateNewVersion(paper, versionLimit)

  const allPersistedIds = React.useMemo(() => {
    const pages = messagesData?.pages ?? []
    return [...pages]
      .reverse()
      .flatMap((page) => page.items)
      .filter(
        (message) =>
          isPersistedMessageId(message.id) &&
          (message.role === "user" || message.role === "assistant")
      )
      .map((message) => message.id)
  }, [messagesData])

  const explicitSelectedIds = React.useMemo(() => {
    if (!selection || selection.selectedCount === 0) return []
    return allPersistedIds.filter((id) => selection.isSelected(id))
  }, [allPersistedIds, selection])

  const usingAllMessages = explicitSelectedIds.length === 0
  const effectiveCount = usingAllMessages
    ? allPersistedIds.length
    : explicitSelectedIds.length

  React.useEffect(() => {
    if (!open || !usingAllMessages) return
    if (!hasNextPage || isFetchingNextPage) return
    void fetchNextPage()
  }, [
    open,
    usingAllMessages,
    hasNextPage,
    isFetchingNextPage,
    fetchNextPage,
  ])

  function handleOpenChange(nextOpen: boolean) {
    if (!nextOpen) setTeacherInstructions("")
    onOpenChange(nextOpen)
  }

  async function handleGenerate() {
    if (!canGenerate) return
    const selected_message_ids = usingAllMessages
      ? allPersistedIds
      : explicitSelectedIds
    await createVersion.mutateAsync({
      selected_message_ids,
      teacher_instructions: teacherInstructions.trim() || null,
    })
    selection?.clear()
    setTeacherInstructions("")
    onOpenChange(false)
  }

  const pending =
    createVersion.isPending ||
    (usingAllMessages && (Boolean(hasNextPage) || isFetchingNextPage))

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Generate Version {versionNumber}</DialogTitle>
          <DialogDescription className="flex items-start gap-2 text-sm text-foreground">
            <Check
              className="mt-0.5 size-4 shrink-0 text-emerald-600 dark:text-emerald-400"
              aria-hidden
            />
            <span>
              {isFetchingNextPage || (usingAllMessages && hasNextPage)
                ? "Loading chat messages…"
                : `${effectiveCount} chat message${effectiveCount === 1 ? "" : "s"} selected as context for Version ${versionNumber}.`}
            </span>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-2">
          <Label htmlFor="generate-version-instructions">
            Teacher instructions{" "}
            <span className="font-normal text-muted-foreground">(optional)</span>
          </Label>
          <Textarea
            id="generate-version-instructions"
            value={teacherInstructions}
            onChange={(event) => setTeacherInstructions(event.target.value)}
            placeholder={INSTRUCTIONS_PLACEHOLDER}
            className="min-h-40"
          />
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => handleOpenChange(false)}
            disabled={createVersion.isPending}
          >
            Cancel
          </Button>
          <Button
            type="button"
            disabled={!canGenerate || pending}
            onClick={() => void handleGenerate()}
          >
            {createVersion.isPending ? (
              <Loader2 className="size-4 animate-spin" aria-hidden />
            ) : null}
            Generate Version
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
