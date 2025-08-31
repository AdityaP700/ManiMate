"use client"
import { type FormEvent, useState } from "react"
import { colors } from "./colors"

type Props = {
  onSend: (text: string) => void
}

export function ChatInput({ onSend }: Props) {
  const [value, setValue] = useState("")

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const text = value.trim()
    if (!text) return
    onSend(text)
    setValue("")
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex w-full items-center gap-2 border-t p-4"
      style={{ borderColor: colors.border, backgroundColor: colors.background }}
      aria-label="Chat input"
    >
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Send a message…"
        className="flex-1 rounded-xl border px-4 py-3 text-sm outline-none"
        style={{
          backgroundColor: colors.inputBg,
          color: colors.inputText,
          borderColor: colors.border,
        }}
        aria-label="Message"
      />
      <button
        type="submit"
        className="rounded-md px-4 py-3 text-sm font-medium transition-colors"
        style={{
          backgroundColor: colors.button,
          color: colors.primaryText,
        }}
        onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = colors.buttonHover)}
        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = colors.button)}
        aria-label="Send message"
      >
        Send
      </button>
    </form>
  )
}
