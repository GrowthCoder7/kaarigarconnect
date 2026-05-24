import { ProductListing } from "@/types/events"

export const SEED_ARTISANS = [
  {
    id: "artisan-001",
    full_name: "Sunita Devi",
    business_name: "Sunita Handlooms",
    state: "Madhya Pradesh",
    district: "Chanderi",
    mobile: "9876543210",
    craft_type: "Handwoven Textiles",
    is_verified: true,
    udyam_number: "UDYAM-MP-12-0012345",
  },
  {
    id: "artisan-002",
    full_name: "Kamla Bai",
    business_name: "Kutch Kala",
    state: "Gujarat",
    district: "Kutch",
    mobile: "9876543211",
    craft_type: "Embroidery",
    is_verified: true,
    udyam_number: "UDYAM-GJ-08-0056789",
  },
  {
    id: "artisan-003",
    full_name: "Priya Sharma",
    business_name: "Blue Pottery Studio",
    state: "Rajasthan",
    district: "Jaipur",
    mobile: "9876543212",
    craft_type: "Blue Pottery",
    is_verified: false,
    udyam_number: null,
  },
]

export const SEED_PRODUCTS: (ProductListing & {
  id: string
  artisan_name: string
  artisan_district: string
  images: string[]
  status: "live"
})[] = [
  {
    id: "prod-001",
    artisan_id: "artisan-001",
    artisan_name: "Sunita Devi",
    artisan_district: "Chanderi, MP",
    title: "Handwoven Chanderi Silk Saree with Zari Border",
    description:
      "Exquisitely crafted by skilled artisans in Chanderi, this pure silk saree features traditional zari work passed down through generations.",
    cultural_story:
      "Chanderi weaving dates back to the 2nd century BC. The unique texture is created by interlacing silk and cotton threads on pit looms.",
    craft_type: "Handwoven Textiles",
    origin_region: "Chanderi",
    tags: ["handwoven", "silk", "chanderi", "saree", "GI-tagged"],
    b2c_price: 2400,
    b2b_price: 1920,
    moq: 5,
    gi_tag: { id: "GI-001", name: "Chanderi Fabric", state: "Madhya Pradesh" },
    pricing_insight: {
      fair_price: 2400,
      calculation: "(₹500 materials + ₹640 labour) × 2.5",
      was_underpriced: true,
      old_price_estimate: 800,
      price_increase_percent: 200,
    },
    confidence: 0.95,
    images: [
      "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=400",
    ],
    status: "live",
  },
  {
    id: "prod-002",
    artisan_id: "artisan-002",
    artisan_name: "Kamla Bai",
    artisan_district: "Kutch, GJ",
    title: "Traditional Kutch Mirror Work Embroidered Blouse Fabric",
    description:
      "Hand-stitched Kutch embroidery featuring intricate mirror work and vibrant thread patterns on cotton fabric.",
    cultural_story:
      "Kutch embroidery is a 400-year-old tradition practiced by women of the Kutch region. Each motif carries symbolic meaning.",
    craft_type: "Embroidery",
    origin_region: "Kutch",
    tags: ["kutch", "embroidery", "mirror-work", "handmade", "GI-tagged"],
    b2c_price: 1800,
    b2b_price: 1440,
    moq: 10,
    gi_tag: { id: "GI-002", name: "Kutch Embroidery", state: "Gujarat" },
    pricing_insight: {
      fair_price: 1800,
      calculation: "(₹300 materials + ₹420 labour) × 2.5",
      was_underpriced: true,
      old_price_estimate: 600,
      price_increase_percent: 200,
    },
    confidence: 0.92,
    images: [
      "https://images.unsplash.com/photo-1583391733956-6c78276477e2?w=400",
    ],
    status: "live",
  },
  {
    id: "prod-003",
    artisan_id: "artisan-003",
    artisan_name: "Priya Sharma",
    artisan_district: "Jaipur, RJ",
    title: "Hand-Painted Blue Pottery Decorative Plate Set",
    description:
      "Set of 4 hand-painted blue pottery plates featuring floral motifs in traditional Jaipur style.",
    cultural_story:
      "Jaipur Blue Pottery is a Central Asian craft brought to India in the Mughal era. It uses quartz stone powder instead of clay.",
    craft_type: "Blue Pottery",
    origin_region: "Jaipur",
    tags: ["blue-pottery", "jaipur", "handpainted", "decor", "GI-tagged"],
    b2c_price: 1200,
    b2b_price: 960,
    moq: 12,
    gi_tag: { id: "GI-003", name: "Blue Pottery of Jaipur", state: "Rajasthan" },
    pricing_insight: {
      fair_price: 1200,
      calculation: "(₹200 materials + ₹280 labour) × 2.5",
      was_underpriced: true,
      old_price_estimate: 400,
      price_increase_percent: 200,
    },
    confidence: 0.89,
    images: [
      "https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=400",
    ],
    status: "live",
  },
  {
    id: "prod-004",
    artisan_id: "artisan-001",
    artisan_name: "Sunita Devi",
    artisan_district: "Chanderi, MP",
    title: "Lightweight Chanderi Cotton Dupatta with Block Print",
    description:
      "Airy Chanderi cotton dupatta with traditional block-printed border in natural indigo dye.",
    cultural_story:
      "Block printing on Chanderi fabric combines two ancient Indian textile traditions.",
    craft_type: "Handwoven Textiles",
    origin_region: "Chanderi",
    tags: ["chanderi", "block-print", "dupatta", "cotton"],
    b2c_price: 850,
    b2b_price: 680,
    moq: 20,
    gi_tag: { id: "GI-001", name: "Chanderi Fabric", state: "Madhya Pradesh" },
    pricing_insight: null,
    confidence: 0.88,
    images: [
      "https://images.unsplash.com/photo-1594938298603-c8148c4b4c5e?w=400",
    ],
    status: "live",
  },
  {
    id: "prod-005",
    artisan_id: "artisan-002",
    artisan_name: "Kamla Bai",
    artisan_district: "Kutch, GJ",
    title: "Handmade Kutch Embroidered Cushion Cover Pair",
    description:
      "Pair of cotton cushion covers with authentic Kutch embroidery and mirror work detailing.",
    cultural_story:
      "Each cushion cover takes 3 days to embroider by hand.",
    craft_type: "Embroidery",
    origin_region: "Kutch",
    tags: ["kutch", "cushion", "home-decor", "embroidery"],
    b2c_price: 950,
    b2b_price: 760,
    moq: 15,
    gi_tag: { id: "GI-002", name: "Kutch Embroidery", state: "Gujarat" },
    pricing_insight: null,
    confidence: 0.91,
    images: [
      "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
    ],
    status: "live",
  },
]

export const SEED_METRICS = {
  total_artisans: 1247,
  verified_artisans: 893,
  total_products: 3842,
  total_orders: 512,
  schemes_accessed: 234,
  districts_covered: 47,
  weekly_registrations: [12, 19, 28, 35, 41, 38, 52],
  scheme_uptake: [
    { name: "PM Vishwakarma", count: 89 },
    { name: "Mudra Shishu",   count: 67 },
    { name: "SFURTI",         count: 45 },
    { name: "PMEGP",          count: 33 },
  ],
  district_pins: [
    { name: "Chanderi",  lat: 24.71, lng: 78.13, count: 89  },
    { name: "Kutch",     lat: 23.73, lng: 69.86, count: 134 },
    { name: "Jaipur",    lat: 26.91, lng: 75.79, count: 201 },
    { name: "Varanasi",  lat: 25.32, lng: 82.97, count: 76  },
    { name: "Mysuru",    lat: 12.29, lng: 76.63, count: 98  },
    { name: "Lucknow",   lat: 26.84, lng: 80.94, count: 112 },
    { name: "Bhuj",      lat: 23.25, lng: 69.66, count: 67  },
  ],
}