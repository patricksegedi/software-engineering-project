// src/components/MovieRow.jsx
import MovieCard from "./MovieCard";

export default function MovieRow({ title, movies }) {
  if (!movies || movies.length === 0) return null;

  return (
    <section style={{ marginBottom: "1.8rem" }}>
      <h2
        style={{
          fontSize: "1.1rem",
          fontWeight: 600,
          marginBottom: "0.6rem",
        }}
      >
        {title}
      </h2>
      <div
        style={{
          display: "flex",
          gap: "0.6rem",
          overflowX: "auto",
          paddingBottom: "0.4rem",
        }}
      >
        {movies.map((m) => (
          <div key={m.id} style={{ minWidth: "160px", maxWidth: "180px" }}>
            <MovieCard movie={m} />
          </div>
        ))}
      </div>
    </section>
  );
}
