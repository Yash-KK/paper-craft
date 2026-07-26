import * as React from "react"
import { useMutation } from "@tanstack/react-query"
import { toast } from "sonner"

import {
  useGenerateQuestionPaper,
  useSampleBlueprints,
} from "@/hooks/use-sample-blueprints"
import { fetchSampleBlueprint } from "@/lib/api"
import type { NotebookListItem, SelectedChapter } from "@/lib/types/notebook"
import {
  classGradeToNumber,
  emptyBlueprint,
  hasForeignChapterAllocations,
  rematchBlueprintChapters,
  sectionLetter,
  type BlueprintSection,
  type ChapterAllocation,
  type QuestionPaperBlueprint,
  type SampleBlueprintSummary,
} from "@/lib/types/generation"

export function useGeneratePaperForm(
  notebook: NotebookListItem,
  schoolName: string | null
) {
  const chapters = notebook.selected_chapters
  const samplesQuery = useSampleBlueprints()
  const generateMutation = useGenerateQuestionPaper()

  const [sample, setSample] = React.useState<SampleBlueprintSummary | null>(null)
  const [teacherInstructions, setTeacherInstructions] = React.useState("")
  const [blueprint, setBlueprint] = React.useState<QuestionPaperBlueprint>(() =>
    emptyBlueprint({
      school_name: schoolName,
      subject: notebook.subject ?? "Mathematics",
      grade: classGradeToNumber(notebook.class_grade),
    })
  )

  function patchBlueprint(patch: Partial<QuestionPaperBlueprint>) {
    setBlueprint((prev) => ({ ...prev, ...patch }))
  }

  function updateSections(
    updater: (sections: BlueprintSection[]) => BlueprintSection[]
  ) {
    setBlueprint((prev) => ({ ...prev, sections: updater(prev.sections) }))
  }

  const applySampleMutation = useMutation({
    mutationFn: async (next: SampleBlueprintSummary) => {
      if (chapters.length === 0) {
        throw new Error(
          "Select chapters on this notebook before applying a blueprint."
        )
      }
      const detail = await fetchSampleBlueprint(next.id)
      return {
        sample: next,
        blueprint: {
          ...rematchBlueprintChapters(
            structuredClone(detail.blueprint),
            chapters
          ),
          school_name: schoolName ?? detail.blueprint.school_name,
          subject: notebook.subject ?? detail.blueprint.subject,
          grade:
            classGradeToNumber(notebook.class_grade) || detail.blueprint.grade,
        },
      }
    },
    onSuccess: ({ sample: next, blueprint: nextBlueprint }) => {
      setSample(next)
      setBlueprint(nextBlueprint)
      setTeacherInstructions("")
    },
    onError: (err) => {
      toast.error(
        err instanceof Error ? err.message : "Failed to load sample blueprint"
      )
    },
  })

  function updateSection(index: number, patch: Partial<BlueprintSection>) {
    updateSections((sections) =>
      sections.map((section, i) =>
        i === index ? { ...section, ...patch } : section
      )
    )
  }

  function updateAllocation(
    sectionIndex: number,
    allocIndex: number,
    patch: Partial<ChapterAllocation>
  ) {
    updateSections((sections) =>
      sections.map((section, i) => {
        if (i !== sectionIndex) return section
        return {
          ...section,
          chapter_allocations: section.chapter_allocations.map((alloc, j) =>
            j === allocIndex ? { ...alloc, ...patch } : alloc
          ),
        }
      })
    )
  }

  function addChapter(sectionIndex: number, chapter: SelectedChapter) {
    updateSections((sections) =>
      sections.map((section, i) => {
        if (i !== sectionIndex) return section
        if (
          section.chapter_allocations.some(
            (alloc) => alloc.chapter_number === chapter.chapter_number
          )
        ) {
          return section
        }
        return {
          ...section,
          chapter_allocations: [
            ...section.chapter_allocations,
            {
              chapter_number: chapter.chapter_number,
              chapter_name: chapter.chapter_name,
              question_count: 1,
              blooms_level: null,
              has_internal_choice: false,
              is_assertion_reason: false,
              marks: null,
            },
          ],
        }
      })
    )
  }

  function removeAllocation(sectionIndex: number, allocIndex: number) {
    updateSections((sections) =>
      sections.map((section, i) =>
        i === sectionIndex
          ? {
              ...section,
              chapter_allocations: section.chapter_allocations.filter(
                (_, j) => j !== allocIndex
              ),
            }
          : section
      )
    )
  }

  function addSection() {
    updateSections((sections) => [
      ...sections,
      {
        section_name: `Section ${sectionLetter(sections.length)}`,
        question_type: "MCQ",
        marks_each: 1,
        chapter_allocations: [],
        section_instructions: null,
      },
    ])
  }

  function removeSection(index: number) {
    updateSections((sections) => sections.filter((_, i) => i !== index))
  }

  async function generate() {
    if (!sample) {
      toast.error("Select a sample blueprint first.")
      return false
    }
    if (chapters.length === 0) {
      toast.error("Select at least one chapter on the notebook first.")
      return false
    }
    if (blueprint.sections.length === 0) {
      toast.error("Add at least one section to the marking scheme.")
      return false
    }
    if (hasForeignChapterAllocations(blueprint, chapters)) {
      toast.error(
        "Marking scheme includes chapters outside this notebook. Remove them or rematch."
      )
      return false
    }

    try {
      await generateMutation.mutateAsync({
        blueprint,
        selected_chapters: chapters,
        subject: blueprint.subject,
        grade: blueprint.grade,
        teacher_instructions: teacherInstructions.trim() || null,
      })
      return true
    } catch {
      return false
    }
  }

  return {
    chapters,
    samples: samplesQuery.data ?? [],
    samplesLoading: samplesQuery.isPending,
    sample,
    sampleSelected: Boolean(sample),
    applyingSample: applySampleMutation.isPending,
    applySample: applySampleMutation.mutate,
    blueprint,
    patchBlueprint,
    teacherInstructions,
    setTeacherInstructions,
    updateSection,
    updateAllocation,
    addChapter,
    removeAllocation,
    addSection,
    removeSection,
    generate,
    generating: generateMutation.isPending,
  }
}
