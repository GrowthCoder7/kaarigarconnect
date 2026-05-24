import axios from "axios"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"

export const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { "Content-Type": "application/json" },
})

export const WS_BASE = API_BASE.replace("http", "ws")

// Form fill job
export async function startFormFill(payload: {
  artisan_id: string
  scheme_id: string
  profile: Record<string, unknown>
  demo_mode?: boolean
}) {
  const { data } = await api.post("/automate/start", payload)
  return data as { job_id: string; ws_channel: string; status: string }
}

// Catalogue job
export async function startCatalogue(
  file: File,
  artisan_id: string,
  artisan_profile: Record<string, unknown>,
  material_cost = 0,
  hours_spent = 0
) {
  const form = new FormData()
  form.append("file", file)
  form.append("artisan_id", artisan_id)
  form.append("artisan_profile", JSON.stringify(artisan_profile))
  form.append("material_cost", String(material_cost))
  form.append("hours_spent", String(hours_spent))

  const { data } = await api.post("/automate/catalogue/start", form, {
    headers: { "Content-Type": "multipart/form-data" },
  })
  return data.data as { job_id: string; ws_channel: string }
}

// OCR
export async function runOCR(file: File, doc_type = "aadhaar") {
  const form = new FormData()
  form.append("file", file)
  form.append("doc_type", doc_type)
  const { data } = await api.post("/automate/ocr", form, {
    headers: { "Content-Type": "multipart/form-data" },
  })
  return data.data as { extracted: Record<string, unknown>; flat: Record<string, string> }
}