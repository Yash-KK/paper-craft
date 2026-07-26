import * as React from "react"
import {
  AlertCircle,
  Download,
  FileText,
  Loader2,
  RefreshCw,
} from "lucide-react"
import { Link } from "react-router-dom"
import { MathJaxContext } from "better-react-mathjax"
import { toast } from "sonner"

import { ChatMarkdown } from "@/features/chat/components/chat-markdown"
import { MATHJAX_CONFIG } from "@/features/chat/lib/mathjax-config"
import { VersionStatusBadge } from "@/features/question-papers/components/version-status-badge"
import { usePaperVersion } from "@/features/question-papers/hooks/use-paper-version"
import {
  formatRelativeTime,
  versionHref,
} from "@/features/question-papers/lib/question-paper-utils"
import { downloadVersionExport } from "@/lib/api"
import { isActiveGenerationStatus } from "@/lib/types/generation"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"

type PaperVersionViewProps = {
  notebookId: string
  paperId: string
  versionNumber: number
  siblingVersions?: number[]
}

export function PaperVersionView({
  notebookId,
  paperId,
  versionNumber,
  siblingVersions = [],
}: PaperVersionViewProps) {
  const query = usePaperVersion(paperId, versionNumber)
  const [tab, setTab] = React.useState<"paper" | "answer_key">("paper")
  const [exporting, setExporting] = React.useState<"paper" | "answer_key" | null>(
    null
  )

  async function handleExport(variant: "paper" | "answer_key") {
    try {
      setExporting(variant)
      await downloadVersionExport(paperId, versionNumber, variant)
      toast.success(
        variant === "answer_key" ? "Answer key downloaded." : "Paper downloaded."
      )
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Export failed")
    } finally {
      setExporting(null)
    }
  }

  if (query.isPending) {
    return (
      <div className="mx-auto flex w-full max-w-4xl flex-col gap-4 px-4 py-6 sm:px-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-5 w-40" />
        <Skeleton className="h-96 w-full rounded-2xl" />
      </div>
    )
  }

  if (query.isError || !query.data) {
    return (
      <div className="mx-auto flex w-full max-w-lg flex-1 flex-col items-center justify-center gap-4 px-4 py-16 text-center">
        <AlertCircle className="size-8 text-destructive" aria-hidden />
        <h1 className="font-heading text-xl font-semibold">
          Unable to load version
        </h1>
        <p className="text-sm text-muted-foreground">
          {query.error instanceof Error
            ? query.error.message
            : "This version could not be loaded."}
        </p>
        <div className="flex gap-2">
          <Button type="button" onClick={() => void query.refetch()}>
            Try again
          </Button>
          <Button
            type="button"
            variant="outline"
            render={<Link to={`/notebooks/${notebookId}`} />}
          >
            Back to notebook
          </Button>
        </div>
      </div>
    )
  }

  const version = query.data
  const isActive = isActiveGenerationStatus(version.status)
  const markdown =
    tab === "paper" ? version.paper_markdown : version.answer_key_markdown
  const versions =
    siblingVersions.length > 0
      ? siblingVersions
      : [version.version_number]

  return (
    <MathJaxContext config={MATHJAX_CONFIG}>
      <div className="mx-auto flex w-full max-w-4xl flex-col gap-5 px-4 py-6 sm:px-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0 space-y-2">
            <p className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
              Question paper
            </p>
            <h1 className="font-heading text-2xl font-semibold tracking-tight">
              {version.title}
            </h1>
            <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
              <VersionStatusBadge status={version.status} />
              <span>Version {version.version_number}</span>
              <span>·</span>
              <span>{version.subject}</span>
              <span>·</span>
              <span>Class {version.grade}</span>
              <span>·</span>
              <span>Updated {formatRelativeTime(version.updated_at)}</span>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={version.status !== "ready" || exporting !== null}
              onClick={() => void handleExport("paper")}
            >
              {exporting === "paper" ? (
                <Loader2 className="size-4 animate-spin" aria-hidden />
              ) : (
                <Download className="size-4" aria-hidden />
              )}
              Paper DOCX
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={version.status !== "ready" || exporting !== null}
              onClick={() => void handleExport("answer_key")}
            >
              {exporting === "answer_key" ? (
                <Loader2 className="size-4 animate-spin" aria-hidden />
              ) : (
                <FileText className="size-4" aria-hidden />
              )}
              Answer key
            </Button>
          </div>
        </div>

        {versions.length > 1 ? (
          <div className="flex flex-wrap gap-2">
            {versions.map((number) => (
              <Button
                key={number}
                type="button"
                size="sm"
                variant={number === versionNumber ? "default" : "outline"}
                render={
                  <Link to={versionHref(notebookId, paperId, number)} />
                }
              >
                v{number}
              </Button>
            ))}
          </div>
        ) : null}

        {isActive ? (
          <div className="flex items-start gap-3 rounded-2xl border border-sky-500/20 bg-sky-500/5 px-4 py-3">
            <Loader2
              className="mt-0.5 size-4 shrink-0 animate-spin text-sky-600"
              aria-hidden
            />
            <div className="space-y-1">
              <p className="text-sm font-medium">
                {version.status === "pending"
                  ? "Queued for generation"
                  : "Generating this version"}
              </p>
              <p className="text-xs text-muted-foreground">
                This page refreshes automatically every few seconds.
              </p>
            </div>
          </div>
        ) : null}

        {version.status === "failed" ? (
          <div className="flex flex-col items-start gap-3 rounded-2xl border border-destructive/20 bg-destructive/5 px-4 py-4">
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="size-4" aria-hidden />
              <p className="text-sm font-medium">Generation failed</p>
            </div>
            <p className="text-xs text-muted-foreground">
              {version.error ||
                "The worker could not finish this version. Start a new paper, or create a new version from a ready base."}
            </p>
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={() => void query.refetch()}
            >
              <RefreshCw className="size-4" aria-hidden />
              Refresh status
            </Button>
          </div>
        ) : null}

        {version.selected_chat_messages.length > 0 ? (
          <details className="rounded-2xl border px-4 py-3">
            <summary className="cursor-pointer text-sm font-medium">
              Revision chat context ({version.selected_chat_messages.length})
            </summary>
            <div className="mt-3 space-y-2">
              {version.selected_chat_messages.map((message) => (
                <div
                  key={message.id}
                  className="rounded-xl bg-muted/50 px-3 py-2 text-xs"
                >
                  <p className="mb-1 font-medium uppercase tracking-wide text-muted-foreground">
                    {message.role}
                  </p>
                  <p className="whitespace-pre-wrap text-foreground">
                    {message.content}
                  </p>
                </div>
              ))}
            </div>
          </details>
        ) : null}

        <div className="flex gap-2 border-b pb-2">
          <TabButton
            active={tab === "paper"}
            onClick={() => setTab("paper")}
            label="Question paper"
          />
          <TabButton
            active={tab === "answer_key"}
            onClick={() => setTab("answer_key")}
            label="Answer key"
          />
        </div>

        <div className="min-h-72 rounded-2xl border bg-card px-4 py-5 sm:px-6">
          {version.status === "ready" && markdown.trim() ? (
            <ChatMarkdown text={markdown} />
          ) : version.status === "ready" ? (
            <p className="text-sm text-muted-foreground">
              No markdown is available for this tab yet.
            </p>
          ) : (
            <p className="text-sm text-muted-foreground">
              Content appears here once generation finishes.
            </p>
          )}
        </div>
      </div>
    </MathJaxContext>
  )
}

function TabButton({
  active,
  onClick,
  label,
}: {
  active: boolean
  onClick: () => void
  label: string
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "min-h-10 rounded-lg px-3 text-sm font-medium outline-none transition-colors focus-visible:ring-2 focus-visible:ring-ring",
        active
          ? "bg-violet-600 text-white"
          : "text-muted-foreground hover:bg-muted hover:text-foreground"
      )}
    >
      {label}
    </button>
  )
}
