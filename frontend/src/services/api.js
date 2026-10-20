const API_BASE_URL = "http://127.0.0.1:8000";

export async function pingBackend() {
  const response = await fetch(`${API_BASE_URL}/api/ping`);

  if (!response.ok) {
    throw new Error("Backend connection failed");
  }

  return response.json();
}


export async function createGame() {
  const response = await fetch(`${API_BASE_URL}/api/games`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Failed to create game");
  }

  return response.json();
}

export async function getGame(gameId) {
  const response = await fetch(
    `${API_BASE_URL}/api/games/${gameId}`
  );

  if (!response.ok) {
    throw new Error("Failed to retrieve game");
  }

  return response.json();
}

export async function makePlayerMove(gameId, column) {
  const response = await fetch(
    `${API_BASE_URL}/api/games/${gameId}/moves`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ column }),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to apply player move");
  }

  return response.json();
}

