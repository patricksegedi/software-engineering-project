// src/pages/MovieDetailPage.jsx
import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { getMovieById } from "../api/movies";

export default function MovieDetailPage() {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function load() {
      const data = await getMovieById(id);
      setMovie(data);
    }
    load();
  }, [id]);

  if (!movie) {
    return (
      <div style={{ padding: "5rem 1.5rem" }}>
        <p>Movie not found.</p>
      </div>
    );
  }

  return (
    <div
      style={{
        maxWidth: "1200px",
        margin: "0 auto",
        padding: "2.5rem 1.5rem",
        display: "grid",
        gridTemplateColumns: "1.1fr 1.3fr",
        gap: "1.8rem",
      }}
    >
      <div>
        <div
          style={{
            borderRadius: "0.5rem",
            overflow: "hidden",
            boxShadow: "0 18px 35px rgba(0,0,0,0.9)",
          }}
        >
          <img
            src={movie.posterUrl}
            alt={movie.title}
            style={{ width: "100%", display: "block" }}
          />
        </div>
      </div>

      <div>
        <button
          onClick={() => navigate(-1)}
          style={{
            marginBottom: "0.9rem",
            padding: "0.35rem 0.8rem",
            borderRadius: "4px",
            border: "none",
            backgroundColor: "rgba(31,41,55,0.9)",
            color: "#e5e7eb",
            fontSize: "0.8rem",
            cursor: "pointer",
          }}
        >
          ← Back
        </button>

        <h1 style={{ fontSize: "2rem", fontWeight: 800 }}>
          {movie.title}
        </h1>
        <p
          style={{
            marginTop: "0.4rem",
            color: "#d1d5db",
            fontSize: "0.9rem",
          }}
        >
          {movie.genre} · {movie.year}
        </p>

        <p
          style={{
            marginTop: "1rem",
            lineHeight: 1.6,
            color: "#e5e7eb",
            fontSize: "0.95rem",
          }}
        >
          {movie.description}
        </p>

        <div style={{ marginTop: "1.7rem", display: "flex", gap: "0.7rem" }}>
          <button
            style={{
              padding: "0.55rem 1.3rem",
              borderRadius: "4px",
              border: "none",
              backgroundColor: "#fff",
              color: "#000",
              fontWeight: 600,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "0.3rem",
            }}
          >
            ▶ Play
          </button>
          <button
            style={{
              padding: "0.55rem 1.3rem",
              borderRadius: "4px",
              border: "none",
              backgroundColor: "rgba(75,85,99,0.9)",
              color: "#f9fafb",
              fontWeight: 600,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "0.3rem",
            }}
          >
            + Add to My List
          </button>
        </div>
      </div>
    </div>
  );
}
