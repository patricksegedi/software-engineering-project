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

  // 로그인 안 되어 있으면 로그인 페이지로
  if (!user) {
    return <Navigate to="/login" replace />
  }

  // DB에서 온 플래그 사용: is_admin === true 인 경우만 접근 허용
  if (!user.is_admin) {
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
