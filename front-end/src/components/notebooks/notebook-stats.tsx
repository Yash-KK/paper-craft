import { BookOpen, FileText } from "lucide-react"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { MOCK_NOTEBOOKS } from "@/lib/mock-notebooks"
import { cn } from "@/lib/utils"

type NotebookStatsProps = {
  className?: string
}

const totalDocuments = MOCK_NOTEBOOKS.reduce(
  (sum, notebook) => sum + notebook.documentCount,
  0
)

const stats = [
  {
    label: "Total Notebooks",
    value: String(MOCK_NOTEBOOKS.length),
    icon: BookOpen,
    accent: "text-violet-600 dark:text-violet-400",
    iconBg: "bg-violet-500/10",
  },
  {
    label: "Question Papers",
    value: String(totalDocuments),
    icon: FileText,
    accent: "text-teal-600 dark:text-teal-400",
    iconBg: "bg-teal-500/10",
  },
] as const

export function NotebookStats({ className }: NotebookStatsProps) {
  return (
    <div className={cn("grid gap-3 sm:grid-cols-2 sm:gap-4", className)}>
      {stats.map((stat) => (
        <Card
          key={stat.label}
          className="bg-card/80 shadow-sm backdrop-blur-sm transition-shadow hover:shadow-md"
        >
          <CardHeader className="flex-row items-center">
            <div
              className={cn(
                "flex size-10 shrink-0 items-center justify-center rounded-xl",
                stat.iconBg
              )}
            >
              <stat.icon className={cn("size-7", stat.accent)} />
            </div>
            <CardContent className="min-w-0 px-0">
              <CardDescription>{stat.label}</CardDescription>
              <CardTitle className="text-xl font-semibold tracking-tight">
                {stat.value}
              </CardTitle>
            </CardContent>
          </CardHeader>
        </Card>
      ))}
    </div>
  )
}
