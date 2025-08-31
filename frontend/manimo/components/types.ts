export type Role = "user" | "ai"

export interface Message {
  id: string
  role: Role
  content: string
  createdAt: number
}

export interface ChatItem {
  id: string
  title: string
  updatedAt: number
}
