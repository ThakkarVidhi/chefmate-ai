import { useState } from 'react';
import { useImmer } from 'use-immer';
import api from '@/api';
import ChatMessages from '@/components/ChatMessages';
import ChatInput from '@/components/ChatInput';

function Chatbot() {
  const [messages, setMessages] = useImmer([]);
  const [newMessage, setNewMessage] = useState('');

  const isLoading = messages.length && messages[messages.length - 1].loading;

  async function submitNewMessage() {
    const trimmedMessage = newMessage.trim();
    if (!trimmedMessage || isLoading) return;

    // Add user's message and a loading assistant placeholder
    setMessages(draft => [
      ...draft,
      { role: 'user', content: trimmedMessage },
      { role: 'assistant', content: '', loading: true }
    ]);
    setNewMessage('');

    try {
      // Send full chat history including this latest user message
      const chatHistory = [
        ...messages,
        { role: 'user', content: trimmedMessage }
      ];
      const assistantReply = await api.sendChatHistory(chatHistory);

      // Update assistant's message with real content
      setMessages(draft => {
        draft[draft.length - 1].content = assistantReply;
        draft[draft.length - 1].loading = false;
      });
    } catch (err) {
      console.error(err);
      setMessages(draft => {
        draft[draft.length - 1].content = 'Error generating the response';
        draft[draft.length - 1].loading = false;
        draft[draft.length - 1].error = true;
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
