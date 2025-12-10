// src/api/users.js
import { api } from "./client"

// 전체 유저 목록 불러오기
export async function getUsersApi() {
  const res = await api.get("/users")
  return res.data
}

// 유저 삭제 (Admin에서 계정 지울 때)
export async function deleteUserApi(id) {
  await api.delete(`/users/${id}`)
}
