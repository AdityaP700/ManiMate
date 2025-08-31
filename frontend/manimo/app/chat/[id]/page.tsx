import { ChatShell } from "@/components/chat-shell"

type Props = {
  params: { id: string }
  searchParams: Record<string, string | string[] | undefined>
}

export default function ChatPage({ params }: Props) {
  const { id } = params
  return <ChatShell chatId={id} title={`Chat ${id.slice(0, 4)}`} />
}
