const BASE_URL = import.meta.env.VITE_API_URL;

async function sendChatHistoryStream(chatHistory, onMessageChunk) {
  try {

    const res = await fetch(`${BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_history: chatHistory })
    });

    console.log(res)
    
    if (!res.ok) {
      console.log("Error:")
      console.log(res)
      throw new Error(`Server error: ${res.status}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");

    let message = '';
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value, { stream: true });
      message += chunk;
      onMessageChunk(chunk); // Notify frontend to append streamed content
    }
    
    return message;
    
  } catch (err) {
    console.error("Fetch failed:", err);
    throw err;
  }
}

export default {
  sendChatHistoryStream
};