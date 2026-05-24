import { create } from "zustand"
import { ProductListing } from "@/types/events"

interface ArtisanProfile {
  id: string
  full_name: string
  business_name: string
  state: string
  district: string
  mobile: string
  craft_type: string
  [key: string]: unknown
}

interface ArtisanStore {
  profile: ArtisanProfile | null
  isRegistered: boolean
  listings: ProductListing[]
  setProfile: (p: ArtisanProfile) => void
  setRegistered: () => void
  addListing: (l: ProductListing) => void
}

// Demo profile — swap with Person A's API response later
export const DEMO_PROFILE: ArtisanProfile = {
  id: "artisan-demo-001",
  full_name: "Sunita Devi",
  business_name: "Sunita Handlooms",
  state: "Madhya Pradesh",
  district: "Chanderi",
  mobile: "9876543210",
  craft_type: "Handwoven Textiles",
}

export const useArtisanStore = create<ArtisanStore>((set) => ({
  profile: DEMO_PROFILE,   // ← swap to null when Person A's onboarding is ready
  isRegistered: false,
  listings: [],
  setProfile: (profile) => set({ profile }),
  setRegistered: () => set({ isRegistered: true }),
  addListing: (listing) => set((s) => ({ listings: [...s.listings, listing] })),
}))