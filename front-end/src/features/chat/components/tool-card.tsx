import { BookOpen, Globe, Loader2 } from "lucide-react"

import type { ToolCall } from "@/features/chat/types/chat"

const TOOL_LABELS: Record<string, string> = {
  retrieve_context: "Using TextBooks",
  web_search: "Using Web Search",
}

export function ToolCallCard({ tc }: { tc: ToolCall }) {
  const running = tc.status === "running"
  const label = TOOL_LABELS[tc.tool] ?? `Using ${tc.tool.replace(/_/g, " ")}`
  const ToolIcon = tc.tool === "web_search" ? Globe : BookOpen

  return (
    <div
      className={`my-1.5 flex items-center gap-2 rounded-xl border px-3 py-2 text-xs ${
        running
          ? "border-violet-200 bg-violet-50/60 text-violet-700"
          : "border-border bg-muted/40 text-muted-foreground"
      }`}
    >
      {running ? (
        <Loader2 size={12} className="shrink-0 animate-spin" />
      ) : (
        <ToolIcon size={12} className="shrink-0 text-emerald-500" />
      )}
      <span className="font-semibold">{running ? label : `✓ ${label}`}</span>
    </div>
  )
}
