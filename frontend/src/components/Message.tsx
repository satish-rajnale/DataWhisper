import type { Message as MessageType } from '../types';
import './Message.css';

interface MessageProps {
  message: MessageType;
}

export function Message({ message }: MessageProps) {
  const isUser = message.role === 'user';
  
  return (
    <div className={`message ${isUser ? 'message-user' : 'message-assistant'}`}>
      <div className="message-header">
        <span className="message-role">{isUser ? 'You' : 'Assistant'}</span>
        <span className="message-time">
          {message.timestamp.toLocaleTimeString()}
        </span>
      </div>
      <div className="message-content">
        {message.error ? (
          <div className="message-error">{message.error}</div>
        ) : (
          <>
            <p>{message.content}</p>
            {message.sql && (
              <details className="message-sql">
                <summary>SQL Query</summary>
                <pre>{message.sql}</pre>
              </details>
            )}
            {message.rows && message.rows.length > 0 && (
              <details className="message-data">
                <summary>Data ({message.rows.length} rows)</summary>
                <div className="message-table-container">
                  <table className="message-table">
                    <thead>
                      <tr>
                        {Object.keys(message.rows[0]).map((key) => (
                          <th key={key}>{key}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {message.rows.slice(0, 10).map((row, idx) => (
                        <tr key={idx}>
                          {Object.values(row).map((value, colIdx) => (
                            <td key={colIdx}>
                              {value === null ? (
                                <em>null</em>
                              ) : typeof value === 'object' ? (
                                JSON.stringify(value)
                              ) : (
                                String(value)
                              )}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {message.rows.length > 10 && (
                    <p className="message-table-note">
                      Showing first 10 of {message.rows.length} rows
                    </p>
                  )}
                </div>
              </details>
            )}
          </>
        )}
      </div>
    </div>
  );
}

