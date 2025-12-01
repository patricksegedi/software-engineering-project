// src/App.jsx
import { Routes, Route, Navigate, Outlet } from "react-router-dom"
import Login from "./pages/Login.jsx"
import Signup from "./pages/Signup.jsx"
import UserDashboard from "./pages/User/UserDashboard.jsx"
import Profile from "./pages/User/Profile.jsx"
import AdminDashboard from "./pages/Admin/AdminDashboard.jsx"
import UserManagement from "./pages/Admin/UserManagement.jsx"
import ZoneManagement from "./pages/Admin/ZoneManagement.jsx"
import DeviceManagement from "./pages/Admin/DeviceManagement.jsx"
import NavBar from "./components/NavBar.jsx"
import { useAuth } from "./AuthContext.jsx"

function MainLayout() {
  return (
    <>
      <NavBar />
      <div className="page-body">
        <Outlet />
      </div>
    </>
  )
}

function RequireAdmin({ children }) {
  const { user } = useAuth()
  if (!user || user.role !== "admin") {
    return <Navigate to="/dashboard" replace />
  }
  return children
}

function App() {
  return (
    <Routes>
      {/* Auth only */}
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      {/* Main layout with NavBar */}
      <Route element={<MainLayout />}>
        <Route path="/dashboard" element={<UserDashboard />} />
        <Route path="/profile" element={<Profile />} />

        <Route
          path="/admin"
          element={
            <RequireAdmin>
              <AdminDashboard />
            </RequireAdmin>
          }
        />
        <Route
          path="/admin/users"
          element={
            <RequireAdmin>
              <UserManagement />
            </RequireAdmin>
          }
        />
        <Route
          path="/admin/zones"
          element={
            <RequireAdmin>
              <ZoneManagement />
            </RequireAdmin>
          }
        />
        <Route
          path="/admin/devices"
          element={
            <RequireAdmin>
              <DeviceManagement />
            </RequireAdmin>
          }
        />
      </Route>
    </Routes>
  )
}

export default App
