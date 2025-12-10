// src/userStorage.js
const STORAGE_KEY = "smarthome_users"

function readUsers() {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return []
  try {
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return []
    return parsed
  } catch (e) {
    console.error("Failed to parse users from storage", e)
    return []
  }
}

function writeUsers(users) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(users))
}

// 처음 아무 것도 없으면 데모 유저 3명 만들어두기
export function ensureDemoUsers() {
  const current = readUsers()
  if (current.length === 0) {
    const demoUsers = [
      {
        id: 1,
        email: "admin@example.com",
        password: "admin123",
        role: "admin",
        familyRole: "Father",
      },
      {
        id: 2,
        email: "mother@example.com",
        password: "mother123",
        role: "user",
        familyRole: "Mother",
      },
      {
        id: 3,
        email: "child@example.com",
        password: "child123",
        role: "user",
        familyRole: "Child",
      },
    ]
    writeUsers(demoUsers)
    return demoUsers
  }
  return current
}

export function getAllUsers() {
  return readUsers()
}

export function findUserByEmailAndPassword(email, password) {
  const users = readUsers()
  return users.find(
    (u) => u.email === email && u.password === password
  )
}

export function addUser({ email, password, role = "user", familyRole = "Member" }) {
  const users = readUsers()

  if (users.some((u) => u.email === email)) {
    throw new Error("Email already registered")
  }

  const nextId = users.length ? Math.max(...users.map((u) => u.id)) + 1 : 1

  const newUser = {
    id: nextId,
    email,
    password,
    role,
    familyRole,
  }

  const updated = [...users, newUser]
  writeUsers(updated)
  return newUser
}

export function updateUsers(updatedUsers) {
  writeUsers(updatedUsers)
}

// --- 새로 추가: 로그인 상태 저장용 ---

const AUTH_KEY = "smarthome_auth_user"

export function saveAuthUser(user) {
  localStorage.setItem(AUTH_KEY, JSON.stringify(user))
}

export function getAuthUser() {
  const raw = localStorage.getItem(AUTH_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch (e) {
    console.error("Failed to parse auth user", e)
    return null
  }
}

export function clearAuthUser() {
  localStorage.removeItem(AUTH_KEY)
}
