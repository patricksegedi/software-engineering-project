import { useEffect, useState } from "react"
import "./DeviceManagement.css"
import { getZonesApi } from "../../api/zones"
import {
  getDevicesApi,
  createDeviceApi,
  deleteDeviceApi,
} from "../../api/devices"

const DEVICE_TYPES = [
  { value: "light", label: "Light" },
  { value: "tv", label: "TV" },
  { value: "ac", label: "Air conditioner" },
  { value: "door", label: "Door" },
]

export default function DeviceManagement() {
  const [zones, setZones] = useState([])
  const [devices, setDevices] = useState([])
  const [newName, setNewName] = useState("")
  const [newType, setNewType] = useState("light")
  const [newZoneId, setNewZoneId] = useState("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [zonesData, devicesData] = await Promise.all([
          getZonesApi(),
          getDevicesApi(),
        ])
        setZones(zonesData)
        setDevices(devicesData)
      } catch (err) {
        console.error(err)
        alert("서버에서 디바이스/존 정보를 불러오지 못했습니다.")
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const handleAddDevice = async (e) => {
    e.preventDefault()
    const trimmed = newName.trim()
    if (!trimmed || !newZoneId) return

    try {
      const created = await createDeviceApi({
        name: trimmed,
        type: newType,
        zoneId: newZoneId,
      })
      setDevices((prev) => [...prev, created])
      setNewName("")
      setNewType("light")
      setNewZoneId("")
    } catch (err) {
      console.error(err)
      alert("디바이스를 추가하는 중 오류가 발생했습니다.")
    }
  }

  const handleDeleteDevice = async (id) => {
    if (!window.confirm("이 디바이스를 삭제하시겠습니까?")) return
    try {
      await deleteDeviceApi(id)
      setDevices((prev) => prev.filter((d) => d.id !== id))
    } catch (err) {
      console.error(err)
      alert("디바이스 삭제 중 오류가 발생했습니다.")
    }
  }

  const findZoneLabel = (device) => {
    if (device.zone) {
      return device.zone.display_name || device.zone.name
    }
    const z = zones.find((z) => z.id === device.zone_id)
    return z ? z.display_name || z.name : "Unknown"
  }

  return (
    <div className="devices-container">
      <header className="devices-header">
        <h1 className="devices-title">Device management</h1>
        <p className="devices-subtitle">
          각 존에 연결된 스마트 디바이스를 등록하고 관리합니다.
        </p>
      </header>

      <section className="devices-section">
        <h2 className="devices-section-title">Add new device</h2>

        <form className="devices-form" onSubmit={handleAddDevice}>
          <input
            className="devices-input"
            type="text"
            placeholder="Device name (e.g. Living room lights)"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            required
          />

          <select
            className="devices-select"
            value={newType}
            onChange={(e) => setNewType(e.target.value)}
          >
            {DEVICE_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>

          <select
            className="devices-select"
            value={newZoneId}
            onChange={(e) => setNewZoneId(e.target.value)}
            required
          >
            <option value="">Select zone</option>
            {zones.map((z) => (
              <option key={z.id} value={z.id}>
                {z.display_name || z.name}
              </option>
            ))}
          </select>

          <button className="devices-add-btn" type="submit">
            Add device
          </button>
        </form>
      </section>

      <section className="devices-section">
        <h2 className="devices-section-title">Existing devices</h2>

        {loading ? (
          <p className="devices-empty">Loading devices...</p>
        ) : (
          <div className="devices-list">
            {devices.map((device) => (
              <div key={device.id} className="device-card">
                <div className="device-main">
                  <div className="device-name">{device.name}</div>
                  <div className="device-meta">
                    <span className="device-type">{device.type}</span>
                    <span className="device-zone">{findZoneLabel(device)}</span>
                    <span className="device-status">{device.status}</span>
                  </div>
                </div>
                <button
                  className="device-remove-btn"
                  type="button"
                  onClick={() => handleDeleteDevice(device.id)}
                >
                  Remove
                </button>
              </div>
            ))}

            {devices.length === 0 && !loading && (
              <p className="devices-empty">No devices configured yet.</p>
            )}
          </div>
        )}
      </section>
    </div>
  )
}
