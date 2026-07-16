export type NotebookTheme = "violet" | "teal" | "amber" | "rose" | "sky"

export type MockNotebook = {
  id: string
  title: string
  description: string
  classGrade: string
  chapters: string[]
  documentCount: number
  lastUpdated: string
  theme: NotebookTheme
}

export const MOCK_NOTEBOOKS: MockNotebook[] = [
  {
    id: "nb-1",
    title: "Mid-Term Prep",
    description: "Focused revision for the upcoming mid-term across key chapters.",
    classGrade: "Class 9",
    chapters: ["Ch 1", "Ch 3", "Ch 5", "Ch 7"],
    documentCount: 3,
    lastUpdated: "2026-07-10",
    theme: "violet",
  },
  {
    id: "nb-2",
    title: "Final Exam — Math",
    description: "Comprehensive question papers and practice sets for board prep.",
    classGrade: "Class 10",
    chapters: ["Ch 2", "Ch 4", "Ch 6", "Ch 8", "Ch 12"],
    documentCount: 5,
    lastUpdated: "2026-07-14",
    theme: "teal",
  },
  {
    id: "nb-3",
    title: "Practice Sets",
    description: "Quick drills and mixed-topic worksheets for daily practice.",
    classGrade: "Class 9",
    chapters: ["Ch 2", "Ch 9", "Ch 11"],
    documentCount: 2,
    lastUpdated: "2026-07-15",
    theme: "amber",
  },
]

export const NOTEBOOK_THEME_STYLES: Record<
  NotebookTheme,
  {
    stripe: string
    iconBg: string
    iconText: string
    badge: string
    glow: string
    dot: string
  }
> = {
  violet: {
    stripe: "bg-violet-500",
    iconBg: "bg-violet-500/10",
    iconText: "text-violet-600 dark:text-violet-400",
    badge: "bg-violet-500/10 text-violet-700 dark:text-violet-300",
    glow: "group-hover:shadow-violet-500/20",
    dot: "bg-violet-500",
  },
  teal: {
    stripe: "bg-teal-500",
    iconBg: "bg-teal-500/10",
    iconText: "text-teal-600 dark:text-teal-400",
    badge: "bg-teal-500/10 text-teal-700 dark:text-teal-300",
    glow: "group-hover:shadow-teal-500/20",
    dot: "bg-teal-500",
  },
  amber: {
    stripe: "bg-amber-500",
    iconBg: "bg-amber-500/10",
    iconText: "text-amber-600 dark:text-amber-400",
    badge: "bg-amber-500/10 text-amber-700 dark:text-amber-300",
    glow: "group-hover:shadow-amber-500/20",
    dot: "bg-amber-500",
  },
  rose: {
    stripe: "bg-rose-500",
    iconBg: "bg-rose-500/10",
    iconText: "text-rose-600 dark:text-rose-400",
    badge: "bg-rose-500/10 text-rose-700 dark:text-rose-300",
    glow: "group-hover:shadow-rose-500/20",
    dot: "bg-rose-500",
  },
  sky: {
    stripe: "bg-sky-500",
    iconBg: "bg-sky-500/10",
    iconText: "text-sky-600 dark:text-sky-400",
    badge: "bg-sky-500/10 text-sky-700 dark:text-sky-300",
    glow: "group-hover:shadow-sky-500/20",
    dot: "bg-sky-500",
  },
}

export function formatNotebookDate(isoDate: string): string {
  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(isoDate))
}
