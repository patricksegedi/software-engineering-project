// src/pages/Admin/UserManagement.jsx
import { useEffect, useState } from "react"
import "./UserManagement.css"
import { getUsersApi, deleteUserApi } from "../../api/users"

export default function UserManagement() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)

  // 처음 로딩될 때 유저 목록 가져오기
  useEffect(() => {
    async function loadUsers() {
      try {
        const data = await getUsersApi()
        setUsers(data)
      } catch (err) {
        console.error(err)
        alert("서버에서 유저 목록을 불러오지 못했습니다.")
      } finally {
        setLoading(false)
      }
    }
    loadUsers()
  }, [])

  const handleDeleteUser = async (id) => {
    if (!window.confirm("정말로 이 사용자를 삭제하시겠습니까?")) return

    try {
      await deleteUserApi(id)
      setUsers((prev) => prev.filter((u) => u.id !== id))
    } catch (err) {
      console.error(err)
      alert("사용자 삭제 중 오류가 발생했습니다.")
    }
  }

  const formatRole = (user) => {
    if (user.is_admin) return "Admin"
    if (user.family_role) return user.family_role
    return "User"
  }

  return (
    <div className="users-container">
      <header className="users-header">
        <h1 className="users-title">User management</h1>
        <p className="users-subtitle">
          서비스에 등록된 계정을 확인하고, 필요 시 삭제할 수 있습니다.
        </p>
      </header>

      {loading ? (
        <p className="users-empty">Loading users...</p>
      ) : (
        <section className="users-section">
          {users.length === 0 ? (
            <p className="users-empty">No users found.</p>
          ) : (
            <table className="users-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Email</th>
                  <th>Age</th>
                  <th>Role</th>
                  <th>Created at</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>{u.id}</td>
                    <td>{u.email}</td>
                    <td>{u.age ?? "-"}</td>
                    <td>
                      {u.is_admin ? (
                        <span className="badge badge-admin">Admin</span>
                      ) : (
                        <span className="badge badge-user">
                          {u.family_role || "User"}
                        </span>
                      )}
                    </td>
                    <td>
                      {u.created_at
                        ? new Date(u.created_at).toLocaleString()
                        : "-"}
                    </td>
                    <td>
                      <button
                        className="user-delete-btn"
                        type="button"
                        onClick={() => handleDeleteUser(u.id)}
                        disabled={u.is_admin} // 관리자 계정은 삭제 못하게 막음(선택)
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      )}
    </div>
  )
}
