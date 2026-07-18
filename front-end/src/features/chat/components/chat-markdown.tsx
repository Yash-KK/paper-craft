import type { ReactNode } from "react"

export function ChatMarkdown({ text }: { text: string }) {
  const lines = text.split("\n")
  const elements: ReactNode[] = []

  lines.forEach((line, i) => {
    const isBullet = /^[-*•]\s/.test(line)
    const content = line.replace(/^[-*•]\s/, "")
    const parts: ReactNode[] = []
    const pattern = /(\*\*[^*]+\*\*|`[^`]+`)/g
    let last = 0
    let match: RegExpExecArray | null
    let part = 0

    while ((match = pattern.exec(content)) !== null) {
      if (match.index > last) parts.push(content.slice(last, match.index))
      const token = match[0]
      if (token.startsWith("**")) {
        parts.push(<strong key={`${i}-${part}`}>{token.slice(2, -2)}</strong>)
      } else {
        parts.push(
          <code
            key={`${i}-${part}`}
            className="rounded bg-muted px-1 py-0.5 font-mono text-xs text-violet-700"
          >
            {token.slice(1, -1)}
          </code>
        )
      }
      last = match.index + token.length
      part += 1
    }
    if (last < content.length) parts.push(content.slice(last))

    if (isBullet) {
      elements.push(
        <li key={i} className="ml-4 list-disc">
          {parts}
        </li>
      )
    } else if (content.trim()) {
      elements.push(
        <p key={i} className="mb-1">
          {parts}
        </p>
      )
    } else {
      elements.push(<br key={i} />)
    }
  })

  return <div className="text-sm leading-relaxed">{elements}</div>
}
