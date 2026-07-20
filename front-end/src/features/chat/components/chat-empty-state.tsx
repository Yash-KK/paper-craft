import { Button } from "@/components/ui/button"

const SUGGESTIONS = [
  "Explain the key concepts in this notebook",
  "Walk me through a worked example",
] as const

type ChatEmptyStateProps = {
  notebookName: string
  onSend: (prompt: string) => void
}

export function ChatEmptyState({ notebookName, onSend }: ChatEmptyStateProps) {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center pb-8 text-center select-none">
      <h2 className="font-heading mb-2 text-xl font-semibold">
        Chat with {notebookName}
      </h2>
      <p className="mb-5 max-w-sm text-sm text-muted-foreground">
        Ask for explanations or worked examples grounded in this
        notebook&apos;s chapters.
      </p>
      <div className="flex flex-wrap justify-center gap-2">
        {SUGGESTIONS.map((suggestion) => (
          <Button
            key={suggestion}
            type="button"
            variant="outline"
            size="xs"
            onClick={() => onSend(suggestion)}
            className="rounded-full text-muted-foreground"
          >
            {suggestion}
          </Button>
        ))}
      </div>
    </div>
  )
}
