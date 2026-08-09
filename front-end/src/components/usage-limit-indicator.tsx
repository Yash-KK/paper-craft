import { Badge } from "@/components/ui/badge"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"

export type UsageLimitResource = "question_paper" | "chat_message"

export function isUsageLimitReached(usage: number, limit: number): boolean {
  return usage >= limit
}

export function usageLimitTooltip(
  resource: UsageLimitResource,
  usage: number,
  limit: number
): string {
  const remaining = Math.max(0, limit - usage)
  if (remaining === 0) return "Limit Reached"

  if (resource === "question_paper") {
    if (usage === 0) {
      return `Can generate ${remaining} question paper${remaining === 1 ? "" : "s"}`
    }
    return `Can generate ${remaining} more question paper${remaining === 1 ? "" : "s"}`
  }

  return `Can ask ${remaining} more question${remaining === 1 ? "" : "s"}`
}

type UsageLimitIndicatorProps = {
  usage: number
  limit: number
  resource: UsageLimitResource
  className?: string
}

export function UsageLimitIndicator({
  usage,
  limit,
  resource,
  className,
}: UsageLimitIndicatorProps) {
  const atLimit = isUsageLimitReached(usage, limit)
  const tooltip = usageLimitTooltip(resource, usage, limit)

  return (
    <Tooltip>
      <TooltipTrigger
        type="button"
        className={cn(
          "inline-flex cursor-default items-center gap-1.5 rounded-md outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50",
          className
        )}
        aria-label={tooltip}
      >
        <Badge variant={atLimit ? "destructive" : "secondary"}>
          {usage}/{limit}
        </Badge>
        {atLimit ? (
          <span className="text-xs font-medium text-destructive">
            Limit Reached
          </span>
        ) : null}
      </TooltipTrigger>
      <TooltipContent>{tooltip}</TooltipContent>
    </Tooltip>
  )
}
