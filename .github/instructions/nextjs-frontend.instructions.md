---
applyTo: "frontend/**"
---

# Instructions - Next.js Frontend (frontend/)

## Project Overview

Next.js 14 frontend for FinSight AI. Provides the UI for PDF upload, RAG-based chat, financial metric dashboard, and multi-document comparison. Uses the App Router, TailwindCSS for styling, and communicates with the FastAPI backend over REST.

## Tech Stack

| Component | Technology |
|---|---|
| Framework | Next.js 14 (App Router) |
| Language | TypeScript |
| Styling | TailwindCSS |
| HTTP client | fetch / axios |
| Testing | Jest + React Testing Library |

## Key Commands

```bash
cd frontend
npm install
npm run dev       # start dev server on port 3000
npm run build     # production build
npm run test      # run tests
npm run lint      # ESLint check
```

## Project Structure

```
frontend/
  app/
    layout.tsx        - root layout with providers
    page.tsx          - home page
    globals.css       - global styles + Tailwind directives
  components/         - reusable React components
  lib/                - utility functions, API client, type definitions
  pages/              - legacy pages directory (if used)
```

## TypeScript Conventions

- Strict TypeScript (`"strict": true`). No `any` unless absolutely unavoidable and justified with a comment.
- Use `interface` for object shapes that may be extended; `type` for unions and mapped types.
- Export types and interfaces from `lib/types.ts` or co-locate with the component that owns them.
- All API response shapes must be typed.

## React and Next.js Conventions

- Prefer Server Components by default; mark as `"use client"` only when interactivity requires it.
- Use the `app/` App Router directory structure. Keep `pages/` only for legacy routes if already present.
- Co-locate component-specific styles and tests with the component file.
- Use `React.FC` or explicit return types on components.
- Do not use `React.memo` unless a measurable performance problem is documented.

## API Communication

- All backend API calls go through a typed client in `lib/api.ts`.
- Backend base URL must come from environment variable `NEXT_PUBLIC_API_URL`, never hardcoded.
- Handle loading, error, and empty states in all data-fetching components.
- Never expose backend error details directly to the end user; log to console and show a friendly message.

## Styling Conventions

- Use TailwindCSS utility classes. Avoid inline styles.
- Custom design tokens (colors, spacing) go in `tailwind.config.ts`, not scattered across components.
- Responsive design: mobile-first. Test at `sm`, `md`, and `lg` breakpoints.

## File Upload Conventions

- PDF uploads use `multipart/form-data` to `POST /api/upload`.
- Validate file type (`application/pdf`) and size on the client before submitting.
- Show upload progress and clear error messages on failure.

## Security Rules

- Never embed API keys or secrets in frontend code or environment variables prefixed with `NEXT_PUBLIC_`.
- Sanitize any user content rendered as HTML (use `DOMPurify` or avoid `dangerouslySetInnerHTML`).
- CSP headers configured in `next.config.ts`.
