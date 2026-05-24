import { useEffect, useRef, useState, useCallback } from "react"
import { PlaywrightEvent } from "@/types/events"
import { WS_BASE } from "@/lib/api"

interface FilledField {
  field: string
  label: string
  value: string
}

interface UsePlaywrightStreamReturn {
  events: PlaywrightEvent[]
  filledFields: FilledField[]
  currentField: string | null
  isComplete: boolean
  isError: boolean
  certificateUrl: string | null
  progress: number   // 0-100
}

const TOTAL_FIELDS = 9  // matches FIELD_MAP in backend

export function usePlaywrightStream(jobId: string | null): UsePlaywrightStreamReturn {
  const wsRef = useRef<WebSocket | null>(null)
  const [events, setEvents]           = useState<PlaywrightEvent[]>([])
  const [filledFields, setFilledFields] = useState<FilledField[]>([])
  const [currentField, setCurrentField] = useState<string | null>(null)
  const [isComplete, setIsComplete]   = useState(false)
  const [isError, setIsError]         = useState(false)
  const [certificateUrl, setCertificateUrl] = useState<string | null>(null)
  const [progress, setProgress]       = useState(0)

  useEffect(() => {
    if (!jobId) return

    const ws = new WebSocket(`${WS_BASE}/api/v1/automate/ws/playwright/${jobId}`)
    wsRef.current = ws

    ws.onmessage = (e) => {
      const event: PlaywrightEvent = JSON.parse(e.data)
      setEvents(prev => [...prev, event])

      if (event.type === "FIELD_START") {
        setCurrentField(event.label || event.field || null)
      }

      if (event.type === "FIELD_FILLED" && event.field && event.label && event.value) {
        setFilledFields(prev => {
          const updated = [...prev, {
            field: event.field!,
            label: event.label!,
            value: event.value!
          }]
          setProgress(Math.round((updated.length / TOTAL_FIELDS) * 90))
          return updated
        })
        setCurrentField(null)
      }

      if (event.type === "PAGE_SUBMIT") {
        setProgress(95)
        setCurrentField("Submitting application...")
      }

      if (event.type === "COMPLETE") {
        setProgress(100)
        setIsComplete(true)
        setCurrentField(null)
        setCertificateUrl(event.certificate_url || null)
      }

      if (event.type === "FATAL_ERROR") {
        setIsError(true)
        setCurrentField(null)
      }
    }

    ws.onerror = () => setIsError(true)

    return () => ws.close()
  }, [jobId])

  return { events, filledFields, currentField, isComplete, isError, certificateUrl, progress }
}