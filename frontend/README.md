# DugunSalonuApp React Frontend

This folder contains the modern React/Vite UI for the wedding hall reservation system. It consumes the FastAPI backend served from `python main.py`.

## Getting started

```bash
cd DugunSalonuApp_Frontend
npm install            # first time setup
cp .env.example .env   # adjust VITE_API_BASE_URL when needed
npm run dev            # start local dev server on http://localhost:5173
```

## Available scripts

| Command            | Description                                                    |
|--------------------|----------------------------------------------------------------|
| `npm run dev`      | Starts Vite dev server with HMR.                               |
| `npm run dev:desktop` | Runs Vite and launches the Electron shell for desktop dev.  |
| `npm run build`    | Builds optimized assets into `dist/`.                          |
| `npm run build:desktop` | Creates a Windows installer using electron-builder (under `release/`). |
| `npm run preview`  | Serves the production build locally for smoke testing.         |
| `npm run lint`     | Runs ESLint with the default React/Vite rule-set.              |

The dev server expects the backend API at `VITE_API_BASE_URL` (default `http://localhost:8000`). Update `.env` if you expose the FastAPI instance on a different host/port.
