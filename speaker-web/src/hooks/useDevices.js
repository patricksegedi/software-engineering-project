// src/hooks/useDevices.js
import { useEffect, useState, useCallback } from "react"
import { getDevicesApi } from "../api/devices"
import { getZonesApi } from "../api/zones"

export function useDevices() {
  const [devices, setDevices] = useState([])
  const [loading, setLoading] = useState(false)

  const fetchDevices = useCallback(async () => {
    try {
      setLoading(true)

      // ✅ DB 디바이스 + zones를 같이 호출
      const [devs, zones] = await Promise.all([
        getDevicesApi(),   // /devices-db
        getZonesApi(),     // /zones
      ])

      const zoneMap = new Map(zones.map((z) => [z.id, z]))

      const enriched = devs.map((d) => {
        const z = zoneMap.get(d.zone_id)
        return {
          ...d,
          zone_display_name: z?.display_name || z?.name || "Unknown Zone",
        }
      })

      setDevices(enriched)
    } catch (err) {
      console.error("Failed to fetch devices/zones", err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchDevices()
    const id = setInterval(fetchDevices, 1500)
    return () => clearInterval(id)
  }, [fetchDevices])

  const toggleDevice = async (device) => {
    const newStatus = device.status === "on" ? "off" : "on"

    try {
      // ✅ DB 디바이스 상태 업데이트
      await fetch(`http://127.0.0.1:8000/devices-db/${device.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      })

      fetchDevices()
    } catch (err) {
      console.error("Failed to toggle device", err)
    }
  }

  return { devices, loading, toggleDevice, refetch: fetchDevices }
}
