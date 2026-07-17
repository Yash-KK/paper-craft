import { BookOpen, ChevronDown, ChevronRight, Globe, Loader2 } from "lucide-react"
import { useState } from "react"

import type { ToolCall } from "@/features/chat/types/chat"

const TOOL_LABELS: Record<string, string> = {
  retrieve_context: "Notebook Sources",
  web_search: "Web Search",
  tavily_search: "Web Search",
}

function label(tool: string) {
  return TOOL_LABELS[tool] ?? tool.replace(/_/g, " ")
}

export function ToolCallCard({ tc }: { tc: ToolCall }) {
  const [open, setOpen] = useState(false)
  const running = tc.status === "running"
  const ToolIcon =
    tc.tool === "web_search" || tc.tool === "tavily_search" ? Globe : BookOpen

  return (
    <div
      className={`my-1.5 overflow-hidden rounded-xl border text-xs transition-colors ${
        running
          ? "border-violet-200 bg-violet-50/60"
          : "cursor-pointer border-border bg-muted/40 hover:border-muted-foreground/30"
      }`}
    >
      <button
        type="button"
        className="flex w-full select-none items-center gap-2 px-3 py-2 text-left"
        onClick={() => !running && setOpen((o) => !o)}
        disabled={running}
      >
        {running ? (
          <Loader2 size={12} className="shrink-0 animate-spin text-violet-500" />
        ) : (
          <ToolIcon size={12} className="shrink-0 text-emerald-500" />
        )}

        <span
          className={`shrink-0 font-semibold ${
            running ? "text-violet-700" : "text-muted-foreground"
          }`}
        >
          {running ? "Searching…" : `✓ ${label(tc.tool)}`}
        </span>

        <span className="flex-1 truncate font-normal text-muted-foreground">
          {tc.input}
        </span>

        {!running &&
          (open ? (
            <ChevronDown size={12} className="shrink-0 text-muted-foreground" />
          ) : (
            <ChevronRight size={12} className="shrink-0 text-muted-foreground" />
          ))}
      </button>

      {open && tc.output ? (
        <div className="border-t border-border px-3 pt-1 pb-3">
          <p className="leading-relaxed whitespace-pre-wrap text-muted-foreground">
            {tc.output}
          </p>
        </div>
      ) : null}
    </div>
  )
}
