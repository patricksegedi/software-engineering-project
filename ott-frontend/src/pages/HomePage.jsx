// src/pages/HomePage.jsx
import { useEffect, useState } from "react";
import { searchMovies } from "../api/movies";
import MovieRow from "../components/MovieRow";

export default function HomePage() {
  const [allMovies, setAllMovies] = useState([]);
  const [featured, setFeatured] = useState(null);

  useEffect(() => {
    async function load() {
      const data = await searchMovies(""); // 서버에서 전체 목록
      setAllMovies(data);
      setFeatured(data[0] || null);
    }
    load();
  }, []);

  const getByGenre = (genre) =>
    allMovies.filter((m) => m.genre.toLowerCase() === genre.toLowerCase());

  return (
    <div>
      {/* 위쪽 Hero 섹션은 너가 이미 만들어둔 코드 그대로 두고 */}

      <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "0 1.5rem" }}>
        <MovieRow title="Trending Now" movies={allMovies} />
        <MovieRow title="Sci-Fi Movies" movies={getByGenre("SF")} />
        <MovieRow title="Action Movies" movies={getByGenre("Action")} />
        <MovieRow title="Romance" movies={getByGenre("Romance")} />
        <MovieRow title="Drama" movies={getByGenre("Drama")} />
        <MovieRow title="Thrillers" movies={getByGenre("Thriller")} />
        <MovieRow title="Animation" movies={getByGenre("Animation")} />
        <MovieRow title="Comedy" movies={getByGenre("Comedy")} />
      </div>
    </div>
  );
}
