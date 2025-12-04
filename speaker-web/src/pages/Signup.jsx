// src/pages/Signup.jsx
import "../Auth.css"
import { Link, useNavigate } from "react-router-dom"
import { addUser } from "../userStorage"

const MASTER_KEY = "01046480328"

export default function Signup() {
  const navigate = useNavigate()

    const handleSignup = async (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    const email = formData.get("email")
    const password = formData.get("password")
    const masterkey = formData.get("masterkey") // 입력한 마스터키

    // 마스터키가 정확히 01046480328이면 admin, 아니면 user
    const role =
      masterkey && masterkey.trim() === MASTER_KEY ? "admin" : "user"

    const familyRole = "Member" // 기본값

    try {
      // 1) 기존 로컬 유저 저장 (지금 구조 유지)
      addUser({ email, password, role, familyRole })

      // 2) 스피커 백엔드에도 유저 등록
      //    name은 일단 이메일 앞부분, age는 임시로 20으로 설정
      await fetch("http://127.0.0.1:8000/users/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: email.split("@")[0] || email,
          age: 20,
        }),
      })

      alert(
        role === "admin"
          ? "Admin account created. You can now log in."
          : "Account created. You can now log in."
      )
      navigate("/login")
    } catch (err) {
      console.error(err)
      alert(err.message || "Failed to sign up.")
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1 className="auth-title">Create an account</h1>
        <p className="auth-subtitle">Sign up to access your smart home</p>

        <form onSubmit={handleSignup} className="auth-form">
          <label className="auth-label">
            Email
            <input type="email" name="email" className="auth-input" required />
          </label>

          <label className="auth-label">
            Password
            <input
              type="password"
              name="password"
              className="auth-input"
              required
            />
          </label>

          <label className="auth-label">
            Master key (optional)
            <input
              type="text"
              name="masterkey"
              placeholder="Enter master key for admin"
              className="auth-input"
            />
          </label>

          <button className="auth-button" type="submit">
            Sign up
          </button>
        </form>

        <div className="auth-toggle">
          Already have an account?
          <Link to="/login" className="auth-link">
            Log in
          </Link>
        </div>
      </div>
    </div>
  )
}
