// src/components/VoiceSearchWatcher.jsx
import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

const API_BASE = "http://127.0.0.1:8000";

export default function VoiceSearchWatcher() {
  const navigate = useNavigate();
  const location = useLocation();
  const [lastToken, setLastToken] = useState("");

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/voice-search`);
        if (!res.ok) return;

        const data = await res.json();
        const query = (data.query || "").trim();
        if (!query) return;

        const token = `${query}|${data.count}`;
        if (token === lastToken) return; // 이미 처리한 요청이면 무시
        setLastToken(token);

        console.log("🔔 Voice search polled:", data);

        if (data.allowed === false) {
          const msg =
            data.reason ||
            "This content is restricted due to age or permission settings.";
          alert(msg);
          console.warn("Blocked voice query:", msg);

          // 한 번 처리했으니 서버 쪽 상태 초기화
          await fetch(`${API_BASE}/voice-search/reset`, { method: "POST" });
          return;
        }

        const currentQ = new URLSearchParams(location.search || "").get("q");
        if (location.pathname === "/search" && currentQ === query) return;

        console.log("✅ Voice search accepted! query =", query);
        navigate(`/search?q=${encodeURIComponent(query)}`);
      } catch (err) {
        console.warn("Voice search polling error:", err);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [lastToken, location.pathname, location.search, navigate]);

  return null;
}
