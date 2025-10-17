import { useState } from "react";
import axios from "axios";

export default function App() {
  const [file, setFile] = useState(null);
  const [imageUrl, setImageUrl] = useState("");
  const [preview, setPreview] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [minScore, setMinScore] = useState(0.5);

  const API_BASE = "https://visual-product-matcher-o6rv.onrender.com"; 

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
    setImageUrl("");
  };

  const handleUrlChange = (e) => {
    setImageUrl(e.target.value);
    setPreview(e.target.value);
    setFile(null);
  };

  const handleSearch = async () => {
    if (!file && !imageUrl) return alert("Please upload or enter an image URL.");
    setLoading(true);
    setResults([]);

    try {
      let response;
      if (file) {
        const formData = new FormData();
        formData.append("file", file);
        response = await axios.post(`${API_BASE}/api/search`, formData);
      } else {
        response = await axios.post(`${API_BASE}/api/search`, { url: imageUrl });
      }
      setResults(response.data.results || []);
    } catch (err) {
      console.error(err);
      alert("Error searching similar products");
    } finally {
      setLoading(false);
    }
  };

  const filteredResults = results.filter((r) => r.similarity >= minScore);

  return (
    <div className="min-h-screen flex flex-col items-center p-6">
      <h1 className="text-3xl font-bold text-black-600 mb-4">
        Visual Product Matcher
      </h1>

      <div className="bg-white shadow-lg rounded-xl p-6 w-full max-w-3xl mb-8">
        <h1 className="text-2xl font-bold text-black mb-4">
              Upload image or Paste link
            </h1>
        <div className="flex flex-col md:flex-row items-center gap-4">
  
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="border rounded p-2 w-full"
          />
          <span className="font-semibold">or</span>
          <input
            type="text"
            placeholder="Paste image URL"
            value={imageUrl}
            onChange={handleUrlChange}
            className="border rounded p-2 w-full"
          />
        </div>

        {preview && (
          <div className="mt-4 flex justify-center">
            <img
              src={preview}
              alt="Preview"
              className="max-h-64 rounded-lg shadow-md"
            />
          </div>
        )}

        <div className="flex justify-center mt-4">
          <button
            onClick={handleSearch}
            disabled={loading}
            className="bg-purple-400 text-white px-5 py-2 rounded-lg hover:bg-purple-700 transition"
          >
            {loading ? "Searching..." : "Find Similar Products"}
          </button>
        </div>
      </div>

      {results.length > 0 && (
        <div className="w-full max-w-5xl">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-xl font-semibold">Results</h2>
            <div className="flex items-center gap-2">
              <label className="text-sm">Min Score:</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={minScore}
                onChange={(e) => setMinScore(parseFloat(e.target.value))}
              />
              <span className="text-sm font-medium">{minScore}</span>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {filteredResults.map((item) => (
              <div
                key={item.id}
                className="bg-white rounded-xl shadow-md p-3 flex flex-col items-center hover:shadow-lg transition"
              >
                <img
                  src={item.image}
                  alt={item.name}
                  className="w-full h-40 object-cover rounded-md"
                />
                <div className="mt-2 text-center">
                  <p className="font-semibold">{item.name}</p>
                  <p className="text-sm text-gray-500">{item.category}</p>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${(item.similarity * 100).toFixed(0)}%` }}
                    ></div>
                  </div>
                  <p className="text-xs mt-1">
                    Similarity: {(item.similarity * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
