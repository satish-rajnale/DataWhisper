# Frontend - Natural Language SQL Chat UI

React + TypeScript frontend for the SQL chat application.

## Setup

1. Install dependencies:
```bash
npm install
```

2. (Optional) Configure API URL in `.env`:
```env
VITE_API_URL=http://localhost:8000
```

3. Start development server:
```bash
npm run dev
```

## Build

Create production build:
```bash
npm run build
```

## Components

- **Chat.tsx**: Main chat container with state management
- **MessageList.tsx**: Scrollable message history
- **MessageInput.tsx**: Input form for user queries
- **Message.tsx**: Individual message rendering

## Features

- Real-time chat interface
- Message history with timestamps
- Expandable SQL query display
- Data table visualization
- Error handling and loading states
