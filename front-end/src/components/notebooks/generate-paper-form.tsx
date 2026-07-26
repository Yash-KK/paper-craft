import type { ReactNode } from "react"
import { FileText, ListChecks, Loader2, Plus, Sparkles } from "lucide-react"

import { MarkingSchemeSection } from "@/components/notebooks/marking-scheme-section"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { MenuSelect } from "@/components/ui/menu-select"
import { Textarea } from "@/components/ui/textarea"
import { useGeneratePaperForm } from "@/hooks/use-generate-paper-form"
import type { NotebookListItem } from "@/lib/types/notebook"
import {
  blueprintAllocatedMarks,
  DURATION_OPTIONS,
} from "@/lib/types/generation"
import { cn } from "@/lib/utils"

type GeneratePaperFormProps = {
  notebook: NotebookListItem
  schoolName: string | null
  onGenerated?: () => void
  onCancel?: () => void
}

function FormPanel({
  icon,
  title,
  description,
  trailing,
  children,
}: {
  icon?: ReactNode
  title: string
  description?: string
  trailing?: ReactNode
  children: ReactNode
}) {
  return (
    <section className="overflow-hidden rounded-2xl border bg-card">
      <div className="flex items-start justify-between gap-3 border-b bg-violet-500/10 px-4 py-3 sm:px-5">
        <div className="flex items-start gap-3">
          {icon}
          <div>
            <h2 className="font-heading text-base font-semibold">{title}</h2>
            {description ? (
              <p className="text-xs text-muted-foreground">{description}</p>
            ) : null}
          </div>
        </div>
        {trailing}
      </div>
      <div className="p-4 sm:p-5">{children}</div>
    </section>
  )
}

function PanelIcon({ children }: { children: ReactNode }) {
  return (
    <span className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-xl bg-violet-600 text-white">
      {children}
    </span>
  )
}

