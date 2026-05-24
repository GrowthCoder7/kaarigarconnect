"use client"

import { useState, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Upload, Loader2, Sparkles, Tag, IndianRupee, AlertCircle } from "lucide-react"
import { useCatalogueStream } from "@/hooks/useCatalogueStream"
import { startCatalogue } from "@/lib/api"
import { ProductListing } from "@/types/events"

interface CatalogueScreenProps {
  artisanId: string
  artisanProfile: Record<string, unknown>
  onListingReady?: (listing: ProductListing) => void
}

export function CatalogueScreen({
  artisanId,
  artisanProfile,
  onListingReady,
}: CatalogueScreenProps) {
  const [jobId, setJobId]           = useState<string | null>(null)
  const [preview, setPreview]       = useState<string | null>(null)
  const [uploading, setUploading]   = useState(false)
  const [materialCost, setMaterialCost] = useState("")
  const [hoursSpent, setHoursSpent] = useState("")
  const fileRef = useRef<HTMLInputElement>(null)
  const selectedFile = useRef<File | null>(null)

  const {
    craftType, title, description,
    pricing, listing,
    isAnalysing, isComplete, isError,
  } = useCatalogueStream(jobId)

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    selectedFile.current = file
    setPreview(URL.createObjectURL(file))
  }

  async function handleUpload() {
    if (!selectedFile.current) return
    setUploading(true)
    try {
      const res = await startCatalogue(
        selectedFile.current,
        artisanId,
        artisanProfile,
        parseFloat(materialCost) || 0,
        parseFloat(hoursSpent) || 0
      )
      setJobId(res.job_id)
    } catch {
      alert("Upload failed. Is the backend running?")
    } finally {
      setUploading(false)
    }
  }

  // ── Upload form ───────────────────────────────────────────────────
  if (!jobId) {
    return (
      <div className="w-full max-w-lg mx-auto p-6 space-y-5">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-900">List Your Product</h2>
          <p className="text-sm text-gray-500 mt-1">
            Photo your craft — AI builds the listing in seconds
          </p>
        </div>

        {/* Drop zone */}
        <div
          onClick={() => fileRef.current?.click()}
          className="border-2 border-dashed border-gray-300 hover:border-emerald-400 
                     rounded-xl p-8 text-center cursor-pointer transition-colors"
        >
          {preview ? (
            <img src={preview} alt="Product" className="max-h-48 mx-auto rounded-lg object-cover" />
          ) : (
            <div className="flex flex-col items-center gap-2 text-gray-400">
              <Upload className="w-8 h-8" />
              <span className="text-sm">Tap to photograph your product</span>
            </div>
          )}
          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={handleFileChange}
          />
        </div>

        {/* Optional inputs */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-gray-500 mb-1 block">Material cost (₹)</label>
            <input
              type="number"
              placeholder="e.g. 500"
              value={materialCost}
              onChange={e => setMaterialCost(e.target.value)}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="text-xs text-gray-500 mb-1 block">Hours spent</label>
            <input
              type="number"
              placeholder="e.g. 8"
              value={hoursSpent}
              onChange={e => setHoursSpent(e.target.value)}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
            />
          </div>
        </div>

        <button
          onClick={handleUpload}
          disabled={!preview || uploading}
          className="w-full flex items-center justify-center gap-2 bg-emerald-600 
                     hover:bg-emerald-700 text-white py-3 rounded-xl font-medium 
                     transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {uploading
            ? <><Loader2 className="w-4 h-4 animate-spin" /> Uploading...</>
            : <><Sparkles className="w-4 h-4" /> Analyse with AI</>
          }
        </button>
      </div>
    )
  }

  // ── Streaming results ─────────────────────────────────────────────
  return (
    <div className="w-full max-w-2xl mx-auto p-6 space-y-4">

      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">AI Cataloguing</h2>
        {isAnalysing && (
          <span className="flex items-center gap-1 text-xs text-amber-600">
            <Loader2 className="w-3 h-3 animate-spin" /> Analysing image...
          </span>
        )}
      </div>

      {/* Product image thumbnail */}
      {preview && (
        <img
          src={preview}
          alt="Product"
          className="w-full h-48 object-cover rounded-xl"
        />
      )}

      {/* Streaming fields */}
      <div className="space-y-3">

        <AnimatePresence>
          {craftType && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2 text-sm"
            >
              <Tag className="w-4 h-4 text-emerald-500" />
              <span className="text-gray-500">Craft detected:</span>
              <span className="font-medium text-gray-900">{craftType}</span>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {title && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <p className="text-xs text-gray-400 mb-1">Product title</p>
              <p className="font-semibold text-gray-900 text-lg leading-snug">{title}</p>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {description && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <p className="text-xs text-gray-400 mb-1">Description</p>
              <p className="text-sm text-gray-700 leading-relaxed">{description}</p>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {pricing && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 space-y-2"
            >
              <div className="flex items-center gap-2">
                <IndianRupee className="w-4 h-4 text-emerald-600" />
                <span className="font-semibold text-emerald-800">Fair Pricing</span>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-white rounded-lg p-3 text-center">
                  <p className="text-xs text-gray-400">B2C Price</p>
                  <p className="text-xl font-bold text-gray-900">
                    ₹{listing?.b2c_price?.toLocaleString() ?? "—"}
                  </p>
                </div>
                <div className="bg-white rounded-lg p-3 text-center">
                  <p className="text-xs text-gray-400">B2B Price</p>
                  <p className="text-xl font-bold text-gray-900">
                    ₹{listing?.b2b_price?.toLocaleString() ?? "—"}
                  </p>
                </div>
              </div>
              {pricing.was_underpriced && (
                <p className="text-xs text-emerald-700 font-medium">
                  ↑ {pricing.price_increase_percent}% above middleman price —
                  fair value for your work
                </p>
              )}
              <p className="text-xs text-gray-400">{pricing.calculation}</p>
            </motion.div>
          )}
        </AnimatePresence>

      </div>

      {/* Complete */}
      <AnimatePresence>
        {isComplete && listing && (
          <motion.div
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col gap-3"
          >
            {listing.gi_tag && (
              <div className="flex items-center gap-2 bg-amber-50 border 
                              border-amber-200 rounded-lg px-4 py-2 text-sm">
                <span>🏛️</span>
                <span className="font-medium text-amber-800">
                  GI Verified — {listing.gi_tag.name}
                </span>
              </div>
            )}
            <button
              onClick={() => onListingReady?.(listing)}
              className="w-full bg-emerald-600 hover:bg-emerald-700 text-white 
                         py-3 rounded-xl font-medium transition-colors"
            >
              Publish Listing →
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {isError && (
        <div className="flex items-center gap-3 bg-red-50 border border-red-200 
                        rounded-lg px-4 py-3 text-sm text-red-700">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>Analysis failed. Using demo data.</span>
        </div>
      )}
    </div>
  )
}