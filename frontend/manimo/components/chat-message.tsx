"use client"
import { colors } from "./colors"
import type { Message } from "./types"

export function ChatMessage({ msg }: { msg: Message }) {
  const isUser = msg.role === "user"
  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className="max-w-[75%] rounded-xl px-4 py-3 text-sm leading-relaxed shadow-sm transition-opacity"
        style={{
          backgroundColor: isUser ? colors.userBubble : colors.aiBubble,
          color: colors.primaryText,
          border: `1px solid ${colors.border}`,
          opacity: 1,
        }}
        aria-live="polite"
      >
        <p className="whitespace-pre-wrap text-pretty">{msg.content}</p>
      </div>
    </div>
  )
}
