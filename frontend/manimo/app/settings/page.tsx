"use client"

import Link from "next/link"
import { colors } from "@/components/colors"

export default function SettingsPage() {
  return (
    <div
      className="flex min-h-screen w-full flex-col"
      style={{ backgroundColor: colors.background, color: colors.primaryText }}
    >
      <header className="border-b px-6 py-4" style={{ borderColor: colors.border }}>
        <h1 className="text-lg font-semibold">Settings</h1>
      </header>

      <main className="mx-auto w-full max-w-3xl flex-1 px-6 py-6">
        <section className="mb-6">
          <h2 className="mb-2 text-base font-semibold">Theme</h2>
          <div
            className="rounded-md border p-4 text-sm"
            style={{ borderColor: colors.border, backgroundColor: colors.aiBubble }}
          >
            Dark mode is enabled by default for this app.
          </div>
        </section>

        <section className="mb-6">
          <h2 className="mb-2 text-base font-semibold">Account</h2>
          <div
            className="rounded-md border p-4 text-sm"
            style={{ borderColor: colors.border, backgroundColor: colors.aiBubble }}
          >
            Placeholder account options. Connect authentication to manage profile settings.
          </div>
        </section>

        <div className="mt-8">
          <Link
            href="/"
            className="rounded-md px-4 py-2 text-sm font-medium transition-colors"
            style={{ backgroundColor: colors.button, color: colors.primaryText }}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = colors.buttonHover)}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = colors.button)}
          >
            Back to Home
          </Link>
        </div>
      </main>
    </div>
  )
}
