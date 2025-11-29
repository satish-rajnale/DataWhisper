import './LoadingIndicator.css';

export function LoadingIndicator() {
  return (
    <div className="loading-indicator">
      <div className="loading-spinner"></div>
      <p className="loading-text">Processing your query...</p>
    </div>
  );
}

