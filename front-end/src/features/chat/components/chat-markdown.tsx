import { Streamdown } from "streamdown"
import { math } from "@streamdown/math"
import "katex/dist/katex.min.css"

type ChatMarkdownProps = {
  text: string
  isStreaming?: boolean
}

export function ChatMarkdown({ text, isStreaming }: ChatMarkdownProps) {
  return (
    <div className="typeset typeset-chat text-sm">
      <Streamdown plugins={{ math }} isAnimating={isStreaming}>
        {text}
      </Streamdown>
    </div>
  )
}
