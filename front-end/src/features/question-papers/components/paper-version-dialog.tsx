import * as React from "react"
import { renderAsync } from "docx-preview"
import { Download, Loader2 } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { fetchVersionExport } from "@/lib/api"
import { cn } from "@/lib/utils"

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
  const previewRef = React.useRef<HTMLDivElement>(null)
  const [filename, setFilename] = React.useState(
    `${paperTitle}_v${versionNumber}.docx`
  )
  const [blob, setBlob] = React.useState<Blob | null>(null)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const [downloading, setDownloading] = React.useState(false)

  React.useEffect(() => {
    if (!open) {
      setBlob(null)
      setError(null)
      setLoading(false)
      if (previewRef.current) previewRef.current.innerHTML = ""
      return
    }

    let cancelled = false
    setLoading(true)
    setError(null)
    setBlob(null)

    void fetchVersionExport(paperId, versionNumber, "paper")
      .then(({ blob: nextBlob, filename: nextFilename }) => {
        if (cancelled) return
        setFilename(nextFilename)
        setBlob(nextBlob)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setError(err instanceof Error ? err.message : "Failed to load document")
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [open, paperId, versionNumber])

  React.useEffect(() => {
    if (!blob || !previewRef.current) return

    let cancelled = false
    const container = previewRef.current
    container.innerHTML = ""

    void renderAsync(blob, container, undefined, {
      className: "docx-preview",
      inWrapper: true,
      ignoreWidth: false,
      breakPages: true,
    }).catch((err: unknown) => {
      if (cancelled) return
      setError(err instanceof Error ? err.message : "Failed to preview document")
    })

    return () => {
      cancelled = true
    }
  }, [blob])

  function handleDownload() {
    if (!blob) return
    setDownloading(true)
    try {
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement("a")
      anchor.href = url
      anchor.download = filename
      document.body.appendChild(anchor)
      anchor.click()
      anchor.remove()
      URL.revokeObjectURL(url)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Download failed")
    } finally {
      setDownloading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        showCloseButton
        className="flex h-[min(92vh,56rem)] max-w-[calc(100%-2rem)] flex-col gap-0 overflow-hidden p-0 sm:max-w-5xl"
      >
        <DialogHeader className="flex-row items-center justify-between gap-3 space-y-0 border-b px-5 py-4 pr-12">
          <DialogTitle className="truncate font-sans text-sm font-medium">
            {filename}
          </DialogTitle>
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="shrink-0"
            disabled={!blob || downloading}
            onClick={handleDownload}
          >
            {downloading ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <Download className="size-4" />
            )}
            Download
          </Button>
        </DialogHeader>

        <div className="relative min-h-0 flex-1 overflow-y-auto bg-muted/40 p-4 sm:p-6">
          {loading ? (
            <div className="absolute inset-0 z-10 flex items-center justify-center gap-2 bg-muted/40 text-sm text-muted-foreground">
              <Loader2 className="size-4 animate-spin" />
              Loading document…
            </div>
          ) : null}

          {error ? (
            <div className="flex min-h-64 items-center justify-center text-sm text-destructive">
              {error}
            </div>
          ) : null}

          <div
            ref={previewRef}
            className={cn(
              "docx-preview-container mx-auto w-full max-w-3xl rounded-lg bg-background shadow-sm",
              (loading || error) && "hidden"
            )}
          />
        </div>
      </DialogContent>
    </Dialog>
  )
}
