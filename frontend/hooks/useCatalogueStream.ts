import { useEffect, useRef, useState } from "react"
import { CatalogueEvent, ProductListing } from "@/types/events"
import { WS_BASE } from "@/lib/api"

interface UseCatalogueStreamReturn {
  events: CatalogueEvent[]
  craftType: string | null
  title: string | null
  description: string | null
  pricing: CatalogueEvent["payload"]["insight"] | null
  listing: ProductListing | null
  isAnalysing: boolean
  isComplete: boolean
  isError: boolean
}

export function useCatalogueStream(jobId: string | null): UseCatalogueStreamReturn {
  const [events, setEvents]       = useState<CatalogueEvent[]>([])
  const [craftType, setCraftType] = useState<string | null>(null)
  const [title, setTitle]         = useState<string | null>(null)
  const [description, setDescription] = useState<string | null>(null)
  const [pricing, setPricing]     = useState<CatalogueEvent["payload"]["insight"] | null>(null)
  const [listing, setListing]     = useState<ProductListing | null>(null)
  const [isAnalysing, setIsAnalysing] = useState(false)
  const [isComplete, setIsComplete]   = useState(false)
  const [isError, setIsError]         = useState(false)

  useEffect(() => {
    if (!jobId) return

    const ws = new WebSocket(`${WS_BASE}/api/v1/automate/ws/catalogue/${jobId}`)

    ws.onmessage = (e) => {
      const event: CatalogueEvent = JSON.parse(e.data)
      setEvents(prev => [...prev, event])

      switch (event.type) {
        case "ANALYSING":
          setIsAnalysing(true)
          break
        case "CRAFT_DETECTED":
          setCraftType(event.payload.craft_type || null)
          setIsAnalysing(false)
          break
        case "TITLE_READY":
          setTitle(event.payload.title || null)
          break
        case "DESCRIPTION_READY":
          setDescription(event.payload.description || null)
          break
        case "PRICE_SUGGESTED":
          setPricing(event.payload.insight || null)
          break
        case "LISTING_READY":
          setListing(event.payload as unknown as ProductListing)
          setIsComplete(true)
          break
        case "ERROR":
          setIsError(true)
          break
      }
    }

    ws.onerror = () => setIsError(true)

    return () => ws.close()
  }, [jobId])

  return { events, craftType, title, description, pricing, listing, isAnalysing, isComplete, isError }
}