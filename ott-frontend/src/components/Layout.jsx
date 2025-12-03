// src/components/Layout.jsx
import Header from "./Header";

export default function Layout({ children }) {
  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "#000",
        color: "#fff",
      }}
    >
      <Header />
      <main
        style={{
          paddingTop: "70px", // fixed header height
          paddingBottom: "40px",
        }}
      >
        {children}
      </main>
    </div>
  );
}
