const BASE_URL = import.meta.env.VITE_API_URL;

async function sendChatHistoryStream(sessionId, chatHistory, onToken, onDone, onError, onMetadata) {
  try {
    console.log("Sending chat history:", chatHistory);

    const payload = {
      session_id: sessionId,
      chat_history: chatHistory.map(({ role, content }) => ({ role, content })),
    };

    const res = await fetch(`${BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
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
        console.log("Received line:", line);
        if (!line.trim()) continue;

        try {
          const parsed = JSON.parse(line);
          console.log(parsed)
          console.log("Parsed message type:", parsed.type);
          console.log("Parsed message event:", parsed.event);

          switch (parsed.event) {
            case 'token':
              onToken(parsed.data);
              break;
            case 'done':
              onDone();
              break;
            case 'metadata':
              onMetadata?.(parsed.data);
              break;
            case 'error':
              onError(parsed.message);
              break;
            default:
              console.warn('Unknown message event:', parsed.event);
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