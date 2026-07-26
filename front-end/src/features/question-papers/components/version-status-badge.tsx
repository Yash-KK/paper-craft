import { Badge } from "@/components/ui/badge"
import { QUESTION_PAPER_STATUS_LABELS } from "@/lib/types/generation"
import type { QuestionPaperStatus } from "@/lib/types/generation"
import { statusBadgeClass } from "@/features/question-papers/lib/question-paper-utils"
import { cn } from "@/lib/utils"

type VersionStatusBadgeProps = {
  status: QuestionPaperStatus
  className?: string
}

export function VersionStatusBadge({
  status,
  className,
}: VersionStatusBadgeProps) {
  return (
    <Badge
      variant="secondary"
      className={cn("h-5 px-1.5 text-[10px]", statusBadgeClass(status), className)}
    >
      {QUESTION_PAPER_STATUS_LABELS[status]}
    </Badge>
  )
}
