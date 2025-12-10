// src/AuthContext.jsx
import { createContext, useContext, useEffect, useState } from "react"
import { loginApi } from "./api/auth"
import { getAuthUser, saveAuthUser, clearAuthUser } from "./userStorage"

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)

  // 앱 처음 켰을 때 localStorage에서 로그인 상태 복구
  useEffect(() => {
    const stored = getAuthUser()
    if (stored) {
      setUser(stored)
    }
  }, [])

  const login = async (email, password) => {
    // 백엔드에 로그인 요청
    const loggedIn = await loginApi({ email, password })
    setUser(loggedIn)
    saveAuthUser(loggedIn)
  }

  const logout = () => {
    setUser(null)
    clearAuthUser()
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
