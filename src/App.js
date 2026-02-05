import { useState } from "react";
import "./App.css";

const App = () => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:8000/chroma/query?query_text=${encodeURIComponent(query)}&n_results=5`
      );
      const data = await response.json();

      if (data.status === "success") {
        setResults(data.results);
      } else {
        setError(data.message || "An error occurred");
      }
    } catch (err) {
      setError("Failed to connect to backend. Make sure it's running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1 style={{ marginBottom: "0px" }}>ChromaDB Search</h1>
        <p style={{ marginTop: "10px", marginBottom: "30px" }}>
          Search through your contact database
        </p>

        {/* Search Form */}
        <div className="search-container">
          <form onSubmit={handleSearch} className="search-form">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search contact notes..."
              className="search-input"
              disabled={loading}
            />
            <button type="submit" className="search-button" disabled={loading}>
              {loading ? "Searching..." : "Search"}
            </button>
          </form>
        </div>

        {/* Error Display */}
        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}

        {/* Results Display */}
        {results && results.documents && results.documents[0] && (
          <div className="results-container">
            <h3>Found {results.documents[0].length} results</h3>
            {results.documents[0].map((doc, idx) => (
              <div key={idx} className="result-card">
                <div className="result-header">
                  <strong>
                    {results.metadatas[0][idx].first_name}{" "}
                    {results.metadatas[0][idx].last_name}
                  </strong>
                  <span className="company">
                    {results.metadatas[0][idx].company}
                  </span>
                </div>
                <p className="contact-info">
                  {results.metadatas[0][idx].email} |{" "}
                  {results.metadatas[0][idx].phone}
                </p>
                <p className="contact-note">{doc}</p>
                <p className="relevance">
                  Relevance: {(1 - results.distances[0][idx]).toFixed(2)}
                </p>
              </div>
            ))}
          </div>
        )}
      </header>
    </div>
  );
};

export default App;
