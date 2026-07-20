import ReactMarkdown, { type Components } from "react-markdown"
import remarkMath from "remark-math"
import { MathJax } from "better-react-mathjax"
import type { Element } from "hast"

import { prepareMarkdownContent } from "@/features/chat/lib/latex-markdown"
import { cn } from "@/lib/utils"

function classList(className: unknown): string[] {
  if (Array.isArray(className)) return className.map(String)
  if (typeof className === "string") return className.split(/\s+/).filter(Boolean)
  return []
}

function isMathDisplayPre(node: Element | undefined): boolean {
  const first = node?.children?.[0]
  if (!first || first.type !== "element" || first.tagName !== "code") return false
  return classList(first.properties?.className).includes("math-display")
}

const components: Components = {
  code({ className, children, ...props }) {
    const classes = classList(className)
    if (classes.includes("math-inline")) {
      return <MathJax inline dynamic>{`\\(${String(children)}\\)`}</MathJax>
    }
    if (classes.includes("math-display")) {
      return (
        <MathJax dynamic className="my-2 overflow-x-auto">
          {`\\[${String(children)}\\]`}
        </MathJax>
      )
    }
    if (classes.some((c) => c.startsWith("language-"))) {
      return (
        <code className={cn("font-mono text-[0.8em]", className)} {...props}>
          {children}
        </code>
      )
    }
    return (
      <code
        className={cn(
          "rounded bg-muted px-1 py-0.5 font-mono text-[0.85em]",
          className
        )}
        {...props}
      >
        {children}
      </code>
    )
  },
  pre({ className, children, node, ...props }) {
    if (isMathDisplayPre(node)) return <>{children}</>
    return (
      <pre
        className={cn(
          "my-2 overflow-x-auto rounded-lg bg-muted px-3 py-2 font-mono text-[0.8em]",
          className
        )}
        {...props}
      >
        {children}
      </pre>
    )
  },
  a({ className, ...props }) {
    return (
      <a
        className={cn(
          "font-medium text-violet-600 underline underline-offset-2 hover:text-violet-700",
          className
        )}
        target="_blank"
        rel="noreferrer"
        {...props}
      />
    )
  },
}

const wrapperClass = cn(
  "typeset text-sm text-foreground",
  "[&_h1]:mt-3 [&_h1]:mb-2 [&_h1]:text-base [&_h1]:font-semibold [&_h1:first-child]:mt-0",
  "[&_h2]:mt-3 [&_h2]:mb-1.5 [&_h2]:text-sm [&_h2]:font-semibold [&_h2:first-child]:mt-0",
  "[&_h3]:mt-2.5 [&_h3]:mb-1 [&_h3]:text-sm [&_h3]:font-semibold [&_h3:first-child]:mt-0",
  "[&_p]:my-2 [&_p]:leading-relaxed [&_p:first-child]:mt-0 [&_p:last-child]:mb-0",
  "[&_ul]:my-2 [&_ul]:list-disc [&_ul]:space-y-1 [&_ul]:pl-5",
  "[&_ol]:my-2 [&_ol]:list-decimal [&_ol]:space-y-1 [&_ol]:pl-5",
  "[&_li]:leading-relaxed",
  "[&_blockquote]:my-2 [&_blockquote]:border-l-2 [&_blockquote]:border-violet-300 [&_blockquote]:pl-3 [&_blockquote]:text-muted-foreground"
)

export function ChatMarkdown({ text }: { text: string }) {
  return (
    <div className={wrapperClass}>
      <ReactMarkdown remarkPlugins={[remarkMath]} components={components}>
        {prepareMarkdownContent(text)}
      </ReactMarkdown>
    </div>
  )
}
