// src/api/devices.js
import { api } from "./client"

export async function getDevicesApi() {
  const res = await api.get("/devices-db")
  return res.data
}

export async function createDeviceApi({ name, type, zoneId }) {
  const res = await api.post("/devices-db", {
    name,
    type,
    status: "off",
    zone_id: Number(zoneId),
  })
  return res.data
}

export async function deleteDeviceApi(id) {
  await api.delete(`/devices-db/${id}`)
}
