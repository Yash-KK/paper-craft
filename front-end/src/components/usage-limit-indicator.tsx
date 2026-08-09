import { Badge } from "@/components/ui/badge"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"

export const DEFAULT_QUESTION_PAPER_LIMIT = 2
export const DEFAULT_VERSION_LIMIT = 2
export const DEFAULT_CHAT_MESSAGE_LIMIT = 5

type UsageLimitResource = "question_paper" | "chat_message"

function usageLimitTooltip(
  resource: UsageLimitResource,
  usage: number,
  limit: number
): string {
  const remaining = Math.max(0, limit - usage)
  if (remaining === 0) return "Limit Reached"

  if (resource === "question_paper") {
    const noun = remaining === 1 ? "question paper" : "question papers"
    return usage === 0
      ? `Can generate ${remaining} ${noun}`
      : `Can generate ${remaining} more ${noun}`
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
  const atLimit = usage >= limit
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
