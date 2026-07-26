import { Check, ChevronDown, Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Label } from "@/components/ui/label"

type MenuSelectProps<T extends string | number> = {
  label: string
  value: T | ""
  placeholder: string
  disabled?: boolean
  loading?: boolean
  options: { value: T; label: string }[]
  onChange: (value: T) => void
  className?: string
}

export function MenuSelect<T extends string | number>({
  label,
  value,
  placeholder,
  disabled,
  loading,
  options,
  onChange,
  className = "h-10 w-full justify-between font-normal",
}: MenuSelectProps<T>) {
  const selected = options.find((option) => option.value === value)

  return (
    <div className="grid gap-2">
      <Label>{label}</Label>
      <DropdownMenu>
        <DropdownMenuTrigger
          disabled={disabled || loading}
          render={<Button variant="outline" className={className} />}
        >
          <span className="truncate">
            {loading ? "Loading…" : (selected?.label ?? placeholder)}
          </span>
          {loading ? (
            <Loader2 className="size-4 shrink-0 animate-spin opacity-50" />
          ) : (
            <ChevronDown className="size-4 shrink-0 opacity-50" />
          )}
        </DropdownMenuTrigger>
        <DropdownMenuContent className="z-100 max-h-60 w-(--anchor-width)">
          {options.length === 0 ? (
            <DropdownMenuItem disabled>No options available</DropdownMenuItem>
          ) : (
            options.map((option) => (
              <DropdownMenuItem
                key={String(option.value)}
                onClick={() => onChange(option.value)}
              >
                {option.label}
                {value === option.value ? (
                  <Check className="ml-auto size-4" />
                ) : null}
              </DropdownMenuItem>
            ))
          )}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}
