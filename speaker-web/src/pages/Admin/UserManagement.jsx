// src/pages/Admin/UserManagement.jsx
import { useEffect, useState } from "react"
import "./UserManagement.css"
import { getAllUsers, updateUsers } from "../../userStorage"

export default function UserManagement() {
  const [users, setUsers] = useState([])

  useEffect(() => {
    const loaded = getAllUsers()
    setUsers(loaded)
  }, [])

  const familyRoles = ["Father", "Mother", "Child", "Member"]
  const roles = ["user", "admin"]

  const handleChange = (id, key, value) => {
    const updated = users.map((user) =>
      user.id === id ? { ...user, [key]: value } : user
    )
    setUsers(updated)
    updateUsers(updated)
  }

  const handleDelete = (id) => {
    const target = users.find((u) => u.id === id)
    if (!target) return

    const ok = window.confirm(
      `Delete user "${target.email}"? This cannot be undone. (Demo DB)`
    )
    if (!ok) return

    const updated = users.filter((user) => user.id !== id)
    setUsers(updated)
    updateUsers(updated)
  }

  return (
    <div className="admin-users-container">
      <h1 className="admin-users-title">User Management</h1>
      <p className="admin-users-subtitle">
        View and edit users registered in this smart home system. Data is loaded
        from a local demo database.
      </p>

      <div className="users-table">
        <div className="table-header">
          <span>Email</span>
          <span>Role</span>
          <span>Family Role</span>
          <span>Actions</span>
        </div>

        {users.map((user) => (
          <div key={user.id} className="table-row">
            <span className="email-field">{user.email}</span>

            <select
              className="select-field"
              value={user.role}
              onChange={(e) =>
                handleChange(user.id, "role", e.target.value)
              }
            >
              {roles.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </select>

            <select
              className="select-field"
              value={user.familyRole}
              onChange={(e) =>
                handleChange(user.id, "familyRole", e.target.value)
              }
            >
              {familyRoles.map((fr) => (
                <option key={fr} value={fr}>
                  {fr}
                </option>
              ))}
            </select>

            <div className="action-group">
              <button
                className="action-btn"
                type="button"
                onClick={() =>
                  alert("Changes are already saved to the demo DB.")
                }
              >
                Save
              </button>
              <button
                className="secondary-btn"
                type="button"
                onClick={() => handleDelete(user.id)}
              >
                Delete
              </button>
            </div>
          </div>
        ))}

        {users.length === 0 && (
          <div className="table-row">
            <span>No users found in the demo database.</span>
          </div>
        )}
      </div>
    </div>
  )
}