export function GeneratePaperForm({
  notebook,
  schoolName,
  onGenerated,
  onCancel,
}: GeneratePaperFormProps) {
  const form = useGeneratePaperForm(notebook, schoolName)
  const allocated = blueprintAllocatedMarks(form.blueprint)
  const marksMismatch = allocated !== form.blueprint.total_marks
  const classSubject = `${notebook.class_grade ?? "Class"} — ${notebook.subject ?? "Subject"}`

  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col gap-6 px-4 py-6 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-1">
          <p className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
            Question paper
          </p>
          <h1 className="font-heading text-2xl font-semibold tracking-tight">
            Generate Paper
          </h1>
          <p className="text-sm text-muted-foreground">
            Choose a sample blueprint, review the scheme, then generate. Chapters
            are limited to this notebook&apos;s selection.
          </p>
        </div>
        <div className="flex shrink-0 gap-2">
          {onCancel ? (
            <Button type="button" variant="outline" onClick={onCancel}>
              Cancel
            </Button>
          ) : null}
          <Button
            type="button"
            className="gap-2 bg-emerald-600 text-white hover:bg-emerald-600/90"
            disabled={
              !form.sampleSelected || form.generating || form.chapters.length === 0
            }
            onClick={() => void form.generate().then((ok) => ok && onGenerated?.())}
          >
            {form.generating ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <Sparkles className="size-4" />
            )}
            Generate Paper
          </Button>
        </div>
      </div>

      <div className="grid gap-2 rounded-2xl border bg-card p-4 sm:p-5">
        <MenuSelect
          label="Sample Blueprint"
          value={form.sample?.id ?? ""}
          placeholder="Select a sample blueprint"
          disabled={form.chapters.length === 0}
          loading={form.samplesLoading || form.applyingSample}
          className="h-11 w-full justify-between font-normal sm:max-w-md"
          options={form.samples.map((sample) => ({
            value: sample.id,
            label: sample.label,
          }))}
          onChange={(id) => {
            const next = form.samples.find((sample) => sample.id === id)
            if (next) form.applySample(next)
          }}
        />
        <p
          className={cn(
            "text-xs",
            form.chapters.length === 0
              ? "text-destructive"
              : "text-muted-foreground"
          )}
        >
          {form.chapters.length === 0
            ? "Add chapters to this notebook before selecting a blueprint."
            : `Available chapters: ${form.chapters
                .map((chapter) => `Ch ${chapter.chapter_number}`)
                .join(", ")}`}
        </p>
      </div>

      <FormPanel
        icon={
          <PanelIcon>
            <FileText className="size-4" />
          </PanelIcon>
        }
        title="Paper Details"
        description="Basic information for your paper."
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="grid gap-2 sm:col-span-2">
            <Label htmlFor="school-name">School Name</Label>
            <Input
              id="school-name"
              value={form.blueprint.school_name ?? ""}
              disabled={!form.sampleSelected}
              onChange={(e) =>
                form.patchBlueprint({ school_name: e.target.value || null })
              }
            />
          </div>

          <div className="grid gap-2 sm:col-span-2">
            <div className="flex items-center gap-2">
              <Label>Class & Subject</Label>
              <Badge variant="secondary" className="h-5 px-1.5 text-[10px]">
                Locked
              </Badge>
            </div>
            <Input value={classSubject} disabled />
          </div>

          <div className="grid gap-2 sm:col-span-2">
            <Label htmlFor="exam-title">Exam Title</Label>
            <Input
              id="exam-title"
              value={form.blueprint.exam_title ?? ""}
              disabled={!form.sampleSelected}
              onChange={(e) =>
                form.patchBlueprint({ exam_title: e.target.value || null })
              }
            />
          </div>

          <MenuSelect
            label="Duration"
            value={form.blueprint.duration_minutes ?? ""}
            placeholder="Select duration"
            disabled={!form.sampleSelected}
            options={DURATION_OPTIONS.map((option) => ({
              value: option.minutes,
              label: option.label,
            }))}
            onChange={(duration_minutes) =>
              form.patchBlueprint({ duration_minutes })
            }
          />

          <div className="grid gap-2">
            <Label htmlFor="total-marks">Total Marks</Label>
            <Input
              id="total-marks"
              type="number"
              min={1}
              value={form.blueprint.total_marks}
              disabled={!form.sampleSelected}
              onChange={(e) =>
                form.patchBlueprint({
                  total_marks: Number(e.target.value) || 0,
                })
              }
            />
          </div>

          <div className="grid gap-2 sm:col-span-2">
            <Label htmlFor="exam-date">Exam Date</Label>
            <Input
              id="exam-date"
              type="date"
              value={form.blueprint.exam_date ?? ""}
              disabled={!form.sampleSelected}
              onChange={(e) =>
                form.patchBlueprint({ exam_date: e.target.value || null })
              }
            />
          </div>
        </div>
      </FormPanel>

      {form.sampleSelected ? (
        <>
          <FormPanel
            icon={
              <PanelIcon>
                <ListChecks className="size-4" />
              </PanelIcon>
            }
            title="Marking Scheme"
            description="Sections, question types, and chapter distribution."
            trailing={
              <span
                className={cn(
                  "shrink-0 text-sm font-semibold",
                  marksMismatch
                    ? "text-destructive"
                    : "text-emerald-600 dark:text-emerald-400"
                )}
              >
                Total: {allocated}/{form.blueprint.total_marks}
              </span>
            }
          >
            <div className="space-y-4">
              {form.blueprint.sections.map((section, index) => (
                <MarkingSchemeSection
                  key={`${section.section_name}-${index}`}
                  index={index}
                  section={section}
                  chapters={form.chapters}
                  onChange={(patch) => form.updateSection(index, patch)}
                  onUpdateAllocation={(allocIndex, patch) =>
                    form.updateAllocation(index, allocIndex, patch)
                  }
                  onAddChapter={(chapter) => form.addChapter(index, chapter)}
                  onRemoveAllocation={(allocIndex) =>
                    form.removeAllocation(index, allocIndex)
                  }
                  onRemove={() => form.removeSection(index)}
                />
              ))}
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="gap-1.5"
                onClick={form.addSection}
              >
                <Plus className="size-3.5" />
                Add Section
              </Button>
            </div>
          </FormPanel>

          <FormPanel
            title="Teacher Instructions"
            description="Optional preferences for the AI. These do not change the blueprint — they are added to the generation prompt only."
          >
            <Textarea
              value={form.teacherInstructions}
              onChange={(e) => form.setTeacherInstructions(e.target.value)}
              placeholder={
                "Focus more on application-based questions.\nAvoid direct textbook questions.\nInclude at least one challenging numerical."
              }
              className="min-h-32"
            />
          </FormPanel>
        </>
      ) : (
        <div className="rounded-2xl border border-dashed px-4 py-16 text-center text-sm text-muted-foreground">
          Select a sample blueprint above to auto-fill paper details and the
          marking scheme. All fields stay editable afterward.
        </div>
      )}
    </div>
  )
}
