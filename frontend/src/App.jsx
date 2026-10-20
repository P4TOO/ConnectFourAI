
import { useEffect, useRef, useState } from "react";
import {
  createGame,
  getGame,
  makePlayerMove,
} from "./services/api";

function App() {
  const [game, setGame] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const requestPending = useRef(false);

  useEffect(() => {
    let active = true;

    createGame()
      .then((data) => {
        if (active) setGame(data);
      })
      .catch((err) => {
        if (active) setError(err.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  async function handleColumnClick(column) {
    if (
      !game ||
      game.current_player !== 1 ||
      game.status !== "ongoing" ||
      requestPending.current
    ) {
      return;
    }

    requestPending.current = true;
    setLoading(true);
    setError("");

    try {
      const updatedGame = await makePlayerMove(
        game.game_id,
        column
      );
      setGame(updatedGame);
    } catch (err) {
      setError(err.message);
    } finally {
      requestPending.current = false;
      setLoading(false);
    }
  }

  async function handleRefresh() {
    if (!game || requestPending.current) return;

    requestPending.current = true;
    setLoading(true);
    setError("");

    try {
      const updatedGame = await getGame(game.game_id);
      setGame(updatedGame);
    } catch (err) {
      setError(err.message);
    } finally {
      requestPending.current = false;
      setLoading(false);
    }
  }

  return (
    <main style={{ padding: "2rem", textAlign: "center" }}>
      <h1>ConnectFourAI</h1>
      <p>Temporary API Integration Test</p>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {game && (
        <>
          <p>Game ID: {game.game_id}</p>
          <p>Current Player: {game.current_player}</p>
          <p>Game Status: {game.status}</p>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(7, 50px)",
              gap: "5px",
              justifyContent: "center",
              margin: "20px auto",
            }}
          >
            {game.board.flatMap((row, rowIndex) =>
              row.map((cell, colIndex) => (
                <button
                  key={`${rowIndex}-${colIndex}`}
                  onClick={() => handleColumnClick(colIndex)}
                  disabled={
                    loading ||
                    game.current_player !== 1 ||
                    game.status !== "ongoing"
                  }
                  style={{
                    width: "50px",
                    height: "50px",
                    borderRadius: "50%",
                    border: "2px solid #333",
                    backgroundColor:
                      cell === 1
                        ? "red"
                        : cell === 2
                          ? "yellow"
                          : "white",
                    cursor: "pointer",
                  }}
                />
              ))
            )}
          </div>

          <button onClick={handleRefresh} disabled={loading}>
            Refresh Board from Python
          </button>
        </>
      )}

      {loading && <p>Loading...</p>}
    </main>
  );
}

export default App;
