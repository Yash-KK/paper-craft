import { Download, Info, Loader2 } from "lucide-react"
import { MathJaxContext } from "better-react-mathjax"
import { useQuery } from "@tanstack/react-query"
import { toast } from "sonner"

import { ChatMarkdown } from "@/features/chat/components/chat-markdown"
import { MATHJAX_CONFIG } from "@/features/chat/lib/mathjax-config"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { downloadVersionExport, fetchPaperVersion } from "@/lib/api"
import { queryKeys } from "@/lib/query-keys"
import { cn } from "@/lib/utils"
import * as React from "react"

type PaperVersionDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  paperId: string
  paperTitle: string
  versionNumber: number
}

export function PaperVersionDialog({
  open,
  onOpenChange,
  paperId,
  paperTitle,
  versionNumber,
}: PaperVersionDialogProps) {
  const [downloading, setDownloading] = React.useState(false)

  const versionQuery = useQuery({
    queryKey: queryKeys.paperVersion(paperId, versionNumber),
    queryFn: () => fetchPaperVersion(paperId, versionNumber),
    enabled: open,
  })

  async function handleDownload() {
    setDownloading(true)
    try {
      await downloadVersionExport(paperId, versionNumber)
      toast.success("Question paper downloaded.")
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Download failed")
    } finally {
      setDownloading(false)
    }
  }

  const title = `${paperTitle} — Version ${versionNumber}`
  const markdown = versionQuery.data?.paper_markdown ?? ""

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        showCloseButton
        className="flex h-[min(92vh,56rem)] max-w-[calc(100%-2rem)] flex-col gap-0 overflow-hidden p-0 sm:max-w-5xl"
      >
        <DialogHeader className="flex-row items-center justify-between gap-3 space-y-0 border-b px-5 py-4 pr-12">
          <DialogTitle className="truncate font-sans text-sm font-medium">
            {title}
          </DialogTitle>
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="shrink-0"
            disabled={downloading || versionQuery.data?.status !== "ready"}
            onClick={() => void handleDownload()}
          >
            {downloading ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <Download className="size-4" />
            )}
            Download DOCX
          </Button>
        </DialogHeader>

        <div className="flex items-start gap-2 border-b bg-amber-500/10 px-5 py-3 text-xs text-amber-950 dark:text-amber-100">
          <Info className="mt-0.5 size-4 shrink-0" aria-hidden />
          <p>
            This is a preview only. Formatting may differ from the final paper.
            Download DOCX for the actual question paper.
          </p>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto bg-muted/40 p-4 sm:p-6">
          {versionQuery.isPending ? (
            <div className="flex min-h-64 items-center justify-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="size-4 animate-spin" />
              Loading preview…
            </div>
          ) : versionQuery.isError ? (
            <div className="flex min-h-64 items-center justify-center text-sm text-destructive">
              {versionQuery.error instanceof Error
                ? versionQuery.error.message
                : "Failed to load preview"}
            </div>
          ) : (
            <MathJaxContext config={MATHJAX_CONFIG}>
              <div
                className={cn(
                  "mx-auto max-w-3xl rounded-lg bg-background p-6 shadow-sm",
                  !markdown.trim() && "text-sm text-muted-foreground"
                )}
              >
                {markdown.trim() ? (
                  <ChatMarkdown text={markdown} />
                ) : (
                  "No preview content available."
                )}
              </div>
            </MathJaxContext>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
