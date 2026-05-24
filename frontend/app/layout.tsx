import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { Nav } from "@/components/shared/Nav"

<head>
<link
  rel="stylesheet"
  href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
/>
</head>

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "KaarigarConnect",
  description: "The operating system for India's women artisans",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
        />
      </head>
      <body className={`${inter.className} pb-16 sm:pb-0`}>
        <Nav />
        {children}
      </body>
    </html>
  )
}