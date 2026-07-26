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
  blueprintAllocatedMarks,
  blueprintQuestionCount,
  classGradeToNumber,
  emptyBlueprint,
  hasForeignChapterAllocations,
  isMarkBasedBlueprint,
  rematchBlueprintChapters,
  sectionLetter,
  updateGroupedQuestionCount,
  type BlueprintSection,
  type QuestionPaperBlueprint,
  type SampleBlueprintSummary,
} from "@/lib/types/generation"

export function useGeneratePaperForm(
  notebook: NotebookListItem,
  schoolName: string | null
) {
  const chapters = notebook.selected_chapters
  const samplesQuery = useSampleBlueprints({
    board: notebook.board,
    subject: notebook.subject,
  })
  const generateMutation = useGenerateQuestionPaper()

  const [sample, setSample] = React.useState<SampleBlueprintSummary | null>(
    null
  )
  const [teacherInstructions, setTeacherInstructions] = React.useState("")
  const [formatReference, setFormatReference] = React.useState<File | null>(
    null
  )
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
        blueprint: rematchBlueprintChapters(detail.blueprint, chapters),
      }
    },
    onSuccess: ({ sample: next, blueprint: nextBlueprint }) => {
      setSample(next)
      setBlueprint((prev) => ({
        ...nextBlueprint,
        school_name: prev.school_name ?? schoolName,
        subject: notebook.subject ?? nextBlueprint.subject,
        grade: classGradeToNumber(notebook.class_grade),
      }))
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

  function updateChapterQuestionCount(
    sectionIndex: number,
    allocationIndexes: number[],
    questionCount: number
  ) {
    updateSections((sections) =>
      sections.map((section, index) =>
        index === sectionIndex
          ? {
              ...section,
              chapter_allocations: updateGroupedQuestionCount(
                section.chapter_allocations,
                allocationIndexes,
                questionCount
              ),
            }
          : section
      )
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

  function removeChapterAllocations(
    sectionIndex: number,
    allocationIndexes: number[]
  ) {
    const targetIndexes = new Set(allocationIndexes)
    updateSections((sections) =>
      sections.map((section, i) =>
        i === sectionIndex
          ? {
              ...section,
              chapter_allocations: section.chapter_allocations.filter(
                (_, allocationIndex) => !targetIndexes.has(allocationIndex)
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
        marks_each: isMarkBasedBlueprint(blueprint) ? 1 : null,
        chapter_allocations: [],
        section_instructions: null,
        sub_parts: [],
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
      toast.error("Add at least one section to the blueprint.")
      return false
    }
    if (isMarkBasedBlueprint(blueprint)) {
      const allocatedMarks = blueprintAllocatedMarks(blueprint)
      if (
        allocatedMarks == null ||
        blueprint.total_marks == null ||
        allocatedMarks !== blueprint.total_marks
      ) {
        toast.error(
          `Marking scheme totals ${allocatedMarks ?? "?"} marks, but the paper total is ${blueprint.total_marks}.`
        )
        return false
      }
    } else if (blueprintQuestionCount(blueprint) < 1) {
      toast.error("Add at least one question to the revision sheet.")
      return false
    }
    if (hasForeignChapterAllocations(blueprint, chapters)) {
      toast.error(
        "Blueprint includes chapters outside this notebook. Remove them or rematch."
      )
      return false
    }

    try {
      const submissionBlueprint = {
        ...blueprint,
        general_instructions: blueprint.general_instructions
          .map((instruction) => instruction.trim())
          .filter(Boolean),
        learning_outcomes: blueprint.learning_outcomes
          .map((outcome) => outcome.trim())
          .filter(Boolean),
        generation_rules: blueprint.generation_rules
          .map((rule) => rule.trim())
          .filter(Boolean),
      }
      await generateMutation.mutateAsync({
        notebook_id: notebook.id,
        blueprint: submissionBlueprint,
        selected_chapters: chapters,
        subject: submissionBlueprint.subject,
        grade: submissionBlueprint.grade,
        teacher_instructions: teacherInstructions.trim() || null,
        format_reference_uri: sample.format_reference_uri,
        format_reference: formatReference,
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
    applyingSample: applySampleMutation.isPending,
    applySample: applySampleMutation.mutate,
    blueprint,
    patchBlueprint,
    teacherInstructions,
    setTeacherInstructions,
    formatReference,
    setFormatReference,
    updateSection,
    updateChapterQuestionCount,
    addChapter,
    removeChapterAllocations,
    addSection,
    removeSection,
    generate,
    generating: generateMutation.isPending,
  }
}
