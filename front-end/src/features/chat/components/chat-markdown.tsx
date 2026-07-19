import { Streamdown } from "streamdown"
import { math } from "@streamdown/math"
import "katex/dist/katex.min.css"

export function ChatMarkdown({
  text,
  isStreaming,
}: {
  text: string
  isStreaming?: boolean
}) {
  return (
    <div className="typeset text-sm">
      <Streamdown plugins={{ math }} isAnimating={isStreaming}>
        {text}
      </Streamdown>
    </div>
  )
}
