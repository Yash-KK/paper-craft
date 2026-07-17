import { BookOpen, FileText } from "lucide-react"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import type { NotebookListItem } from "@/lib/types/notebook"
import { cn } from "@/lib/utils"

type NotebookStatsProps = {
  notebooks: NotebookListItem[]
  className?: string
  compact?: boolean
}

export function NotebookStats({
  notebooks,
  className,
  compact = false,
}: NotebookStatsProps) {
  const stats = [
    {
      label: "Total Notebooks",
      value: String(notebooks.length),
      icon: BookOpen,
      accent: "text-violet-600 dark:text-violet-400",
      iconBg: "bg-violet-500/10",
    },
    {
      label: "Question Papers",
      value: String(0),
      icon: FileText,
      accent: "text-teal-600 dark:text-teal-400",
      iconBg: "bg-teal-500/10",
    },
  ] as const

  return (
    <div
      className={cn(
        "grid gap-3",
        !compact && "sm:grid-cols-2 sm:gap-4",
        className
      )}
    >
      {stats.map((stat) => (
        <Card
          key={stat.label}
          size={compact ? "sm" : "default"}
          className={cn("bg-card/80 shadow-sm", compact && "gap-0")}
        >
          <CardHeader
            className={cn(
              "flex-row items-center",
              compact && "gap-3 px-3 py-3"
            )}
          >
            <div
              className={cn(
                "flex items-center justify-center rounded-xl",
                compact ? "size-9" : "size-10",
                stat.iconBg
              )}
            >
              <stat.icon
                className={cn(compact ? "size-4" : "size-5", stat.accent)}
              />
            </div>
            <CardContent className="min-w-0 px-0">
              <CardDescription className={cn(compact && "text-xs")}>
                {stat.label}
              </CardDescription>
              <CardTitle
                className={cn(
                  "font-semibold",
                  compact ? "text-lg" : "text-xl"
                )}
              >
                {stat.value}
              </CardTitle>
            </CardContent>
          </CardHeader>
        </Card>
      ))}
    </div>
  )
}
