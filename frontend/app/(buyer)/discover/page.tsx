"use client"

import { useState, useMemo } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Search, SlidersHorizontal, ShoppingBag, Building2, X } from "lucide-react"
import { SEED_PRODUCTS } from "@/lib/seedData"

const CRAFT_FILTERS = ["All", "Handwoven Textiles", "Embroidery", "Blue Pottery"]
const TYPE_FILTERS  = [
  { label: "All",  value: "all"  },
  { label: "B2C",  value: "b2c"  },
  { label: "Bulk", value: "b2b"  },
]

export default function DiscoverPage() {
  const [search, setSearch]         = useState("")
  const [craft, setCraft]           = useState("All")
  const [type, setType]             = useState("all")
  const [enquiryProduct, setEnquiry] = useState<typeof SEED_PRODUCTS[0] | null>(null)
  const [enquirySent, setEnquirySent] = useState(false)

  const filtered = useMemo(() => {
    return SEED_PRODUCTS.filter(p => {
      const matchSearch = !search ||
        p.title.toLowerCase().includes(search.toLowerCase()) ||
        p.craft_type.toLowerCase().includes(search.toLowerCase()) ||
        p.artisan_district.toLowerCase().includes(search.toLowerCase())
      const matchCraft  = craft === "All" || p.craft_type === craft
      return matchSearch && matchCraft
    })
  }, [search, craft, type])

  return (
    <div className="min-h-screen bg-gray-50">

      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-4 space-y-3">
          <div className="flex items-center justify-between">
            <h1 className="text-lg font-semibold text-gray-900">
              🧵 KaarigarConnect
            </h1>
            <span className="text-xs text-gray-400">{filtered.length} products</span>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search craft, district, artisan..."
              className="w-full pl-9 pr-4 py-2.5 border border-gray-200 rounded-xl 
                         text-sm focus:outline-none focus:border-emerald-400"
            />
          </div>

          {/* Filters */}
          <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
            {CRAFT_FILTERS.map(f => (
              <button
                key={f}
                onClick={() => setCraft(f)}
                className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium 
                            transition-colors ${
                  craft === f
                    ? "bg-emerald-600 text-white"
                    : "bg-white border border-gray-200 text-gray-600"
                }`}
              >
                {f}
              </button>
            ))}
            <div className="w-px bg-gray-200 mx-1" />
            {TYPE_FILTERS.map(f => (
              <button
                key={f.value}
                onClick={() => setType(f.value)}
                className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium 
                            transition-colors ${
                  type === f.value
                    ? "bg-gray-900 text-white"
                    : "bg-white border border-gray-200 text-gray-600"
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Product grid */}
      <div className="max-w-5xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <AnimatePresence>
            {filtered.map((product, i) => (
              <motion.div
                key={product.id}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="bg-white rounded-2xl border border-gray-200 
                           overflow-hidden hover:shadow-md transition-shadow"
              >
                {/* Image */}
                <div className="relative h-48 bg-gray-100">
                  <img
                    src={product.images[0]}
                    alt={product.title}
                    className="w-full h-full object-cover"
                  />
                  {product.gi_tag && (
                    <span className="absolute top-2 right-2 bg-amber-400 text-amber-900 
                                     text-xs font-semibold px-2 py-0.5 rounded-full">
                      GI ✓
                    </span>
                  )}
                </div>

                {/* Content */}
                <div className="p-4 space-y-3">
                  <div>
                    <p className="text-xs text-gray-400">{product.artisan_district}</p>
                    <h3 className="text-sm font-semibold text-gray-900 leading-snug mt-0.5 
                                   line-clamp-2">
                      {product.title}
                    </h3>
                  </div>

                  <p className="text-xs text-gray-500 line-clamp-2">
                    {product.cultural_story}
                  </p>

                  {/* Prices */}
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs text-gray-400">B2C</p>
                      <p className="text-base font-bold text-gray-900">
                        ₹{product.b2c_price.toLocaleString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-400">Bulk (MOQ {product.moq})</p>
                      <p className="text-base font-bold text-emerald-600">
                        ₹{product.b2b_price.toLocaleString()}
                      </p>
                    </div>
                  </div>

                  {/* Artisan + underpricing insight */}
                  {product.pricing_insight?.was_underpriced && (
                    <p className="text-xs text-emerald-600 bg-emerald-50 
                                  rounded-lg px-2 py-1">
                      ↑ {product.pricing_insight.price_increase_percent}% above 
                      middleman price — direct from artisan
                    </p>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2 pt-1">
                    <button className="flex-1 flex items-center justify-center gap-1.5 
                                       bg-gray-900 text-white text-xs font-medium py-2 
                                       rounded-lg hover:bg-gray-800 transition-colors">
                      <ShoppingBag className="w-3.5 h-3.5" /> Buy Now
                    </button>
                    <button
                      onClick={() => { setEnquiry(product); setEnquirySent(false) }}
                      className="flex-1 flex items-center justify-center gap-1.5 
                                 border border-emerald-600 text-emerald-600 text-xs 
                                 font-medium py-2 rounded-lg hover:bg-emerald-50 
                                 transition-colors"
                    >
                      <Building2 className="w-3.5 h-3.5" /> Bulk Enquiry
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {filtered.length === 0 && (
          <div className="text-center py-20 text-gray-400">
            <p className="text-lg">No products found</p>
            <p className="text-sm mt-1">Try a different filter</p>
          </div>
        )}
      </div>

      {/* B2B Enquiry modal */}
      <AnimatePresence>
        {enquiryProduct && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50 flex items-end sm:items-center 
                       justify-center p-4"
            onClick={() => setEnquiry(null)}
          >
            <motion.div
              initial={{ y: 40, opacity: 0 }}
              animate={{ y: 0,  opacity: 1 }}
              exit={{ y: 40,    opacity: 0 }}
              onClick={e => e.stopPropagation()}
              className="bg-white rounded-2xl w-full max-w-md p-6 space-y-4"
            >
              {!enquirySent ? (
                <>
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900">Bulk Enquiry</h3>
                      <p className="text-xs text-gray-400 mt-0.5 line-clamp-1">
                        {enquiryProduct.title}
                      </p>
                    </div>
                    <button onClick={() => setEnquiry(null)}>
                      <X className="w-5 h-5 text-gray-400" />
                    </button>
                  </div>

                  <div className="bg-gray-50 rounded-xl p-3 grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <p className="text-xs text-gray-400">B2B Price</p>
                      <p className="font-bold">₹{enquiryProduct.b2b_price.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-400">Min. Order</p>
                      <p className="font-bold">{enquiryProduct.moq} units</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-400">Artisan</p>
                      <p className="font-medium">{enquiryProduct.artisan_name}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-400">District</p>
                      <p className="font-medium">{enquiryProduct.artisan_district}</p>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <input
                      placeholder="Your name / company"
                      className="w-full border border-gray-200 rounded-xl px-3 
                                 py-2.5 text-sm focus:outline-none focus:border-emerald-400"
                    />
                    <input
                      placeholder="Quantity required"
                      type="number"
                      className="w-full border border-gray-200 rounded-xl px-3 
                                 py-2.5 text-sm focus:outline-none focus:border-emerald-400"
                    />
                    <textarea
                      placeholder="Any customisation or additional details..."
                      rows={3}
                      className="w-full border border-gray-200 rounded-xl px-3 
                                 py-2.5 text-sm focus:outline-none focus:border-emerald-400 
                                 resize-none"
                    />
                  </div>

                  <button
                    onClick={() => setEnquirySent(true)}
                    className="w-full bg-emerald-600 hover:bg-emerald-700 text-white 
                               py-3 rounded-xl font-medium text-sm transition-colors"
                  >
                    Send Enquiry via Telegram →
                  </button>
                </>
              ) : (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1  }}
                  className="text-center py-6 space-y-3"
                >
                  <div className="text-4xl">✅</div>
                  <h3 className="font-semibold text-gray-900">Enquiry Sent!</h3>
                  <p className="text-sm text-gray-500">
                    {enquiryProduct.artisan_name} will receive your enquiry on 
                    Telegram and respond within 24 hours.
                  </p>
                  <button
                    onClick={() => setEnquiry(null)}
                    className="text-sm text-emerald-600 font-medium"
                  >
                    Back to marketplace
                  </button>
                </motion.div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}