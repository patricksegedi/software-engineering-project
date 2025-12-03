// src/api/movies.js

const BASE_URL = "http://127.0.0.1:8000";

export async function searchMovies(q) {
  const res = await fetch(
    `${BASE_URL}/movies?q=${encodeURIComponent(q || "")}`
  );

  if (!res.ok) {
    console.error("Failed to fetch movies", res.status);
    return [];
  }

  const data = await res.json();
  return data.results; // FastAPI에서 results 배열로 내려줌
}

export async function getMovieById(id) {
  // 아직 /movies/{id} 엔드포인트는 없으니까
  // /movies 전체를 받아서 그 안에서 찾아줌
  const res = await fetch(`${BASE_URL}/movies`);

  if (!res.ok) {
    console.error("Failed to fetch movies", res.status);
    return null;
  }

  const data = await res.json();
  const movie = data.results.find((m) => m.id === Number(id));
  return movie ?? null;
}
