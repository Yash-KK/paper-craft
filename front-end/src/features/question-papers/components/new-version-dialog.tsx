import * as React from "react"
import { Loader2 } from "lucide-react"
import { useNavigate } from "react-router-dom"

import { useCreatePaperVersion } from "@/features/question-papers/hooks/use-create-paper-version"
import {
  canCreateNewVersion,
  versionHref,
} from "@/features/question-papers/lib/question-paper-utils"
import type { QuestionPaperSummary } from "@/lib/types/generation"
import type { PersistedMessage } from "@/features/chat/types/chat"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import { cn } from "@/lib/utils"

type NewVersionDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  notebookId: string
  paper: QuestionPaperSummary | null
  messages: PersistedMessage[]
  selectedMessageIds: string[]
  onSelectedMessageIdsChange: (ids: string[]) => void
  onLoadMoreMessages?: () => void
  hasMoreMessages?: boolean
  loadingMoreMessages?: boolean
}

export function NewVersionDialog({
  open,
  onOpenChange,
  notebookId,
  paper,
  messages,
  selectedMessageIds,
  onSelectedMessageIdsChange,
  onLoadMoreMessages,
  hasMoreMessages = false,
  loadingMoreMessages = false,
}: NewVersionDialogProps) {
  const navigate = useNavigate()
  const [teacherInstructions, setTeacherInstructions] = React.useState("")
  const createVersion = useCreatePaperVersion(paper?.id ?? "", notebookId)

  const selectableMessages = messages.filter(
    (message) => message.role === "user" || message.role === "assistant"
  )
  const selectedSet = React.useMemo(
    () => new Set(selectedMessageIds),
    [selectedMessageIds]
  )

  function toggleMessage(id: string) {
    if (selectedSet.has(id)) {
      onSelectedMessageIdsChange(selectedMessageIds.filter((item) => item !== id))
      return
    }
    onSelectedMessageIdsChange([...selectedMessageIds, id])
  }

  async function handleCreate() {
    if (!paper || !canCreateNewVersion(paper)) return
    const result = await createVersion.mutateAsync({
      selected_message_ids: selectedMessageIds,
      teacher_instructions: teacherInstructions.trim() || null,
    })
    onOpenChange(false)
    setTeacherInstructions("")
    onSelectedMessageIdsChange([])
    navigate(
      versionHref(notebookId, result.paper_id, result.version_number)
    )
  }

  const disabled =
    !paper ||
    !canCreateNewVersion(paper) ||
    createVersion.isPending

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[85vh] overflow-y-auto sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Create new version</DialogTitle>
          <DialogDescription>
            {paper
              ? `Builds the next version of “${paper.title}” from the latest ready paper and any selected chat guidance.`
              : "Select a paper first."}
          </DialogDescription>
        </DialogHeader>

        {!paper ? (
          <p className="text-sm text-muted-foreground">
            Choose a ready paper from the sidebar, then try again.
          </p>
        ) : !canCreateNewVersion(paper) ? (
          <p className="text-sm text-muted-foreground">
            {paper.versions.some(
              (version) =>
                version.status === "pending" || version.status === "running"
            )
              ? "A generation is already in progress for this paper."
              : "This paper has no ready version to revise. Generate a successful paper first."}
          </p>
        ) : (
          <div className="space-y-4">
            <div className="space-y-2">
              <p className="text-sm font-medium">Chat context</p>
              <p className="text-xs text-muted-foreground">
                Optional. Select saved messages that describe the changes you
                want. Fresh streamed messages become selectable after they are
                saved.
              </p>
              <div className="max-h-56 space-y-2 overflow-y-auto rounded-xl border p-2">
                {selectableMessages.length === 0 ? (
                  <p className="px-2 py-6 text-center text-xs text-muted-foreground">
                    No saved chat messages yet.
                  </p>
                ) : (
                  selectableMessages.map((message) => {
                    const checked = selectedSet.has(message.id)
                    return (
                      <label
                        key={message.id}
                        className={cn(
                          "flex cursor-pointer gap-3 rounded-lg border px-3 py-2 text-left transition-colors",
                          checked
                            ? "border-violet-500/40 bg-violet-500/5"
                            : "hover:bg-muted/50"
                        )}
                      >
                        <input
                          type="checkbox"
                          className="mt-1 size-4 accent-violet-600"
                          checked={checked}
                          onChange={() => toggleMessage(message.id)}
                        />
                        <span className="min-w-0 flex-1">
                          <span className="mb-1 block text-[10px] font-medium tracking-wide text-muted-foreground uppercase">
                            {message.role}
                          </span>
                          <span className="line-clamp-3 text-xs whitespace-pre-wrap">
                            {message.content}
                          </span>
                        </span>
                      </label>
                    )
                  })
                )}
              </div>
              {hasMoreMessages ? (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  disabled={loadingMoreMessages}
                  onClick={onLoadMoreMessages}
                >
                  {loadingMoreMessages ? (
                    <Loader2 className="size-4 animate-spin" aria-hidden />
                  ) : null}
                  Load older messages
                </Button>
              ) : null}
            </div>

            <div className="space-y-2">
              <label
                htmlFor="revision-instructions"
                className="text-sm font-medium"
              >
                Extra instructions
              </label>
              <Textarea
                id="revision-instructions"
                value={teacherInstructions}
                onChange={(event) => setTeacherInstructions(event.target.value)}
                placeholder="Optional notes for this revision"
                rows={3}
              />
            </div>
          </div>
        )}

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={createVersion.isPending}
          >
            Cancel
          </Button>
          <Button
            type="button"
            disabled={disabled}
            onClick={() => void handleCreate()}
          >
            {createVersion.isPending ? (
              <Loader2 className="size-4 animate-spin" aria-hidden />
            ) : null}
            Create version
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
