"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { CheckCircle, Loader2, AlertCircle, FileText } from "lucide-react"
import { usePlaywrightStream } from "@/hooks/usePlaywrightStream"
import { startFormFill } from "@/lib/api"

interface FormFillScreenProps {
  artisanId: string
  profile: Record<string, unknown>
  schemeId?: string
  onComplete?: (certificateUrl: string | null) => void
}

export function FormFillScreen({
  artisanId,
  profile,
  schemeId = "udyam",
  onComplete,
}: FormFillScreenProps) {
  const [jobId, setJobId] = useState<string | null>(null)
  const [starting, setStarting] = useState(false)

  const {
    filledFields,
    currentField,
    isComplete,
    isError,
    certificateUrl,
    progress,
  } = usePlaywrightStream(jobId)

  async function handleStart() {
    setStarting(true)
    try {
      const res = await startFormFill({
        artisan_id: artisanId,
        scheme_id: schemeId,
        profile,
        demo_mode: true,
      })
      setJobId(res.job_id)
    } catch {
      alert("Failed to start. Is the backend running?")
    } finally {
      setStarting(false)
    }
  }

  // ── Not started yet ───────────────────────────────────────────────
  if (!jobId) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-6 p-8">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">
            Register Your Business
          </h2>
          <p className="text-gray-500 text-sm max-w-sm">
            Our AI agent will automatically fill your Udyam registration form
            using your profile details.
          </p>
        </div>
        <button
          onClick={handleStart}
          disabled={starting}
          className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 
                     text-white px-8 py-3 rounded-xl font-medium transition-all
                     disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {starting ? (
            <><Loader2 className="w-4 h-4 animate-spin" /> Preparing agent...</>
          ) : (
            <><FileText className="w-4 h-4" /> Start Auto-Registration</>
          )}
        </button>
      </div>
    )
  }

  // ── Running / Complete ────────────────────────────────────────────
  return (
    <div className="w-full max-w-2xl mx-auto p-6 space-y-6">

      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">
          Udyam Registration
        </h2>
        <span className="text-sm text-gray-400">{progress}%</span>
      </div>

      {/* Progress bar */}
      <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-emerald-500 rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.4, ease: "easeOut" }}
        />
      </div>

      {/* Current action */}
      <AnimatePresence mode="wait">
        {currentField && !isComplete && (
          <motion.div
            key={currentField}
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            className="flex items-center gap-3 text-sm text-emerald-700 
                       bg-emerald-50 border border-emerald-200 rounded-lg px-4 py-3"
          >
            <Loader2 className="w-4 h-4 animate-spin flex-shrink-0" />
            <span>Filling <strong>{currentField}</strong>...</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Filled fields list */}
      <div className="space-y-2">
        <AnimatePresence>
          {filledFields.map((f, i) => (
            <motion.div
              key={f.field}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.03 }}
              className="flex items-center justify-between bg-white border 
                         border-gray-100 rounded-lg px-4 py-3 shadow-sm"
            >
              <div className="flex items-center gap-3">
                <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                <span className="text-sm text-gray-500">{f.label}</span>
              </div>
              <span className="text-sm font-medium text-gray-900 truncate max-w-[200px]">
                {f.value}
              </span>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Complete state */}
      <AnimatePresence>
        {isComplete && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center gap-4 bg-emerald-50 
                       border border-emerald-200 rounded-xl p-8 text-center"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200, delay: 0.1 }}
            >
              <CheckCircle className="w-14 h-14 text-emerald-500" />
            </motion.div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                Registration Submitted!
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                Udyam Number: <strong>UDYAM-MP-12-0012345</strong>
              </p>
            </div>
            
            {certificateUrl && (<a
                href={certificateUrl}
                className="text-sm text-emerald-600 underline"
              >
                Download Certificate
              </a>
            )}
            {onComplete && (
              <button
                onClick={() => onComplete(certificateUrl)}
                className="bg-emerald-600 text-white px-6 py-2 rounded-lg 
                           text-sm font-medium hover:bg-emerald-700 transition-colors"
              >
                Continue →
              </button>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error state */}
      {isError && (
        <div className="flex items-center gap-3 bg-red-50 border border-red-200 
                        rounded-lg px-4 py-3 text-sm text-red-700">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>Something went wrong. Please try again.</span>
        </div>
      )}
    </div>
  )
}