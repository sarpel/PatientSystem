# Clinical AI Assistant - Frontend

React-based web interface for the Clinical AI Assistant system.

## Technology Stack

- **React 18** - UI framework with TypeScript
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework with medical theme
- **React Router** - Client-side routing
- **Zustand** - Lightweight state management
- **Axios** - HTTP client with interceptors
- **TypeScript** - Type safety

## Features

### Patient Management

- 🔍 Smart patient search by name or TCKN
- 📋 Comprehensive patient profiles
- 🏥 Medical history and lab results

### AI-Powered Analysis

- 🤖 Differential diagnosis with multiple AI models
- 💊 Treatment recommendations and clinical guidelines
- 🧪 Laboratory result analysis and trends
- ⚠️ Drug interaction checking

### User Interface

- 📱 Responsive design for desktop, tablet, and mobile
- 🎨 Medical-themed color scheme
- 📊 Interactive charts and data visualization
- ⚡ Real-time status indicators

## Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

### Development Server

The frontend runs on `http://localhost:5173` with proxy configuration to the backend API at `http://localhost:8000`.

### Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout.tsx     # Main app layout with navigation
│   ├── DiagnosisPanel.tsx
│   ├── TreatmentPanel.tsx
│   └── LabCharts.tsx
├── pages/              # Route components
│   ├── Dashboard.tsx
│   ├── PatientSearch.tsx
│   └── PatientDetails.tsx
├── services/           # API client and data services
│   └── api.ts
├── stores/             # State management
│   └── useAppStore.ts
├── styles/             # Global styles
│   └── globals.css
├── App.tsx             # Main application component
└── main.tsx           # Application entry point
```

### State Management

Uses Zustand for global state management:

- **App State**: Loading states, error handling, app initialization
- **Patient State**: Current patient, search results, search state
- **System Status**: Database and AI service connectivity

### API Integration

Axios client with:

- Request/response interceptors for logging
- Error handling with user-friendly messages
- TypeScript interfaces for type safety
- Automatic retry logic

### Styling

Tailwind CSS with custom medical theme:

- Medical color palette (blues, greens, reds for severity)
- Custom component classes (buttons, cards, tables)
- Responsive utilities
- Loading states and animations

## API Endpoints

The frontend communicates with the following backend endpoints:

- `GET /api/health` - System health check
- `GET /api/patients/search?q={query}` - Patient search
- `GET /api/patients/{tckn}` - Get patient details
- `POST /api/analyze/diagnosis` - Generate differential diagnosis
- `POST /api/analyze/treatment` - Get treatment recommendations
- `GET /api/labs/{tckn}` - Get lab results

## Configuration

### Environment Variables

Create `.env` file in frontend directory:

```env
VITE_API_URL=http://localhost:8000
VITE_APP_TITLE=Clinical AI Assistant
```

### Vite Configuration

- Proxy setup for API requests
- Path aliases (@/ for src/)
- Development server configuration

## Build Process

The build process:

1. TypeScript compilation
2. React component bundling
3. CSS processing with Tailwind
4. Asset optimization
5. Production-ready static files

Output directory: `dist/`

## Browser Support

- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

## Security

- No sensitive data in frontend
- API requests proxied through development server
- Input validation and sanitization
- XSS protection through React

## Performance

- Code splitting by route
- Lazy loading of components
- Optimized bundle sizes
- Efficient state management
