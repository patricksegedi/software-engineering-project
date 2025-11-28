// src/pages/Admin/AdminDashboard.jsx
import "./AdminDashboard.css"

export default function AdminDashboard() {
  // Demo stats – later these could come from backend
  const stats = {
    users: 3,
    zones: 4,
    devices: 6,
  }

  const recentActivity = [
    "Added device “Living room TV” to Living Room zone.",
    "Updated family role of user john@example.com to Father.",
    "Created new zone “Kids’ room”.",
  ]

  return (
    <div className="admin-container">
      <header className="admin-header">
        <h1 className="admin-title">Admin console</h1>
        <p className="admin-subtitle">
          Overview of users, zones and connected devices in your smart home
          system.
        </p>
      </header>

      {/* Summary cards */}
      <section className="admin-section">
        <h2 className="admin-section-title">Overview</h2>
        <div className="admin-grid">
          <div className="admin-card">
            <p className="admin-card-label">Users</p>
            <p className="admin-card-value">{stats.users}</p>
            <p className="admin-card-desc">
              Total registered accounts in the system.
            </p>
          </div>

          <div className="admin-card">
            <p className="admin-card-label">Zones</p>
            <p className="admin-card-value">{stats.zones}</p>
            <p className="admin-card-desc">
              Rooms or areas that can be controlled.
            </p>
          </div>

          <div className="admin-card">
            <p className="admin-card-label">Devices</p>
            <p className="admin-card-value">{stats.devices}</p>
            <p className="admin-card-desc">
              Lights, TVs and doors currently configured.
            </p>
          </div>
        </div>
      </section>

      {/* Recent activity */}
      <section className="admin-section">
        <h2 className="admin-section-title">Recent activity (demo)</h2>
        <p className="admin-text">
          Example actions an admin might perform in a real system.
        </p>

        <ul className="activity-list">
          {recentActivity.map((item, idx) => (
            <li key={idx} className="activity-item">
              {item}
            </li>
          ))}
        </ul>
      </section>

      {/* Next steps (placeholder for more pages) */}
      <section className="admin-section">
        <h2 className="admin-section-title">Management sections</h2>
        <p className="admin-text">
          These pages will manage users, zones and devices in more detail.
        </p>

        <div className="admin-links-grid">
          <div className="admin-link-card">
            <h3>Users</h3>
            <p>View all accounts and change family roles.</p>
          </div>
          <div className="admin-link-card">
            <h3>Zones</h3>
            <p>Configure which rooms exist in the home.</p>
          </div>
          <div className="admin-link-card">
            <h3>Devices</h3>
            <p>Add lights, TVs and doors to specific zones.</p>
          </div>
        </div>
      </section>
    </div>
  )
}
