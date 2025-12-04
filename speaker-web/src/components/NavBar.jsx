// src/components/NavBar.jsx
import { NavLink, useNavigate } from "react-router-dom"
import "./NavBar.css"

export default function NavBar() {
  const navigate = useNavigate()

  const handleLogout = () => {
    // Demo only – 여기서 실제 로그아웃은 안 하고, 로그인 페이지로만 이동
    navigate("/login")
  }

  return (
    <header className="nav-container">
      <div className="nav-inner">
        <div
          className="nav-logo"
          onClick={() => navigate("/dashboard")}
        >
          SmartHome
        </div>

        <nav className="nav-links">
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              isActive ? "nav-link nav-link-active" : "nav-link"
            }
          >
            Dashboard
          </NavLink>

          <NavLink
            to="/profile"
            className={({ isActive }) =>
              isActive ? "nav-link nav-link-active" : "nav-link"
            }
          >
            Profile
          </NavLink>

          <NavLink
            to="/admin"
            className={({ isActive }) =>
              isActive ? "nav-link nav-link-active" : "nav-link"
            }
          >
            Admin
          </NavLink>

          <NavLink
            to="/admin/users"
            className={({ isActive }) =>
              isActive ? "nav-link nav-link-active" : "nav-link"
            }
          >
            Users
          </NavLink>

          <NavLink
            to="/admin/zones"
            className={({ isActive }) =>
              isActive ? "nav-link nav-link-active" : "nav-link"
            }
          >
            Zones
          </NavLink>

          <NavLink
            to="/admin/devices"
            className={({ isActive }) =>
              isActive ? "nav-link nav-link-active" : "nav-link"
            }
          >
            Devices
          </NavLink>
        </nav>

        <div className="nav-right">
          <span className="nav-user-badge">Demo user</span>
          <button
            type="button"
            className="nav-logout-btn"
            onClick={handleLogout}
          >
            Log out
          </button>
        </div>
      </div>
    </header>
  )
}
