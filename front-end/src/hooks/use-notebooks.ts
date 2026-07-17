import * as React from "react"

import { fetchNotebooks, type NotebookListItem } from "@/lib/api"

type NotebooksState = {
  notebooks: NotebookListItem[]
  error: string | null
  status: "pending" | "success" | "error"
}

const INITIAL_STATE: NotebooksState = {
  notebooks: [],
  error: null,
  status: "pending",
}

export function useNotebooks() {
  const [state, setState] = React.useState<NotebooksState>(INITIAL_STATE)
  const [reloadKey, setReloadKey] = React.useState(0)

  React.useEffect(() => {
    let cancelled = false

    fetchNotebooks()
      .then((notebooks) => {
        if (cancelled) return
        setState({ notebooks, error: null, status: "success" })
      })
      .catch((err) => {
        if (cancelled) return
        setState((prev) => ({
          notebooks: prev.notebooks,
          error:
            err instanceof Error ? err.message : "Failed to load notebooks",
          status: "error",
        }))
      })

    return () => {
      cancelled = true
    }
  }, [reloadKey])

  const reload = React.useCallback(() => {
    setState((prev) => ({ ...prev, status: "pending", error: null }))
    setReloadKey((key) => key + 1)
  }, [])

  return {
    notebooks: state.notebooks,
    loading: state.status === "pending" && state.notebooks.length === 0,
    error: state.error,
    reload,
  }
}
