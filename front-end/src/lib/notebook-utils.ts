export type NotebookTheme = "violet" | "teal" | "amber" | "rose" | "sky"

const COLOR_THEME: Record<string, NotebookTheme> = {
  "#7c3aed": "violet",
  "#14b8a6": "teal",
  "#f59e0b": "amber",
  "#ec4899": "rose",
  "#22c55e": "teal",
  "#d946ef": "violet",
}

const FALLBACK_THEMES: NotebookTheme[] = ["violet", "teal", "amber", "rose", "sky"]

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

export function notebookTheme(
  colorHex: string | null | undefined,
  index: number
): NotebookTheme {
  if (colorHex && COLOR_THEME[colorHex.toLowerCase()]) {
    return COLOR_THEME[colorHex.toLowerCase()]
  }
  return FALLBACK_THEMES[index % FALLBACK_THEMES.length]
}

export function formatNotebookDate(isoDate: string): string {
  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(isoDate))
}
