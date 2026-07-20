const LATEX_DOC_MARKERS =
  /\\(?:section\*?|textbf|emph|textit|begin\{(?:itemize|enumerate)\}|vspace|quad)\b/

/** True when content uses LaTeX document markup (not normal Markdown). */
export function looksLikeLatexDocument(content: string): boolean {
  return LATEX_DOC_MARKERS.test(content)
}

/**
 * Normalize LaTeX math delimiters to remark-math friendly `$` / `$$`.
 * Does not alter other Markdown.
 */
export function normalizeMathDelimiters(content: string): string {
  let next = content
  next = next.replace(/\\\[([\s\S]*?)\\\]/g, (_m, tex: string) => {
    return `\n$$\n${tex.trim()}\n$$\n`
  })
  next = next.replace(/\\\(([\s\S]*?)\\\)/g, (_m, tex: string) => {
    return `$${tex}$`
  })
  return next
}

/** Convert common LaTeX document markup to Markdown. */
export function convertLatexToMarkdown(latexContent: string): string {
  let markdownContent = latexContent

  markdownContent = markdownContent.replace(
    /\\section\*\{([^}]+)\}/g,
    "## $1"
  )
  markdownContent = markdownContent.replace(/\\section\{([^}]+)\}/g, "## $1")

  markdownContent = markdownContent.replace(/\\textbf\{([^}]+)\}/g, "**$1**")
  markdownContent = markdownContent.replace(/\\emph\{([^}]+)\}/g, "*$1*")
  markdownContent = markdownContent.replace(/\\textit\{([^}]+)\}/g, "*$1*")

  markdownContent = markdownContent.replace(
    /\\begin\{enumerate\}([\s\S]*?)\\end\{enumerate\}/g,
    (_match, body: string) => body.replace(/\\item\s+/g, "1. ")
  )
  markdownContent = markdownContent.replace(
    /\\begin\{itemize\}([\s\S]*?)\\end\{itemize\}/g,
    (_match, body: string) => body.replace(/\\item\s+/g, "- ")
  )

  markdownContent = markdownContent.replace(/\\vspace\{[^}]+\}/g, "\n\n")
  markdownContent = markdownContent.replace(/\\\\(?:\[[^\]]*\])?/g, "\n")

  markdownContent = markdownContent.replace(/\\text\{([^}]+)\}/g, "$1")
  markdownContent = markdownContent.replace(/\\quad/g, "    ")

  markdownContent = markdownContent.replace(/\n\s*\n\s*\n/g, "\n\n")

  return markdownContent
}

/** Prepare chat content for Markdown rendering. */
export function prepareMarkdownContent(content: string): string {
  const withMath = normalizeMathDelimiters(content)
  if (looksLikeLatexDocument(withMath)) {
    return convertLatexToMarkdown(withMath)
  }
  return withMath
}
