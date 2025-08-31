"use client"

import { useRouter } from "next/navigation"
import { colors } from "@/components/colors"

export default function LandingPage() {
  const router = useRouter()

  function startChat() {
    const id = Math.random().toString(36).slice(2, 10)
    router.push(`/chat/${id}`)
  }

  return (
    <main
      className="flex min-h-screen flex-col items-center justify-center px-6"
      style={{ backgroundColor: colors.background, color: colors.primaryText }}
    >
      <div className="mx-auto w-full max-w-xl text-center">
        <h1 className="mb-2 text-balance text-xl font-bold" style={{ color: colors.primaryText }}>
          Minimal AI Chat
        </h1>
        <p className="mb-6 text-sm" style={{ color: colors.secondaryText }}>
          A modern, professional chat interface. Start a conversation below.
        </p>
        <button
          onClick={startChat}
          className="rounded-md px-5 py-3 text-sm font-medium transition-colors"
          style={{ backgroundColor: colors.button, color: colors.primaryText }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = colors.buttonHover)}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = colors.button)}
          aria-label="Start a new chat"
        >
          Start a chat
        </button>
      </div>
    </main>
  )
}
