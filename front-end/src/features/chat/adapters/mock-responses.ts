import type { ChatStreamEvent, Citation } from "@/features/chat/types/chat"

function sleep(ms: number, signal?: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) {
      reject(new DOMException("Aborted", "AbortError"))
      return
    }
    const timer = window.setTimeout(resolve, ms)
    const onAbort = () => {
      window.clearTimeout(timer)
      reject(new DOMException("Aborted", "AbortError"))
    }
    signal?.addEventListener("abort", onAbort, { once: true })
  })
}

function eventId(prefix: string, n: number): string {
  return `${prefix}-${n}`
}

export function buildMockReply(userText: string, notebookName: string): string {
  const trimmed = userText.trim()
  const lower = trimmed.toLowerCase()

  if (lower.includes("mcq") || lower.includes("multiple choice")) {
    return [
      `Here are **3 MCQs** for **${notebookName}**:`,
      "",
      "1. Which statement is true?",
      "   A) Option A",
      "   B) Option B",
      "   C) Option C",
      "   D) Option D",
      "",
      "2. Fill in the conceptual gap for this chapter.",
      "   A) Definition",
      "   B) Example",
      "   C) Counter-example",
      "   D) All of the above",
      "",
      "3. Which approach best matches the syllabus?",
      "   A) Memorise only",
      "   B) Practise + revise",
      "   C) Skip proofs",
      "   D) Ignore NCERT",
      "",
      "_Mock RAG response — wire your Agentic RAG backend to replace this._",
    ].join("\n")
  }

  if (lower.includes("paper") || lower.includes("question")) {
    return [
      `I can help draft a question paper for **${notebookName}**.`,
      "",
      "Suggested structure:",
      "- Section A — 5 MCQs (1 mark)",
      "- Section B — 3 short answers (3 marks)",
      "- Section C — 2 long answers (5 marks)",
      "",
      `Prompt idea: “Create a 20-mark paper from chapters in ${notebookName}.”`,
      "",
      "_This is a mocked streaming reply._",
    ].join("\n")
  }

  return [
    `Thanks for your question about **${notebookName}**.`,
    "",
    `You asked: “${trimmed || "…"}”`,
    "",
    "In production, the Agentic RAG agent will:",
    "1. Retrieve relevant chapter chunks for this notebook",
    "2. Call tools (e.g. generate paper sections)",
    "3. Stream the final answer with citations",
    "",
    "_Mock assistant response — replace `MockChatTransport` with the real SSE client._",
  ].join("\n")
}

export function mockCitations(notebookName: string): Citation[] {
  return [
    {
      id: "cite-1",
      title: `${notebookName} — Chapter excerpt`,
      snippet:
        "Mock retrieved passage that would come from the vector store for this notebook.",
      chapter_number: 1,
      chapter_name: "Introduction",
      score: 0.91,
    },
    {
      id: "cite-2",
      title: `${notebookName} — Worked example`,
      snippet:
        "Mock secondary source used to ground the assistant answer.",
      chapter_number: 2,
      chapter_name: "Practice",
      score: 0.84,
    },
  ]
}

/** Tokenise reply into small chunks for streaming UX. */
export function chunkText(text: string, size = 12): string[] {
  const chunks: string[] = []
  for (let i = 0; i < text.length; i += size) {
    chunks.push(text.slice(i, i + size))
  }
  return chunks.length > 0 ? chunks : [""]
}

export async function* streamMockReply(options: {
  userText: string
  notebookName: string
  conversationId: string
  runId: string
  messageId: string
  signal?: AbortSignal
}): AsyncGenerator<ChatStreamEvent> {
  const {
    userText,
    notebookName,
    conversationId,
    runId,
    messageId,
    signal,
  } = options

  let n = 0
  yield {
    type: "run.started",
    event_id: eventId(runId, ++n),
    conversation_id: conversationId,
    run_id: runId,
  }

  await sleep(180, signal)

  const sources = mockCitations(notebookName)
  yield {
    type: "retrieved_sources",
    event_id: eventId(runId, ++n),
    sources,
  }

  await sleep(120, signal)

  yield {
    type: "tool.started",
    event_id: eventId(runId, ++n),
    tool: {
      tool_call_id: `tool-${runId}`,
      tool_name: "retrieve_notebook_context",
      status: "running",
      args: { notebook: notebookName, query: userText },
    },
  }

  await sleep(200, signal)

  yield {
    type: "tool.completed",
    event_id: eventId(runId, ++n),
    tool: {
      tool_call_id: `tool-${runId}`,
      tool_name: "retrieve_notebook_context",
      status: "completed",
      args: { notebook: notebookName, query: userText },
      result: { source_count: sources.length },
    },
  }

  const full = buildMockReply(userText, notebookName)
  let accumulated = ""

  for (const piece of chunkText(full, 18)) {
    await sleep(28, signal)
    accumulated += piece
    yield {
      type: "message.delta",
      event_id: eventId(runId, ++n),
      message_id: messageId,
      delta: piece,
    }
  }

  for (const citation of sources) {
    yield {
      type: "citation",
      event_id: eventId(runId, ++n),
      citation,
    }
  }

  yield {
    type: "message.completed",
    event_id: eventId(runId, ++n),
    message_id: messageId,
    content: accumulated,
    citations: sources,
  }

  yield {
    type: "run.completed",
    event_id: eventId(runId, n + 1),
    run_id: runId,
    conversation_id: conversationId,
  }
}
