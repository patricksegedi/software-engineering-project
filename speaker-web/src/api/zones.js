// src/api/zones.js
import { api } from "./client"

export async function getZonesApi() {
  const res = await api.get("/zones")
  return res.data
}

export async function createZoneApi({ name }) {
  const res = await api.post("/zones", {
    name,
    display_name: name,
    order_index: 0,
  })
  return res.data
}

export async function deleteZoneApi(id) {
  await api.delete(`/zones/${id}`)
}
