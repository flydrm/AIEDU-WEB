# E2E

- Dev run:
  - Backend: `uvicorn app.presentation.api.main:app --host 0.0.0.0 --port 8000`
  - Frontend: `npm --prefix web run dev`
  - Set `E2E_BASE_URL=http://localhost:5173`
- Run tests:
  - `npx playwright install --with-deps`
  - `npm --prefix web run build` (or keep dev server running)
  - `npx playwright test` (from repo root)

Covers routes `/`, `/chat`, `/lesson`, `/parent`, `/safety`. SSE relies on backend `/api/v1/ai/chat`.