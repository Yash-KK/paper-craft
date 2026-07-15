import * as React from "react"
import { Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

type ButtonVariant = React.ComponentProps<typeof Button>["variant"]

type ConfirmDialogProps = {
  title: React.ReactNode
  description?: React.ReactNode
  children?: React.ReactNode
  trigger?: React.ReactElement
  open?: boolean
  onOpenChange?: (open: boolean) => void
  confirmLabel?: string
  cancelLabel?: string
  confirmVariant?: ButtonVariant
  onConfirm?: () => void | Promise<void>
}

export function ConfirmDialog({
  title,
  description,
  children,
  trigger,
  open,
  onOpenChange,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  confirmVariant = "default",
  onConfirm,
}: ConfirmDialogProps) {
  const [internalOpen, setInternalOpen] = React.useState(false)
  const [pending, setPending] = React.useState(false)

  const isControlled = open !== undefined
  const actualOpen = isControlled ? open : internalOpen

  const setOpen = React.useCallback(
    (next: boolean) => {
      if (!isControlled) {
        setInternalOpen(next)
      }
      onOpenChange?.(next)
    },
    [isControlled, onOpenChange]
  )

  async function handleConfirm() {
    try {
      setPending(true)
      await onConfirm?.()
      setOpen(false)
    } finally {
      setPending(false)
    }
  }

  return (
    <Dialog open={actualOpen} onOpenChange={setOpen}>
      {trigger && <DialogTrigger render={trigger} />}
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          {description && <DialogDescription>{description}</DialogDescription>}
        </DialogHeader>

        {children}

        <DialogFooter>
          <DialogClose render={<Button variant="outline" disabled={pending} />}>
            {cancelLabel}
          </DialogClose>
          <Button
            variant={confirmVariant}
            onClick={handleConfirm}
            disabled={pending}
          >
            {pending && <Loader2 className="animate-spin" />}
            {confirmLabel}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
