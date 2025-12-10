// src/api/auth.js
import { api } from "./client"

// 회원가입
export async function signupApi({
  email,
  password,
  age,
  familyRole,
  name,
  masterKey,
}) {
  const res = await api.post("/auth/signup", {
    email,
    password,
    age: age ? Number(age) : null,
    family_role: familyRole || null,
    name: name || null,               // ✅ 이름 전달
    master_key: masterKey || null,    // ✅ 마스터키 전달 (비어있으면 null)
  });
  return res.data;
}

// 로그인
export async function loginApi({ email, password }) {
  const res = await api.post("/auth/login", {
    email,
    password,
  })
  return res.data
}
