"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Home, Search, LayoutDashboard, Menu, X } from "lucide-react"

const links = [
  { href: "/dashboard", label: "My Store",    icon: Home          },
  { href: "/discover",  label: "Marketplace", icon: Search        },
  { href: "/admin",     label: "Admin",        icon: LayoutDashboard },
]

export function Nav() {
  const path = usePathname()
  const [open, setOpen] = useState(false)

  return (
    <>
      {/* Desktop top nav */}
      <nav className="hidden sm:flex items-center justify-between px-6 py-3 
                      bg-white border-b border-gray-200 sticky top-0 z-40">
        <Link href="/dashboard" className="font-bold text-emerald-600 text-lg">
          🧵 KaarigarConnect
        </Link>
        <div className="flex items-center gap-1">
          {links.map(l => (
            <Link
              key={l.href}
              href={l.href}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm 
                          font-medium transition-colors ${
                path.startsWith(l.href)
                  ? "bg-emerald-50 text-emerald-700"
                  : "text-gray-500 hover:text-gray-900"
              }`}
            >
              <l.icon className="w-4 h-4" />
              {l.label}
            </Link>
          ))}
        </div>
      </nav>

      {/* Mobile bottom nav */}
      <nav className="sm:hidden fixed bottom-0 left-0 right-0 bg-white border-t 
                      border-gray-200 z-40 flex">
        {links.map(l => (
          <Link
            key={l.href}
            href={l.href}
            className={`flex-1 flex flex-col items-center gap-0.5 py-3 text-xs 
                        font-medium transition-colors ${
              path.startsWith(l.href)
                ? "text-emerald-600"
                : "text-gray-400"
            }`}
          >
            <l.icon className="w-5 h-5" />
            {l.label}
          </Link>
        ))}
      </nav>
    </>
  )
}