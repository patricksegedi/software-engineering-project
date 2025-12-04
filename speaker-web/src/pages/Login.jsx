// src/pages/Login.jsx
import "../Auth.css"
import { Link, useNavigate } from "react-router-dom"
import { useAuth } from "../AuthContext"

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleLogin = (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    const email = formData.get("email")
    const password = formData.get("password")

    try {
      login(email, password)
      navigate("/dashboard")
    } catch (err) {
      alert("Invalid email or password. (Demo DB)")
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
