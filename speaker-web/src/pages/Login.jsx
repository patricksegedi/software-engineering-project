// src/pages/Login.jsx
import "../Auth.css"
import { Link, useNavigate } from "react-router-dom"
import { useAuth } from "../AuthContext"

<input
  type="password"
  name="password"
  className="auth-input"
  required
  maxLength={72}
/>

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleLogin = async (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    const email = formData.get("email")
    const password = formData.get("password")

    try {
      // FastAPI /auth/login 호출 (AuthContext에서 처리됨)
      await login(email, password)
      navigate("/dashboard") // 너가 쓰던 대시보드 경로 유지
    } catch (err) {
      console.error(err)
      alert("로그인에 실패했습니다. 이메일/비밀번호를 확인해주세요.")
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1 className="auth-title">Welcome back</h1>
        <p className="auth-subtitle">Log in to control your smart home</p>

        <form onSubmit={handleLogin} className="auth-form">
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

          <button className="auth-button" type="submit">
            Log in
          </button>
        </form>

        <div className="auth-toggle">
          Don&apos;t have an account?
          <Link to="/signup" className="auth-link">
            Sign up
          </Link>
        </div>
      </div>
    </div>
  )
}


