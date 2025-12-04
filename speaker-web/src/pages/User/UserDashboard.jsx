// src/pages/User/UserDashboard.jsx
import { useEffect, useState } from "react"
import "./UserDashboard.css"

export default function UserDashboard() {
  const [devices, setDevices] = useState([])

  // 1) 처음 렌더링될 때 백엔드에서 기기 목록 불러오기
  useEffect(() => {
    async function loadDevices() {
      try {
        const res = await fetch("http://127.0.0.1:8000/devices")
        const data = await res.json()
        setDevices(data)
      } catch (err) {
        console.error("Failed to load devices", err)
      }
    }
    loadDevices()
  }, [])

  // 2) 기기 상태 토글 → 백엔드에 반영
  const toggleDevice = async (id) => {
    const target = devices.find((d) => d.id === id)
    if (!target) return

    // door 타입이면 locked/unlocked, 그 외에는 on/off
    let nextStatus
    if (target.type === "door") {
      nextStatus = target.status === "locked" ? "unlocked" : "locked"
    } else {
      nextStatus = target.status === "on" ? "off" : "on"
    }

    try {
      await fetch(`http://127.0.0.1:8000/devices/${id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: nextStatus }),
      })

      // 프론트 state도 같이 업데이트
      setDevices((prev) =>
        prev.map((d) => (d.id === id ? { ...d, status: nextStatus } : d))
      )
    } catch (err) {
      console.error("Failed to update device", err)
    }
  }

  // 3) 현재 devices에서 존 목록 뽑기
  const zones = [...new Set(devices.map((d) => d.zone))]

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
