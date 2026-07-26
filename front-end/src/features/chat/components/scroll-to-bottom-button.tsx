import { ArrowDown } from "lucide-react"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

type ScrollToBottomButtonProps = {
  visible: boolean
  onClick: () => void
}

export function ScrollToBottomButton({
  visible,
  onClick,
}: ScrollToBottomButtonProps) {
  return (
    <Button
      type="button"
      variant="outline"
      size="icon-sm"
      aria-label="Scroll to bottom"
      tabIndex={visible ? 0 : -1}
      onClick={onClick}
      className={cn(
        "absolute right-4 bottom-3 z-10 rounded-full border-transparent bg-orange-300 text-orange-950 shadow-md transition-all duration-200 hover:bg-orange-300 hover:text-orange-950 dark:bg-orange-300 dark:hover:bg-orange-300",
        visible
          ? "translate-y-0 opacity-100"
          : "pointer-events-none translate-y-1 opacity-0"
      )}
    >
      <ArrowDown className="size-4" />
    </Button>
  )
}
