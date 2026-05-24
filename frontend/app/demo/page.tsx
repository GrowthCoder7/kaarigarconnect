"use client"

import { useState } from "react"
import { FormFillScreen } from "@/components/automation/FormFillScreen"
import { CatalogueScreen } from "@/components/catalogue/CatalogueScreen"
import { ProductListing } from "@/types/events"

const DEMO_PROFILE = {
  full_name: "Sunita Devi",
  business_name: "Sunita Handlooms",
  state: "Madhya Pradesh",
  district: "Chanderi",
  mobile: "9876543210",
  craft_type: "Handwoven Textiles",
}

export default function DemoPage() {
  const [tab, setTab] = useState<"register" | "catalogue">("register")
  const [listing, setListing] = useState<ProductListing | null>(null)

  return (
    <div className="min-h-screen bg-gray-50 py-10 px-4">
      <div className="max-w-2xl mx-auto">

        {/* Tabs */}
        <div className="flex gap-2 mb-8 bg-white border border-gray-200 
                        rounded-xl p-1 w-fit mx-auto">
          {(["register", "catalogue"] as const).map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-5 py-2 rounded-lg text-sm font-medium transition-colors
                ${tab === t
                  ? "bg-emerald-600 text-white"
                  : "text-gray-500 hover:text-gray-900"
                }`}
            >
              {t === "register" ? "📋 Auto-Register" : "📸 List Product"}
            </button>
          ))}
        </div>

        {/* Panels */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm">
          {tab === "register" && (
            <FormFillScreen
              artisanId="demo-artisan-001"
              profile={DEMO_PROFILE}
              onComplete={(url) => console.log("Certificate:", url)}
            />
          )}
          {tab === "catalogue" && (
            <CatalogueScreen
              artisanId="demo-artisan-001"
              artisanProfile={DEMO_PROFILE}
              onListingReady={(l) => {
                setListing(l)
                console.log("Listing ready:", l)
              }}
            />
          )}
        </div>

        {/* Listing preview */}
        {listing && (
          <div className="mt-6 bg-white rounded-2xl border border-gray-200 p-6">
            <p className="text-xs text-gray-400 mb-2">Published listing</p>
            <pre className="text-xs text-gray-600 overflow-auto">
              {JSON.stringify(listing, null, 2)}
            </pre>
          </div>
        )}

      </div>
    </div>
  )
}