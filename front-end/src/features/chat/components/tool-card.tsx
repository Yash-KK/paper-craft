import { BookOpen, Globe, Loader2 } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import type { ToolCall } from "@/features/chat/types/chat"
import { cn } from "@/lib/utils"

const TOOL_LABELS: Record<string, string> = {
  retrieve_context: "Using Textbook",
  web_search: "Using Web Search",
}

export function ToolCallCard({ tc }: { tc: ToolCall }) {
  const running = tc.status === "running"
  const label = TOOL_LABELS[tc.tool] ?? `Using ${tc.tool.replace(/_/g, " ")}`
  const ToolIcon = tc.tool === "web_search" ? Globe : BookOpen

  return (
    <Badge
      variant="outline"
      className={cn(
        "my-1.5 h-auto gap-2 rounded-xl px-3 py-2 font-semibold",
        running
          ? "border-violet-200 bg-violet-50/60 text-violet-700"
          : "bg-muted/40 text-muted-foreground"
      )}
    >
      {running ? (
        <Loader2 className="size-3 animate-spin" />
      ) : (
        <ToolIcon className="size-3 text-emerald-500" />
      )}
      {running ? label : `✓ ${label}`}
    </Badge>
  )
}
