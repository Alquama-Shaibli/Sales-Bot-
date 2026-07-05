// hooks/useChat.js — Manages full chat state
import { useState, useCallback, useRef } from 'react';
import api from './useApi';

export function useChat() {
  const [messages, setMessages]           = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [isLoading, setIsLoading]         = useState(false);
  const [isStarting, setIsStarting]       = useState(false);
  const [error, setError]                 = useState(null);
  const [turnCount, setTurnCount]         = useState(0);
  const [isStarted, setIsStarted]         = useState(false);
  const abortRef = useRef(null);

  // Start a new conversation session
  const startConversation = useCallback(async () => {
    setIsStarting(true);
    setError(null);
    setMessages([]);
    setTurnCount(0);

    try {
      const { data } = await api.post('/api/conversation/start');
      setConversationId(data.conversation_id);
      setIsStarted(true);

      // Add opening bot message
      setMessages([{
        id: Date.now(),
        role: 'assistant',
        content: data.opening_message,
        timestamp: new Date().toISOString(),
      }]);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsStarting(false);
    }
  }, []);

  // Send a user message and get bot response
  const sendMessage = useCallback(async (userText) => {
    if (!conversationId || !userText.trim() || isLoading) return;

    const userMsg = {
      id: Date.now(),
      role: 'user',
      content: userText.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);
    setError(null);

    try {
      const { data } = await api.post('/api/message', {
        user_message: userText.trim(),
        conversation_id: conversationId,
      });

      const botMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, botMsg]);
      setTurnCount(data.turn_count || turnCount + 1);
    } catch (err) {
      setError(err.message);
      // Add error message in chat
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        content: "I'm having trouble connecting right now. Please try again in a moment.",
        timestamp: new Date().toISOString(),
        isError: true,
      }]);
    } finally {
      setIsLoading(false);
    }
  }, [conversationId, isLoading, turnCount]);

  // Reset to start fresh
  const resetChat = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setTurnCount(0);
    setError(null);
    setIsStarted(false);
  }, []);

  return {
    messages,
    conversationId,
    isLoading,
    isStarting,
    isStarted,
    error,
    turnCount,
    startConversation,
    sendMessage,
    resetChat,
  };
}
