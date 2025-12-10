// src/api/client.js
import axios from "axios"

export const api = axios.create({
  baseURL: "http://127.0.0.1:8000", // FastAPI가 돌아가는 주소/포트
})
