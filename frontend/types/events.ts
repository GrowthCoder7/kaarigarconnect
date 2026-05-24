export type PlaywrightEventType =
  | "FIELD_START"
  | "FIELD_FILLED"
  | "FIELD_ERROR"
  | "PAGE_SUBMIT"
  | "COMPLETE"
  | "FATAL_ERROR"

export type CatalogueEventType =
  | "ANALYSING"
  | "CRAFT_DETECTED"
  | "TITLE_READY"
  | "DESCRIPTION_READY"
  | "PRICE_SUGGESTED"
  | "LISTING_READY"
  | "ERROR"

export interface PlaywrightEvent {
  type: PlaywrightEventType
  field?: string
  label?: string
  value?: string
  error?: string
  certificate_url?: string
  message?: string
  timestamp?: string
}

export interface CatalogueEvent {
  type: CatalogueEventType
  payload: {
    craft_type?: string
    confidence?: number
    title?: string
    description?: string
    cultural_story?: string
    b2c_price?: number
    b2b_price?: number
    insight?: {
      fair_price: number
      calculation: string
      was_underpriced: boolean
      old_price_estimate: number
      price_increase_percent: number
    }
    [key: string]: unknown
  }
  timestamp?: string
}

export interface ProductListing {
  title: string
  description: string
  cultural_story: string
  craft_type: string
  origin_region: string
  tags: string[]
  b2c_price: number
  b2b_price: number
  moq: number
  gi_tag?: { id: string; name: string; state: string } | null
  pricing_insight?: {
    fair_price: number
    calculation: string
    was_underpriced: boolean
    old_price_estimate: number
    price_increase_percent: number
  } | null
  confidence: number
  artisan_id: string
}