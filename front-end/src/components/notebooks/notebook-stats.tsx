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
}

export function NotebookStats({ notebooks, className }: NotebookStatsProps) {
  const totalChapters = notebooks.reduce(
    (sum, nb) => sum + nb.selected_chapters.length,
    0
  )

  const stats = [
    {
      label: "Total Notebooks",
      value: String(notebooks.length),
      icon: BookOpen,
      accent: "text-violet-600 dark:text-violet-400",
      iconBg: "bg-violet-500/10",
    },
    {
      label: "Chapters Selected",
      value: String(totalChapters),
      icon: FileText,
      accent: "text-teal-600 dark:text-teal-400",
      iconBg: "bg-teal-500/10",
    },
  ] as const

  return (
    <div className={cn("grid gap-3 sm:grid-cols-2 sm:gap-4", className)}>
      {stats.map((stat) => (
        <Card key={stat.label} className="bg-card/80 shadow-sm">
          <CardHeader className="flex-row items-center">
            <div
              className={cn(
                "flex size-10 items-center justify-center rounded-xl",
                stat.iconBg
              )}
            >
              <stat.icon className={cn("size-5", stat.accent)} />
            </div>
            <CardContent className="min-w-0 px-0">
              <CardDescription>{stat.label}</CardDescription>
              <CardTitle className="text-xl font-semibold">{stat.value}</CardTitle>
            </CardContent>
          </CardHeader>
        </Card>
      ))}
    </div>
  )
}
