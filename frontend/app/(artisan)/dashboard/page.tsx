"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { FileText, Package, CheckCircle, ChevronRight } from "lucide-react"
import { useArtisanStore } from "@/stores/artisanStore"
import { FormFillScreen } from "@/components/automation/FormFillScreen"
import { CatalogueScreen } from "@/components/catalogue/CatalogueScreen"
import { ProductListing } from "@/types/events"

type View = "home" | "register" | "catalogue"

export default function ArtisanDashboard() {
  const { profile, isRegistered, listings, setRegistered, addListing } = useArtisanStore()
  const [view, setView] = useState<View>("home")

  if (!profile) return (
    <div className="min-h-screen flex items-center justify-center text-gray-400">
      Loading profile...
    </div>
  )

  // ── Home view ───────────────────────────────────────────────────
  if (view === "home") return (
    <div className="min-h-screen bg-gray-50 py-10 px-4">
      <div className="max-w-xl mx-auto space-y-6">

        {/* Profile card */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl border border-gray-200 p-6"
        >
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-full bg-emerald-100 flex items-center 
                            justify-center text-2xl font-bold text-emerald-700">
              {profile.full_name[0]}
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">{profile.full_name}</h1>
              <p className="text-sm text-gray-500">{profile.craft_type} · {profile.district}</p>
              {isRegistered && (
                <span className="inline-flex items-center gap-1 text-xs text-emerald-600 
                                 font-medium mt-1">
                  <CheckCircle className="w-3 h-3" /> Verified Artisan
                </span>
              )}
            </div>
          </div>
        </motion.div>

        {/* Action cards */}
        <div className="space-y-3">

          {/* Register */}
          <motion.button
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            onClick={() => setView("register")}
            className="w-full flex items-center justify-between bg-white border 
                       border-gray-200 rounded-2xl p-5 hover:border-emerald-300 
                       hover:shadow-sm transition-all text-left"
          >
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-emerald-50 rounded-xl flex items-center justify-center">
                <FileText className="w-5 h-5 text-emerald-600" />
              </div>
              <div>
                <p className="font-medium text-gray-900">Register Business</p>
                <p className="text-xs text-gray-400 mt-0.5">
                  {isRegistered ? "Udyam registered ✓" : "Auto-fill Udyam registration"}
                </p>
              </div>
            </div>
            <ChevronRight className="w-5 h-5 text-gray-300" />
          </motion.button>

          {/* Catalogue */}
          <motion.button
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            onClick={() => setView("catalogue")}
            className="w-full flex items-center justify-between bg-white border 
                       border-gray-200 rounded-2xl p-5 hover:border-emerald-300 
                       hover:shadow-sm transition-all text-left"
          >
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-amber-50 rounded-xl flex items-center justify-center">
                <Package className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <p className="font-medium text-gray-900">List a Product</p>
                <p className="text-xs text-gray-400 mt-0.5">
                  {listings.length > 0
                    ? `${listings.length} product${listings.length > 1 ? "s" : ""} listed`
                    : "Photo → AI builds your listing"}
                </p>
              </div>
            </div>
            <ChevronRight className="w-5 h-5 text-gray-300" />
          </motion.button>

        </div>

        {/* Listed products */}
        {listings.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-2"
          >
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wide px-1">
              Your listings
            </p>
            {listings.map((l, i) => (
              <div
                key={i}
                className="bg-white border border-gray-200 rounded-xl p-4 
                           flex items-center justify-between"
              >
                <div>
                  <p className="text-sm font-medium text-gray-900 truncate max-w-[240px]">
                    {l.title}
                  </p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    ₹{l.b2c_price?.toLocaleString()} · MOQ {l.moq}
                  </p>
                </div>
                {l.gi_tag && (
                  <span className="text-xs bg-amber-50 text-amber-700 
                                   border border-amber-200 rounded-full px-2 py-0.5">
                    GI ✓
                  </span>
                )}
              </div>
            ))}
          </motion.div>
        )}

      </div>
    </div>
  )

  // ── Register view ───────────────────────────────────────────────
  if (view === "register") return (
    <div className="min-h-screen bg-gray-50 py-10 px-4">
      <div className="max-w-xl mx-auto">
        <button
          onClick={() => setView("home")}
          className="text-sm text-gray-400 hover:text-gray-600 mb-6 flex items-center gap-1"
        >
          ← Back
        </button>
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm">
          <FormFillScreen
            artisanId={profile.id}
            profile={profile}
            onComplete={() => {
              setRegistered()
              setView("home")
            }}
          />
        </div>
      </div>
    </div>
  )

  // ── Catalogue view ──────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gray-50 py-10 px-4">
      <div className="max-w-xl mx-auto">
        <button
          onClick={() => setView("home")}
          className="text-sm text-gray-400 hover:text-gray-600 mb-6 flex items-center gap-1"
        >
          ← Back
        </button>
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm">
          <CatalogueScreen
            artisanId={profile.id}
            artisanProfile={profile}
            onListingReady={(listing: ProductListing) => {
              addListing(listing)
              setView("home")
            }}
          />
        </div>
      </div>
    </div>
  )
}