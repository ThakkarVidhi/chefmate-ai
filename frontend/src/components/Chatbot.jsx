import { useState, useEffect } from 'react';
import { useImmer } from 'use-immer';
import api from '@/api';
import { getSessionId } from '@/utils/session'; 
import ChatMessages from '@/components/ChatMessages';
import ChatInput from '@/components/ChatInput';

function Chatbot() {
  const [messages, setMessages] = useImmer([]);
  const [newMessage, setNewMessage] = useState('');
  const [sessionId, setSessionId] = useState('');

  const isLoading = messages.length && messages[messages.length - 1].loading;

  useEffect(() => {
    setSessionId(getSessionId()); 
  }, []);

  async function submitNewMessage() {
    const trimmedMessage = newMessage.trim();
    if (!trimmedMessage || isLoading) return;

    setMessages(draft => [
      ...draft,
      { role: 'user', content: trimmedMessage },
      { role: 'assistant', content: '', loading: true }
    ]);
    setNewMessage('');

    const chatHistory = [...messages, { role: 'user', content: trimmedMessage }];

    try {
      await api.sendChatHistoryStream(
        sessionId,                        
        chatHistory,
        (chunk) => {
          setMessages(draft => {
            draft[draft.length - 1].content += chunk;
          });
        },
        () => {
          setMessages(draft => {
            const lastMessage = draft[draft.length - 1];
            lastMessage.loading = false;

            const cleaned = lastMessage.content.trim();
            if (cleaned === '') {
              lastMessage.content = '_Sorry, I couldn’t find enough relevant information to answer that. Could you please clarify or try rephrasing?_';
              lastMessage.fallback = true;
            }
          });
        },
        (err) => {
          console.error("Stream error:", err);
          setMessages(draft => {
            draft[draft.length - 1].content = 'Error generating the response.';
            draft[draft.length - 1].loading = false;
            draft[draft.length - 1].error = true;
          });
        },
        (metadata) => {
          console.log("Received metadata:", metadata);
        }
      );
    } catch (err) {
      console.error("Fetch failed:", err);
      setMessages(draft => {
        const lastIndex = draft.length - 1;
        if (lastIndex >= 0 && draft[lastIndex].loading) {
          draft[lastIndex].content = 'Error generating the response.';
          draft[lastIndex].loading = false;
          draft[lastIndex].error = true;
        }
      });
    }
  }

  return (
    <div className='relative grow flex flex-col gap-6 pt-6'>
      {messages.length === 0 && (
        <div className='mt-3 font-urbanist text-primary-blue text-xl font-light space-y-2'>
          <p>👋 Welcome!</p>
          <p>I'm your friendly AI Cooking Assistant. 🍳</p>
          <p>Just tell me the ingredients you have at home — like "chicken, rice, and bell pepper" — and I'll suggest a recipe you can cook!</p>
        </div>
      )}
      <ChatMessages
        messages={messages}
        isLoading={isLoading}
      />
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