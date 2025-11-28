// src/pages/User/UserDashboard.jsx
import { useState } from "react"
import "./UserDashboard.css"

const INITIAL_DEVICES = [
  {
    id: 1,
    name: "Living room lights",
    type: "light",
    zone: "Living Room",
    status: "off",
  },
  {
    id: 2,
    name: "Living room TV",
    type: "tv",
    zone: "Living Room",
    status: "off",
  },
  {
    id: 3,
    name: "Bedroom lights",
    type: "light",
    zone: "Bedroom",
    status: "on",
  },
  {
    id: 4,
    name: "Main door",
    type: "door",
    zone: "Entrance",
    status: "locked",
  },
]

export default function UserDashboard() {
  const [devices, setDevices] = useState(INITIAL_DEVICES)

  const zones = Array.from(new Set(devices.map((d) => d.zone)))

  const toggleDevice = (id) => {
    setDevices((prev) =>
      prev.map((device) => {
        if (device.id !== id) return device

        if (device.type === "door") {
          return {
            ...device,
            status: device.status === "locked" ? "unlocked" : "locked",
          }
        }

        return {
          ...device,
          status: device.status === "on" ? "off" : "on",
        }
      })
    )
  }

  const getDeviceButtonLabel = (device) => {
    if (device.type === "door") {
      return device.status === "locked" ? "Unlock" : "Lock"
    }
    return device.status === "on" ? "Turn off" : "Turn on"
  }

  const getDeviceStatusLabel = (device) => {
    if (device.type === "door") {
      return device.status === "locked" ? "Locked" : "Unlocked"
    }
    return device.status === "on" ? "On" : "Off"
  }

  return (
    <div className="dash-container">
      <header className="dash-header">
        <h1 className="dash-title">Smart Home Dashboard</h1>
        <p className="dash-welcome">
          Welcome back! Monitor and control your home at a glance.
        </p>
      </header>

      {/* Zones */}
      <section className="dash-section">
        <h2 className="dash-section-title">Home zones</h2>

        <div className="zone-grid">
          {zones.map((zone) => (
            <div key={zone} className="zone-card">
              <h3>{zone}</h3>
              <p>
                {devices.filter((d) => d.zone === zone).length} devices connected
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Devices */}
      <section className="dash-section">
        <h2 className="dash-section-title">Quick controls</h2>

        <div className="device-grid">
          {devices.map((device) => (
            <div
              key={device.id}
              className={`device-card ${
                device.status === "on" || device.status === "unlocked"
                  ? "device-card-active"
                  : ""
              }`}
            >
              <h3>{device.name}</h3>
              <p className="device-meta">
                Type: <span>{device.type}</span> · Zone: <span>{device.zone}</span>
              </p>
              <p className="device-status">
                Status: <strong>{getDeviceStatusLabel(device)}</strong>
              </p>

              <button
                className="toggle-btn"
                type="button"
                onClick={() => toggleDevice(device.id)}
              >
                {getDeviceButtonLabel(device)}
              </button>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
