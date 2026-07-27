import type { Metadata } from "next"
import { DM_Sans, IBM_Plex_Mono } from "next/font/google"
import "maplibre-gl/dist/maplibre-gl.css"
import "./globals.css"

const dmSans = DM_Sans({
  variable: "--font-sans",
  subsets: ["latin"],
})

const plexMono = IBM_Plex_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
})

export const metadata: Metadata = {
  title: "WhoFixesThis | Temporal civic service routing",
  description:
    "An offline-first research prototype for evidence-based civic issue routing, duplicate detection, and calibrated abstention.",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`${dmSans.variable} ${plexMono.variable}`}>{children}</body>
    </html>
  )
}
