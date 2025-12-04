// src/pages/SearchPage.jsx
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { searchMovies } from "../api/movies";
import MovieRow from "../components/MovieRow";

export default function SearchPage() {
  const [params] = useSearchParams();
  const q = params.get("q") || "";
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await searchMovies(q);
      setMovies(data);
      setLoading(false);
    }
    load();
  }, [q]);

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "0 1.5rem" }}>
      <h1
        style={{
          fontSize: "1.6rem",
          fontWeight: 700,
          marginBottom: "0.8rem",
          marginTop: "1rem",
        }}
      >
        Search results for "{q}"
      </h1>

      {loading && <p>Searching...</p>}

      {!loading && movies.length === 0 && (
        <p style={{ color: "#9ca3af" }}>No results found.</p>
      )}

      {!loading && movies.length > 0 && (
        <MovieRow title="Results" movies={movies} />
      )}
    </div>
  );
}
