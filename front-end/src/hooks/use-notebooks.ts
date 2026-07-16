import * as React from "react"

import { fetchNotebooks, type NotebookListItem } from "@/lib/api"

export function useNotebooks() {
  const [notebooks, setNotebooks] = React.useState<NotebookListItem[]>([])
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)

  const load = React.useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setNotebooks(await fetchNotebooks())
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load notebooks")
    } finally {
      setLoading(false)
    }
  }, [])

  React.useEffect(() => {
    void load()
  }, [load])

  return { notebooks, loading, error, reload: load }
}
