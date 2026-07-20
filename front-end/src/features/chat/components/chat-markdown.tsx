import { useMemo } from "react"
import ReactMarkdown, { type Components } from "react-markdown"
import remarkMath from "remark-math"
import { MathJax } from "better-react-mathjax"
import type { Element } from "hast"

import { prepareMarkdownContent } from "@/features/chat/lib/latex-markdown"
import { cn } from "@/lib/utils"

function classList(className: unknown): string[] {
  if (Array.isArray(className)) {
    return className.map(String)
  }
  if (typeof className === "string") {
    return className.split(/\s+/).filter(Boolean)
  }
  return []
}

function hastText(node: Element | undefined): string {
  if (!node) return ""
  return node.children
    .map((child) => (child.type === "text" ? child.value : ""))
    .join("")
}

function isMathDisplayPre(node: Element | undefined): boolean {
  const first = node?.children?.[0]
  if (!first || first.type !== "element" || first.tagName !== "code") {
    return false
  }
  return classList(first.properties?.className).includes("math-display")
}

const markdownComponents: Components = {
  h1: ({ className, ...props }) => (
    <h1
      className={cn("mt-3 mb-2 text-base font-semibold first:mt-0", className)}
      {...props}
    />
  ),
  h2: ({ className, ...props }) => (
    <h2
      className={cn("mt-3 mb-1.5 text-sm font-semibold first:mt-0", className)}
      {...props}
    />
  ),
  h3: ({ className, ...props }) => (
    <h3
      className={cn("mt-2.5 mb-1 text-sm font-semibold first:mt-0", className)}
      {...props}
    />
  ),
  p: ({ className, ...props }) => (
    <p
      className={cn("my-2 leading-relaxed first:mt-0 last:mb-0", className)}
      {...props}
    />
  ),
  ul: ({ className, ...props }) => (
    <ul className={cn("my-2 list-disc space-y-1 pl-5", className)} {...props} />
  ),
  ol: ({ className, ...props }) => (
    <ol
      className={cn("my-2 list-decimal space-y-1 pl-5", className)}
      {...props}
    />
  ),
  li: ({ className, ...props }) => (
    <li className={cn("leading-relaxed", className)} {...props} />
  ),
  strong: ({ className, ...props }) => (
    <strong className={cn("font-semibold", className)} {...props} />
  ),
  em: ({ className, ...props }) => (
    <em className={cn("italic", className)} {...props} />
  ),
  a: ({ className, ...props }) => (
    <a
      className={cn(
        "font-medium text-violet-600 underline underline-offset-2 hover:text-violet-700",
        className
      )}
      target="_blank"
      rel="noreferrer"
      {...props}
    />
  ),
  code: ({ className, children, ...props }) => {
    const classes = classList(className)
    if (classes.includes("math-inline")) {
      return (
        <MathJax inline dynamic>
          {`\\(${String(children)}\\)`}
        </MathJax>
      )
    }
    if (classes.includes("math-display")) {
      return (
        <MathJax dynamic className="my-2 overflow-x-auto">
          {`\\[${String(children)}\\]`}
        </MathJax>
      )
    }

    const isBlock = classes.some((c) => c.startsWith("language-"))
    if (isBlock) {
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
  pre: ({ className, children, node, ...props }) => {
    if (isMathDisplayPre(node)) {
      const codeNode = node?.children?.[0] as Element | undefined
      const tex = hastText(codeNode)
      return (
        <MathJax dynamic className="my-2 overflow-x-auto">
          {`\\[${tex}\\]`}
        </MathJax>
      )
    }
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
  blockquote: ({ className, ...props }) => (
    <blockquote
      className={cn(
        "my-2 border-l-2 border-violet-300 pl-3 text-muted-foreground",
        className
      )}
      {...props}
    />
  ),
  hr: ({ className, ...props }) => (
    <hr className={cn("my-3 border-border", className)} {...props} />
  ),
}

export function ChatMarkdown({ text }: { text: string; isStreaming?: boolean }) {
  const markdown = useMemo(() => prepareMarkdownContent(text), [text])

  return (
    <div className="typeset text-sm text-foreground">
      <ReactMarkdown
        remarkPlugins={[remarkMath]}
        components={markdownComponents}
      >
        {markdown}
      </ReactMarkdown>
    </div>
  )
}
