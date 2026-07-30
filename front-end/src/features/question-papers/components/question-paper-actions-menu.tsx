import * as React from "react"
import { MoreVertical, Trash2 } from "lucide-react"

import { ConfirmDialog } from "@/components/confirm-dialog"
import { Button } from "@/components/ui/button"
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from "@/components/ui/context-menu"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

type MenuItemProps = {
  variant?: "default" | "destructive"
  onClick?: () => void
  children?: React.ReactNode
}

type PaperAction = {
  label: string
  icon: React.ComponentType<{ className?: string }>
  variant?: "default" | "destructive"
  onSelect: () => void
}

function PaperMenuItems({
  Item,
  actions,
}: {
  Item: React.ComponentType<MenuItemProps>
  actions: PaperAction[]
}) {
  return actions.map((action) => (
    <Item key={action.label} variant={action.variant} onClick={action.onSelect}>
      <action.icon />
      {action.label}
    </Item>
  ))
}

type QuestionPaperActionsMenuProps = {
  title: string
  onDelete: () => void | Promise<void>
  children: React.ReactNode
}

export function QuestionPaperActionsMenu({
  title,
  onDelete,
  children,
}: QuestionPaperActionsMenuProps) {
  const [confirmOpen, setConfirmOpen] = React.useState(false)

  const actions: PaperAction[] = [
    {
      label: "Delete",
      icon: Trash2,
      variant: "destructive",
      onSelect: () => setConfirmOpen(true),
    },
  ]

  return (
    <>
      <ContextMenu>
        <ContextMenuTrigger className="group/paper flex w-full items-center rounded-lg hover:bg-muted">
          <div className="min-w-0 flex-1">{children}</div>
          <DropdownMenu>
            <DropdownMenuTrigger
              render={
                <Button
                  type="button"
                  variant="ghost"
                  size="icon-xs"
                  className="mr-1 shrink-0 text-muted-foreground hover:bg-transparent hover:text-foreground group-hover/paper:text-foreground"
                  aria-label={`Actions for ${title}`}
                />
              }
            >
              <MoreVertical className="size-3.5" />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="min-w-36">
              <PaperMenuItems Item={DropdownMenuItem} actions={actions} />
            </DropdownMenuContent>
          </DropdownMenu>
        </ContextMenuTrigger>
        <ContextMenuContent className="min-w-36">
          <PaperMenuItems Item={ContextMenuItem} actions={actions} />
        </ContextMenuContent>
      </ContextMenu>

      <ConfirmDialog
        open={confirmOpen}
        onOpenChange={setConfirmOpen}
        title="Delete question paper?"
        description={`This will delete “${title}”.`}
        confirmLabel="Delete"
        confirmVariant="destructive"
        onConfirm={onDelete}
      />
    </>
  )
}
