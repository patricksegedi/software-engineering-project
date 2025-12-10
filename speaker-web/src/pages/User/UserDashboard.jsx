// src/pages/User/UserDashboard.jsx
import "./UserDashboard.css"
import { useDevices } from "../../hooks/useDevices"

export default function UserDashboard() {
  const { devices, loading, toggleDevice } = useDevices()

  return (
    <div className="dashboard-container">
      <h1 className="dashboard-title">My smart home</h1>
      <p className="dashboard-subtitle">
        Control your lights, TV and other devices.
      </p>

      {loading && devices.length === 0 ? (
        <p>Loading devices…</p>
      ) : (
        <div className="device-grid">
          {devices.map((d) => (
            <button
              key={d.id}
              type="button"
              onClick={() => toggleDevice(d)}
              className={`device-card ${
                d.status === "on" ? "device-on" : "device-off"
              }`}
            >
              <div className="device-name">{d.name}</div>
              <div className="device-zone">
                {d.zone_display_name}
              </div>
              <div className="device-status">
                {d.status === "on" ? "켜짐 🔆" : "꺼짐 🌙"}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
