export type MockQuestionPaper = {
  id: string
  title: string
  status: "draft" | "ready"
  marks: number
  updated_at: string
}

export const MOCK_QUESTION_PAPERS: MockQuestionPaper[] = [
  {
    id: "qp-1",
    title: "Unit Test — Algebra",
    status: "ready",
    marks: 40,
    updated_at: "2 days ago",
  },
  {
    id: "qp-2",
    title: "Mid-Term Practice Set",
    status: "draft",
    marks: 80,
    updated_at: "Yesterday",
  },
  {
    id: "qp-3",
    title: "MCQ Drill — Ch 1–3",
    status: "ready",
    marks: 20,
    updated_at: "Just now",
  },
]
