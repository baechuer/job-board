# Job Board Frontend

A modern React frontend for the Job Board application built with Vite, Tailwind CSS, and React Router.

## Requirements

- Node.js 18+ (recommended LTS) or 20+
- npm 9+ (comes with Node) or yarn/pnpm if you prefer
- Modern browser (for development + Playwright E2E)

Optional, recommended (Python venv-equivalent for Node):
- nvm (Node Version Manager) for Windows/macOS/Linux, or Volta

Why: Node projects commonly pin a Node version. nvm/Volta let you “activate” a per-project Node version similar to `python -m venv`.

Quick install links:
- nvm for Windows: `https://github.com/coreybutler/nvm-windows`
- nvm (macOS/Linux): `https://github.com/nvm-sh/nvm`
- Volta (cross-platform): `https://volta.sh`

## Features

- **Authentication**: Login, registration, and email verification
- **Role-based Access**: Admin, Recruiter, and Candidate dashboards
- **Job Management**: Browse, post, and manage job listings
- **Admin Panel**: Manage recruiter requests and users
- **Responsive Design**: Mobile-first design with Tailwind CSS

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router v6** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **React Query** - Server state management
- **React Hook Form** - Form handling
- **Zustand** - Client state management

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm (or yarn/pnpm)
- If using Playwright E2E locally, the first run will download browsers

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update the API URL in `.env`:
```
VITE_API_URL=http://localhost:5000/api
```

4. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Recommended workflow with Node “virtual env” (nvm/Volta)

Using nvm (closest analogue to Python virtualenv):

1) Install nvm (see links above)
2) Choose a project Node version and save it:
```bash
nvm install 20
nvm use 20
# optionally record it
echo 20 > .nvmrc
```
3) Every time you work on the project:
```bash
cd frontend
nvm use  # reads .nvmrc
npm ci   # or npm install (ci is reproducible on clean installs)
npm run dev
```

Volta alternative (automatic activation):
```bash
volta pin node@20
volta pin npm@10
# Volta ensures pinned versions are used automatically in this folder
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── common/         # Generic components (Button, Input, etc.)
│   ├── layout/         # Layout components (Header, Sidebar, Layout)
│   ├── forms/          # Form components
│   └── job/            # Job-related components
├── pages/              # Page components (routes)
│   ├── auth/           # Authentication pages
│   ├── dashboard/      # Dashboard pages
│   ├── jobs/           # Job-related pages
│   ├── admin/          # Admin pages
│   └── profile/        # Profile pages
├── hooks/              # Custom React hooks
├── services/           # API services
├── context/            # React Context providers
├── utils/              # Utility functions
└── styles/             # Global styles
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run test` - Run unit/integration tests (Vitest + RTL + MSW)
- `npm run test:ui` - Vitest UI runner
- `npm run test:coverage` - Vitest coverage
- `npm run e2e` - Run Playwright end-to-end tests (auto-starts Vite)

## API Integration

The frontend connects to the Flask backend API. Make sure your backend is running on the configured URL.

### Authentication Flow

1. User registers/logs in
2. JWT token is stored in localStorage
3. Token is automatically included in API requests
4. Token refresh is handled automatically

### Role-based Routing

- **Admin**: Access to admin dashboard, user management, recruiter requests
- **Recruiter**: Can post jobs, manage applications, view recruiter dashboard
- **Candidate**: Can browse jobs, apply, view candidate dashboard

## Environment Variables

- `VITE_API_URL` - Backend API URL (default: http://localhost:5000/api)
- `VITE_APP_NAME` - Application name
- `VITE_APP_VERSION` - Application version

## Contributing

1. Follow the existing code structure
2. Use Tailwind CSS for styling
3. Implement proper error handling
4. Add PropTypes for component props
5. Write clean, readable code

## License

This project is part of the Job Board application.

---

## Notes on Testing

- Unit/Integration: uses Vitest + React Testing Library with MSW to mock HTTP; tests do not require the Flask backend.
- E2E: uses Playwright and mocks backend calls at the network layer; first run will download browsers (`npx playwright install`).

## Common Issues

- npm command not found: Install Node.js and restart the terminal. On Windows Git Bash, you may need to open a new terminal after install.
- Tailwind CSS build error about PostCSS plugin: this repo uses Tailwind v4 via `@tailwindcss/postcss`. Ensure `postcss.config.js` references `@tailwindcss/postcss` (already set here).