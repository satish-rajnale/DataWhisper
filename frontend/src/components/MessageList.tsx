import { useEffect, useRef } from 'react';
import { Message } from './Message';
import type { Message as MessageType } from '../types';
import './MessageList.css';

interface MessageListProps {
  messages: MessageType[];
}

export function MessageList({ messages }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="message-list">
      {messages.length === 0 ? (
        <div className="message-list-empty">
          <p>Start asking questions about your database!</p>
          <p className="message-list-hint">
            Try: "How many users do we have?" or "Show me the top 10 products by sales"
          </p>
        </div>
      ) : (
        <>
          {messages.map((message) => (
            <Message key={message.id} message={message} />
          ))}
          <div ref={messagesEndRef} />
        </>
      )}
    </div>
  );
}

