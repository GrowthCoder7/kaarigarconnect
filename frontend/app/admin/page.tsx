"use client"

import { useEffect, useRef } from "react"
import { motion } from "framer-motion"
import {
  BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer
} from "recharts"
import { Users, Package, TrendingUp, MapPin } from "lucide-react"
import { SEED_METRICS } from "@/lib/seedData"

const DAYS    = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
const COLORS  = ["#059669","#0891b2","#7c3aed","#db2777"]

const weekly  = SEED_METRICS.weekly_registrations.map((v, i) => ({
  day: DAYS[i], count: v
}))

export default function AdminDashboard() {
  const mapRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Leaflet loads client-side only
    if (typeof window === "undefined") return
    import("leaflet").then(L => {
      if (!mapRef.current) return
      if ((mapRef.current as any)._leaflet_id) return // already init

      const map = L.map(mapRef.current).setView([22.5, 78.9], 5)
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap"
      }).addTo(map)

      SEED_METRICS.district_pins.forEach(pin => {
        const radius = Math.sqrt(pin.count) * 4000
        L.circle([pin.lat, pin.lng], {
          radius,
          color: "#059669",
          fillColor: "#059669",
          fillOpacity: 0.35,
          weight: 1,
        }).addTo(map).bindPopup(
          `<b>${pin.name}</b><br/>${pin.count} registrations`
        )
      })
    })
  }, [])

  const metrics = [
    { label: "Total Artisans",   value: SEED_METRICS.total_artisans.toLocaleString(),   icon: Users,       color: "bg-emerald-50 text-emerald-600" },
    { label: "Verified",         value: SEED_METRICS.verified_artisans.toLocaleString(), icon: TrendingUp,  color: "bg-blue-50 text-blue-600"       },
    { label: "Products Live",    value: SEED_METRICS.total_products.toLocaleString(),    icon: Package,     color: "bg-amber-50 text-amber-600"     },
    { label: "Districts",        value: SEED_METRICS.districts_covered.toString(),       icon: MapPin,      color: "bg-purple-50 text-purple-600"   },
  ]

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-5xl mx-auto space-y-6">

        {/* Header */}
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">NGO Admin Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">
            KaarigarConnect — Live impact metrics
          </p>
        </div>

        {/* Metric cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {metrics.map((m, i) => (
            <motion.div
              key={m.label}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.07 }}
              className="bg-white rounded-2xl border border-gray-200 p-5"
            >
              <div className={`w-9 h-9 rounded-xl flex items-center justify-center mb-3 ${m.color}`}>
                <m.icon className="w-4 h-4" />
              </div>
              <p className="text-2xl font-bold text-gray-900">{m.value}</p>
              <p className="text-xs text-gray-400 mt-0.5">{m.label}</p>
            </motion.div>
          ))}
        </div>

        {/* Charts row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">

          {/* Weekly registrations */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <h2 className="text-sm font-semibold text-gray-700 mb-4">
              Weekly Registrations
            </h2>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={weekly} barSize={28}>
                <XAxis dataKey="day" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis hide />
                <Tooltip
                  contentStyle={{ borderRadius: 8, border: "none", boxShadow: "0 4px 12px rgba(0,0,0,0.1)" }}
                />
                <Bar dataKey="count" fill="#059669" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Scheme uptake */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <h2 className="text-sm font-semibold text-gray-700 mb-4">
              Scheme Uptake
            </h2>
            <div className="flex items-center gap-4">
              <ResponsiveContainer width="50%" height={180}>
                <PieChart>
                  <Pie
                    data={SEED_METRICS.scheme_uptake}
                    dataKey="count"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={70}
                    paddingAngle={3}
                  >
                    {SEED_METRICS.scheme_uptake.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-2 flex-1">
                {SEED_METRICS.scheme_uptake.map((s, i) => (
                  <div key={s.name} className="flex items-center gap-2">
                    <div
                      className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                      style={{ background: COLORS[i % COLORS.length] }}
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-gray-700 truncate">{s.name}</p>
                    </div>
                    <p className="text-xs font-semibold text-gray-900">{s.count}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* District heatmap */}
        <div className="bg-white rounded-2xl border border-gray-200 p-5">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">
            Artisan Registration Heatmap
          </h2>
          <div
            ref={mapRef}
            className="w-full rounded-xl overflow-hidden"
            style={{ height: 380 }}
          />
        </div>

      </div>
    </div>
  )
}