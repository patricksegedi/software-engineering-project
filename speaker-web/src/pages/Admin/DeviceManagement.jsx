// src/pages/Admin/DeviceManagement.jsx
import { useState } from "react"
import "./DeviceManagement.css"

const ZONES = ["Living room", "Kitchen", "Bedroom", "Entrance"]
const TYPES = ["light", "tv", "door"]

export default function DeviceManagement() {
  const [devices, setDevices] = useState([
    { id: 1, name: "Living room lights", type: "light", zone: "Living room" },
    { id: 2, name: "Living room TV", type: "tv", zone: "Living room" },
    { id: 3, name: "Bedroom lights", type: "light", zone: "Bedroom" },
    { id: 4, name: "Main door", type: "door", zone: "Entrance" },
  ])

  const [newName, setNewName] = useState("")
  const [newType, setNewType] = useState("light")
  const [newZone, setNewZone] = useState("Living room")

  const handleAddDevice = (e) => {
    e.preventDefault()
    const trimmed = newName.trim()
    if (!trimmed) return

    const nextId = devices.length ? Math.max(...devices.map(d => d.id)) + 1 : 1

    setDevices(prev => [
      ...prev,
      { id: nextId, name: trimmed, type: newType, zone: newZone },
    ])

    setNewName("")
    setNewType("light")
    setNewZone("Living room")
  }

  const handleDelete = (id) => {
    if (!confirm("Remove this device? (Demo only)")) return
    setDevices(prev => prev.filter(d => d.id !== id))
  }

  return (
    <div className="devices-container">
      <h1 className="devices-title">Device Management</h1>
      <p className="devices-subtitle">
        Add, view and remove smart devices connected to each zone.
      </p>

      {/* Add device form */}
      <section className="devices-section">
        <h2 className="devices-section-title">Add new device</h2>
        <form className="add-device-form" onSubmit={handleAddDevice}>
          <input
            type="text"
            className="device-input"
            placeholder="e.g. Kids' room lights"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
          />

          <select
            className="select-field"
            value={newType}
            onChange={(e) => setNewType(e.target.value)}
          >
            {TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>

          <select
            className="select-field"
            value={newZone}
            onChange={(e) => setNewZone(e.target.value)}
          >
            {ZONES.map((z) => (
              <option key={z} value={z}>
                {z}
              </option>
            ))}
          </select>

          <button type="submit" className="primary-btn">
            Add device
          </button>
        </form>

        <p className="devices-hint">
          This is a demo form. In a real system, devices would be stored in a
          database and linked to hardware.
        </p>
      </section>

      {/* Device list */}
      <section className="devices-section">
        <h2 className="devices-section-title">Current devices</h2>

        <div className="devices-table">
          <div className="devices-header">
            <span>Name</span>
            <span>Type</span>
            <span>Zone</span>
            <span>Actions</span>
          </div>

          {devices.map((device) => (
            <div key={device.id} className="devices-row">
              <span className="device-name">{device.name}</span>
              <span className="device-type">{device.type}</span>
              <span className="device-zone">{device.zone}</span>
              <button
                type="button"
                className="secondary-btn"
                onClick={() => handleDelete(device.id)}
              >
                Remove
              </button>
            </div>
          ))}

          {devices.length === 0 && (
            <p className="devices-empty">No devices configured yet.</p>
          )}
        </div>
      </section>
    </div>
  )
}
