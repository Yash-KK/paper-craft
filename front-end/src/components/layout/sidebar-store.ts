import { useCallback, useSyncExternalStore } from "react"

let sidebarOpen = true
const listeners = new Set<() => void>()

function emit() {
  listeners.forEach((listener) => listener())
}

function subscribe(listener: () => void) {
  listeners.add(listener)
  return () => {
    listeners.delete(listener)
  }
}

function getSnapshot() {
  return sidebarOpen
}

export function useSidebarOpen() {
  return useSyncExternalStore(subscribe, getSnapshot, () => true)
}

export function useSidebarActions() {
  const setSidebarOpen = useCallback((open: boolean) => {
    if (sidebarOpen === open) return
    sidebarOpen = open
    emit()
  }, [])

  const closeSidebar = useCallback(() => {
    if (!sidebarOpen) return
    sidebarOpen = false
    emit()
  }, [])

  const openSidebar = useCallback(() => {
    if (sidebarOpen) return
    sidebarOpen = true
    emit()
  }, [])

  return { setSidebarOpen, closeSidebar, openSidebar }
}
