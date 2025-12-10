// src/pages/Signup.jsx
import "../Auth.css"
import { Link, useNavigate } from "react-router-dom"
import { signupApi } from "../api/auth"

export default function Signup() {
  const navigate = useNavigate()

  const handleSignup = async (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    const name = formData.get("name")
    const email = formData.get("email")
    const password = formData.get("password")
    const masterkey = formData.get("masterkey") // 빈 문자열일 수도 있음
    const age = formData.get("age")
    const familyRole = formData.get("familyRole")

    try {
      await signupApi({
        name,
        email,
        password,
        age,
        familyRole,
        masterKey: masterkey, // 백엔드에서 master_key로 받게 되어 있음
      })
      alert("회원가입이 완료되었습니다. 로그인해주세요.")
      navigate("/login")
    } catch (err) {
      console.error(err)
      alert("회원가입 중 오류가 발생했습니다.")
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1 className="auth-title">Create an account</h1>
        <p className="auth-subtitle">
          Sign up to start using your smart home
        </p>

        <form onSubmit={handleSignup} className="auth-form">
          {/* ✅ 이름 필드 추가 */}
          <label className="auth-label">
            Name
            <input
              type="text"
              name="name"
              className="auth-input"
              placeholder="Enter your name"
            />
          </label>

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
              maxLength={72} // ✅ 너가 마지막에 붙여준 maxLength 반영
            />
          </label>

          <label className="auth-label">
            Age
            <input
              type="number"
              name="age"
              className="auth-input"
              min="0"
              max="120"
            />
          </label>

          {/* ❌ Sign up as admin 체크박스 제거 */}

          <label className="auth-label">
            Family role
            <select name="familyRole" className="auth-input">
              <option value="">Select role</option>
              <option value="parent">Parent</option>
              <option value="child">Child</option>
              <option value="guest">Guest</option>
            </select>
          </label>

          <label className="auth-label">
            Master key
            <input
              type="password"
              name="masterkey"
              className="auth-input"
              placeholder="(optional) Enter master key"
              // ✅ required 제거: 비워도 회원가입 되게
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
