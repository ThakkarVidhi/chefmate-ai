import { useState, useEffect, useRef } from 'react';
import { useImmer } from 'use-immer';
import ChatMessages from '@/components/ChatMessages';
import ChatInput from '@/components/ChatInput';

function Chatbot() {
  const [messages, setMessages] = useImmer([]);
  const [newMessage, setNewMessage] = useState('');
  const socketRef = useRef(null);

  const isLoading = messages.length && messages[messages.length - 1].loading;

  useEffect(() => {
    socketRef.current = new WebSocket('ws://localhost:8000/ws/chat');

    socketRef.current.onclose = () => {
      console.warn("WebSocket closed");
    };

    return () => {
      socketRef.current.close();
    };
  }, []);

  const submitNewMessage = () => {
    const trimmedMessage = newMessage.trim();
    if (!trimmedMessage || isLoading || !socketRef.current) return;

    // Add user's message and empty assistant message
    setMessages(draft => {
      draft.push({ role: 'user', content: trimmedMessage });
      draft.push({ role: 'assistant', content: '', loading: true });
    });

    setNewMessage('');

    // Send message to backend
    socketRef.current.send(trimmedMessage);

    let buffer = '';

    socketRef.current.onmessage = (event) => {
      const text = event.data;

      if (text === '__END__') {
        setMessages(draft => {
          draft[draft.length - 1].loading = false;
        });
        return;
      }

      buffer += text;
      setMessages(draft => {
        draft[draft.length - 1].content = buffer;
      });
    };

    socketRef.current.onerror = (error) => {
      console.error("WebSocket error:", error);
      setMessages(draft => {
        draft[draft.length - 1].content = 'Error generating the response';
        draft[draft.length - 1].loading = false;
        draft[draft.length - 1].error = true;
      });
    };
  };

  return (
    <div className='relative grow flex flex-col gap-6 pt-6'>
      {messages.length === 0 && (
        <div className='mt-3 font-urbanist text-primary-blue text-xl font-light space-y-2'>
          <p>👋 Welcome!</p>
          <p>I'm your friendly AI Cooking Assistant. 🍳</p>
          <p>Just tell me the ingredients you have at home — like "chicken, rice, and bell pepper" — and I'll suggest a recipe you can cook!</p>
        </div>
      )}
      <ChatMessages messages={messages} isLoading={isLoading} />
      <ChatInput
        newMessage={newMessage}
        isLoading={isLoading}
        setNewMessage={setNewMessage}
        submitNewMessage={submitNewMessage}
      />
    </div>
  );
}

export default Chatbot;