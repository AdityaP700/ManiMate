"use client"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { useMemo } from "react"
import { colors } from "./colors"

type Props = {
  chats: { id: string; title: string }[]
  activeId?: string
}

export function Sidebar({ chats, activeId }: Props) {
  const router = useRouter()
  const pathname = usePathname()

  const isSettings = useMemo(() => pathname?.startsWith("/settings"), [pathname])

  function onNewChat() {
    const id = Math.random().toString(36).slice(2, 10)
    router.push(`/chat/${id}`)
  }

  return (
    <aside
      className="flex h-screen min-w-[280px] max-w-[280px] flex-col border-r"
      style={{ backgroundColor: colors.sidebarBg, borderColor: colors.border }}
      aria-label="Sidebar"
    >
      <div className="p-4">
        <button
          onClick={onNewChat}
          className="w-full rounded-md px-4 py-2 text-sm font-medium transition-colors"
          style={{
            backgroundColor: colors.button,
            color: colors.primaryText,
          }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = colors.buttonHover)}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = colors.button)}
          aria-label="Start a new chat"
        >
          New Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2">
        <ul className="space-y-1" aria-label="Chat history">
          {chats.length === 0 ? (
            <li className="px-2 py-2 text-sm" style={{ color: colors.secondaryText }}>
              No chats yet
            </li>
          ) : (
            chats.map((c) => {
              const active = c.id === activeId
              return (
                <li key={c.id}>
                  <Link
                    href={`/chat/${c.id}`}
                    className="block rounded-md px-3 py-2 text-sm transition-colors"
                    style={{
                      color: colors.primaryText,
                      backgroundColor: active ? colors.sidebarHover : "transparent",
                    }}
                    onMouseEnter={(e) => {
                      if (!active) e.currentTarget.style.backgroundColor = colors.sidebarHover
                    }}
                    onMouseLeave={(e) => {
                      if (!active) e.currentTarget.style.backgroundColor = "transparent"
                    }}
                  >
                    {c.title}
                  </Link>
                </li>
              )
            })
          )}
        </ul>
      </div>

      <div className="border-t p-4" style={{ borderColor: colors.border }}>
        <Link
          href="/settings"
          className="block rounded-md px-3 py-2 text-sm transition-colors"
          style={{
            color: isSettings ? colors.primaryText : colors.secondaryText,
            backgroundColor: isSettings ? colors.sidebarHover : "transparent",
          }}
          onMouseEnter={(e) => {
            if (!isSettings) e.currentTarget.style.backgroundColor = colors.sidebarHover
          }}
          onMouseLeave={(e) => {
            if (!isSettings) e.currentTarget.style.backgroundColor = "transparent"
          }}
        >
          Settings
        </Link>
      </div>
    </aside>
  )
}
