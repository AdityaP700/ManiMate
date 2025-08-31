"use client"
import { useEffect, useMemo, useRef, useState } from "react"
import { Sidebar } from "./sidebar"
import { ChatMessage } from "./chat-message"
import { ChatInput } from "./chat-input"
import { colors } from "./colors"
import type { ChatItem, Message } from "./types"

type Props = {
  chatId: string
  title?: string
}

function makeAiReply(userText: string): string {
  // placeholder AI response
  return `You said: "${userText}". This is a placeholder AI reply.`
}

export function ChatShell({ chatId, title = "New Chat" }: Props) {
  // In a real app, chats/messages would come from a backend. For now, basic in-memory examples.
  const [chats] = useState<ChatItem[]>([
    { id: "welcome", title: "Welcome", updatedAt: Date.now() - 1000 * 60 * 10 },
    { id: chatId, title, updatedAt: Date.now() - 1000 * 30 },
  ])

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "m1",
      role: "ai",
      content: "Hello! Ask me anything.",
      createdAt: Date.now() - 20000,
    },
  ])

  const feedRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    // auto-scroll to bottom on new messages
    feedRef.current?.scrollTo({ top: feedRef.current.scrollHeight, behavior: "smooth" })
  }, [messages.length])

  const headerTitle = useMemo(() => title || "Chat", [title])

  function handleSend(text: string) {
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      createdAt: Date.now(),
    }
    setMessages((prev) => [...prev, userMsg])

    // very subtle delayed AI reply to mimic processing
    setTimeout(() => {
      const aiMsg: Message = {
        id: crypto.randomUUID(),
        role: "ai",
        content: makeAiReply(text),
        createdAt: Date.now(),
      }
      setMessages((prev) => [...prev, aiMsg])
    }, 400)
  }

  return (
    <div className="flex h-screen w-full" style={{ backgroundColor: colors.background, color: colors.primaryText }}>
      <Sidebar chats={chats.map((c) => ({ id: c.id, title: c.title }))} activeId={chatId} />

      <main className="flex min-w-0 flex-1 flex-col">
        <header className="border-b px-6 py-4" style={{ borderColor: colors.border }}>
          <h1 className="text-balance text-lg font-semibold" style={{ color: colors.primaryText }}>
            {headerTitle}
          </h1>
        </header>

        <div
          ref={feedRef}
          className="flex-1 overflow-y-auto px-6 py-6"
          style={{ scrollBehavior: "smooth" }}
          aria-label="Chat messages"
        >
          <div className="mx-auto flex max-w-3xl flex-col gap-3">
            {messages.map((m) => (
              <ChatMessage key={m.id} msg={m} />
            ))}
          </div>
        </div>

        <div className="px-6">
          <div className="mx-auto max-w-3xl">
            <ChatInput onSend={handleSend} />
          </div>
        </div>
      </main>
    </div>
  )
}
