import { BookOpen, Plus } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { cn } from "@/lib/utils"

type NotebooksEmptyStateProps = {
  onCreateClick?: () => void
  className?: string
}

export function NotebooksEmptyState({
  onCreateClick,
  className,
}: NotebooksEmptyStateProps) {
  return (
    <Card
      className={cn(
        "rounded-2xl border-dashed bg-muted/20 py-0 ring-border/80",
        className
      )}
    >
      <CardHeader className="items-center gap-4 pt-10 text-center">
        <div className="flex size-16 items-center justify-center rounded-2xl bg-violet-500/10">
          <BookOpen className="size-8 text-violet-600 dark:text-violet-400" />
        </div>
        <CardTitle className="text-xl font-semibold">
          No notebooks yet
        </CardTitle>
        <CardDescription className="max-w-sm text-center">
          Create your first notebook to organize question papers, chapters, and
          study materials in one place.
        </CardDescription>
      </CardHeader>
      <Separator />
      <CardFooter className="justify-center border-t-0 bg-transparent pb-10">
        <Button className="gap-2" onClick={onCreateClick}>
          <Plus />
          Create Notebook
        </Button>
      </CardFooter>
    </Card>
  )
}
