// src/App.jsx
import Layout from "./components/Layout";
import HomePage from "./pages/HomePage";
import SearchPage from "./pages/SearchPage";
import MovieDetailPage from "./pages/MovieDetailPage";
import { Routes, Route } from "react-router-dom";
import VoiceSearchWatcher from "./components/VoiceSearchWatcher";

function App() {
  return (
    <>
      <VoiceSearchWatcher />

      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/movie/:id" element={<MovieDetailPage />} />
        </Routes>
      </Layout>
    </>
  );
}

export default App;
