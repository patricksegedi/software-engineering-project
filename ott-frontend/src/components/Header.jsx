// src/components/Header.jsx
import { useNavigate, useLocation } from "react-router-dom";
import { useState } from "react";

export default function Header() {
  const navigate = useNavigate();
  const location = useLocation();
  const [query, setQuery] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    navigate(`/search?q=${encodeURIComponent(query.trim())}`);
  };

  const isActive = (path) =>
    location.pathname === path ? "#fff" : "#e5e7ebb0";

  return (
    <header
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        zIndex: 50,
        background:
          "linear-gradient(to bottom, rgba(0,0,0,0.9), rgba(0,0,0,0.4), transparent)",
      }}
    >
      <div
        style={{
          maxWidth: "1200px",
          margin: "0 auto",
          padding: "0.6rem 1.5rem",
          display: "flex",
          alignItems: "center",
          gap: "1.5rem",
        }}
      >
        {/* Logo */}
        <div
          onClick={() => navigate("/")}
          style={{
            fontSize: "1.7rem",
            fontWeight: 900,
            color: "#e50914",
            cursor: "pointer",
            letterSpacing: "0.08em",
          }}
        >
          JINFLIX
        </div>

        {/* Nav */}
        <nav
          style={{
            display: "flex",
            gap: "1rem",
            fontSize: "0.9rem",
          }}
        >
          <button
            onClick={() => navigate("/")}
            style={{
              border: "none",
              background: "none",
              color: isActive("/"),
              cursor: "pointer",
            }}
          >
            Home
          </button>
          <button
            onClick={() => navigate("/")}
            style={{
              border: "none",
              background: "none",
              color: "#e5e7ebb0",
              cursor: "pointer",
            }}
          >
            Movies
          </button>
          <button
            onClick={() => navigate("/")}
            style={{
              border: "none",
              background: "none",
              color: "#e5e7ebb0",
              cursor: "pointer",
            }}
          >
            My List
          </button>
        </nav>

        {/* Right side */}
        <div
          style={{
            marginLeft: "auto",
            display: "flex",
            alignItems: "center",
            gap: "1rem",
          }}
        >
          {/* Search */}
          <form onSubmit={handleSubmit} style={{ position: "relative" }}>
            <input
              type="text"
              placeholder="Search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              style={{
                width: "180px",
                padding: "0.3rem 0.7rem",
                paddingLeft: "2rem",
                borderRadius: "4px",
                border: "1px solid rgba(148,163,184,0.6)",
                backgroundColor: "rgba(15,23,42,0.85)",
                color: "#f9fafb",
                fontSize: "0.85rem",
                outline: "none",
              }}
            />
            <span
              style={{
                position: "absolute",
                left: "6px",
                top: "50%",
                transform: "translateY(-50%)",
                fontSize: "0.8rem",
                color: "#9ca3af",
              }}
            >
              🔍
            </span>
          </form>

          {/* Profile circle */}
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: "999px",
              background:
                "linear-gradient(135deg, #e50914, #f97316)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "0.8rem",
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            J
          </div>
        </div>
      </div>
    </header>
  );
}
