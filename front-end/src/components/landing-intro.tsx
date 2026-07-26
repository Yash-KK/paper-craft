import {
  BookOpenText,
  FileText,
  LayoutTemplate,
  ListChecks,
  Sparkles,
} from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

const features = [
  {
    icon: BookOpenText,
    title: "Chapter-aware questions",
    description:
      "Pick the chapters you've taught and get questions drawn from that syllabus scope.",
  },
  {
    icon: LayoutTemplate,
    title: "Blueprint-driven structure",
    description:
      "Start from a ready blueprint or set your own sections, marks split, and difficulty mix.",
  },
  {
    icon: ListChecks,
    title: "Marking scheme included",
    description:
      "Every paper ships with answers and step-wise marks, ready for evaluation day.",
  },
  {
    icon: FileText,
    title: "Your school's format",
    description:
      "Upload a past paper and PaperCraft mirrors its layout, headings, and instructions.",
  },
]

type LandingIntroProps = {
  className?: string
}

export function LandingIntro({ className }: LandingIntroProps) {
  return (
    <section className={cn("flex flex-col gap-8", className)}>
      <div className="flex flex-col gap-5">
        <Badge
          variant="outline"
          className="h-7 gap-1.5 border-violet-500/20 bg-violet-500/10 px-3 text-violet-700 dark:text-violet-300"
        >
          <Sparkles />
          AI-powered question paper generation
        </Badge>

        <div className="space-y-4">
          <h1 className="font-heading text-4xl font-semibold tracking-tight text-balance sm:text-5xl">
            Create question papers in minutes
          </h1>
          <p className="max-w-xl text-base text-pretty text-muted-foreground sm:text-lg">
            PaperCraft helps teachers generate high-quality, curriculum-aligned
            question papers in just a few clicks. Select chapters, choose a
            blueprint, and let AI draft a well-structured paper while you stay
            in complete control.
          </p>
        </div>
      </div>

      <ul className="grid gap-5 sm:grid-cols-2">
        {features.map((feature) => (
          <li key={feature.title} className="flex gap-3">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-violet-500/10 text-violet-600 dark:text-violet-400">
              <feature.icon className="size-4.5" />
            </span>
            <div className="space-y-1">
              <p className="text-sm font-medium">{feature.title}</p>
              <p className="text-sm text-pretty text-muted-foreground">
                {feature.description}
              </p>
            </div>
          </li>
        ))}
      </ul>

      <p className="text-sm text-muted-foreground">
        No setup required — every question stays editable before you print.
      </p>
    </section>
  )
}
