// src/AuthContext.jsx
import { createContext, useContext, useEffect, useState } from "react"
import {
  ensureDemoUsers,
  findUserByEmailAndPassword,
} from "./userStorage"

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)

  useEffect(() => {
    ensureDemoUsers()
  }, [])

  const login = (email, password) => {
    const found = findUserByEmailAndPassword(email, password)
    if (!found) {
      throw new Error("Invalid email or password")
    }
    setUser({
      email: found.email,
      role: found.role,
      familyRole: found.familyRole,
    })
  }

  const logout = () => {
    setUser(null)
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
