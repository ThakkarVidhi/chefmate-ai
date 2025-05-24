const BASE_URL = import.meta.env.VITE_API_URL;

async function sendChatHistoryStream(chatHistory, onToken, onDone, onError) {
  try {
    console.log("Sending chat history:", chatHistory);

    let resBody = chatHistory.map(({ role, content }) => ({
      role,
      content
    }));

    const res = await fetch(`${BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_history: resBody }),
    });

    if (!res.ok) {
      throw new Error(`Server error: ${res.status}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");

    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const parsed = JSON.parse(line);
          if (parsed.type === 'token') {
            onToken(parsed.content);
          } else if (parsed.type === 'done') {
            onDone();
          } else if (parsed.type === 'error') {
            onError(parsed.message);
          }
        } catch (err) {
          console.error("Failed to parse line:", line, err);
        }
      }
    }

  } catch (err) {
    console.error("Fetch failed:", err);
    onError(err.message);
  }
}

export default {
  sendChatHistoryStream
};
