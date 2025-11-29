import { useState, type FormEvent } from 'react';
import './MessageInput.css';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  return (
    <form className="message-input" onSubmit={handleSubmit}>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask a question about your database..."
        disabled={disabled}
        className="message-input-field"
      />
      <button
        type="submit"
        disabled={disabled || !input.trim()}
        className="message-input-button"
      >
        {disabled ? 'Sending...' : 'Send'}
      </button>
    </form>
  );
}

