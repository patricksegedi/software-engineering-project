// src/pages/Admin/ZoneManagement.jsx
import { useState } from "react"
import "./ZoneManagement.css"

export default function ZoneManagement() {
  const [zones, setZones] = useState([
    { id: 1, name: "Living room" },
    { id: 2, name: "Kitchen" },
    { id: 3, name: "Bedroom" },
    { id: 4, name: "Entrance" },
  ])

  const [newZoneName, setNewZoneName] = useState("")

  const handleAddZone = (e) => {
    e.preventDefault()
    const trimmed = newZoneName.trim()
    if (!trimmed) return

    const nextId = zones.length ? Math.max(...zones.map((z) => z.id)) + 1 : 1

    setZones((prev) => [...prev, { id: nextId, name: trimmed }])
    setNewZoneName("")
  }

  const handleDeleteZone = (id) => {
    if (!confirm("Remove this zone? (Demo only)")) return
    setZones((prev) => prev.filter((z) => z.id !== id))
  }

  return (
    <div className="zones-container">
      <h1 className="zones-title">Zone Management</h1>
      <p className="zones-subtitle">
        Configure which rooms or areas exist in the smart home.
      </p>

      {/* Add zone form */}
      <section className="zones-section">
        <h2 className="zones-section-title">Add new zone</h2>
        <form className="add-zone-form" onSubmit={handleAddZone}>
          <input
            type="text"
            className="zone-input"
            placeholder="e.g. Kids' room"
            value={newZoneName}
            onChange={(e) => setNewZoneName(e.target.value)}
          />
          <button type="submit" className="primary-btn">
            Add zone
          </button>
        </form>
        <p className="zones-hint">
          This is a demo form. In a real system, zones would be stored in a
          database.
        </p>
      </section>

      {/* Zone list */}
      <section className="zones-section">
        <h2 className="zones-section-title">Existing zones</h2>

        <div className="zones-list">
          {zones.map((zone) => (
            <div key={zone.id} className="zone-row">
              <span className="zone-name">{zone.name}</span>
              <button
                type="button"
                className="secondary-btn"
                onClick={() => handleDeleteZone(zone.id)}
              >
                Remove
              </button>
            </div>
          ))}

          {zones.length === 0 && (
            <p className="zones-empty">No zones defined yet.</p>
          )}
        </div>
      </section>
    </div>
  )
}
