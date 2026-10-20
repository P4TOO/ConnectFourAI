
import { useEffect, useState } from "react";
import { pingBackend } from "./services/api";

function App() {
  const [message, setMessage] = useState("Connecting...");
  const [error, setError] = useState(null);

  useEffect(() => {
    pingBackend()
      .then((data) => setMessage(data.message))
      .catch((err) => setError(err.message));
  }, []);

  return (
    <main style={{ padding: "2rem" }}>
      <h1>ConnectFourAI</h1>

      {error ? (
        <p>Connection error: {error}</p>
      ) : (
        <p>Backend: {message}</p>
      )}
    </main>
  );
}

export default App;
