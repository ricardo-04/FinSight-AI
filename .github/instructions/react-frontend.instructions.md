---
applyTo: "frontend/**"
---

# Instructions - React Frontend (frontend/)

## Project Overview

React 18 single-page application using functional components and hooks,
Vite as the build tool, Bootstrap 5 for UI styling, Keycloak for
authentication, and React Router DOM for client-side routing.

## Tech Stack

- **Framework**: React 18 (functional components + hooks)
- **Language**: JavaScript (JSX)
- **Build tool**: Vite 5
- **UI Library**: Bootstrap 5
- **Auth**: keycloak-js 26
- **Routing**: React Router DOM 6
- **Testing**: Not yet configured (recommend Vitest + React Testing Library)

## Key Commands

```bash
cd frontend
npm install             # install dependencies
npm run dev             # start dev server on port 3000
npm run build           # production build
npm run preview         # preview production build
```

## Project Structure

```
frontend/
  src/
    App.jsx              # Root component, routing, auth bootstrap
    main.jsx             # Entry point, renders App into DOM
    styles.css           # Global styles
    auth/
      keycloak.js        # Keycloak initialization and config
    components/
      AsyncState.jsx     # Reusable loading/error/access-denied states
    hooks/
      useProtectedResource.js  # Hook for authenticated API calls
    lib/
      api.js             # API utility functions
    screens/
      DashboardScreen.jsx        # Main dashboard
      NotFoundScreen.jsx         # 404 page
      OpportunityListScreen.jsx  # Opportunity listing
      OpportunityWorkspaceScreen.jsx  # Individual opportunity workspace
      SubmissionScreen.jsx       # Opportunity submission form
      TemplatesScreen.jsx        # Template management
```

## Component Conventions

- Functional components only; no class components
- Hooks for state (`useState`) and side effects (`useEffect`)
- Custom hooks for reusable logic (prefix with `use`, placed in `src/hooks/`)
- Screens represent full page views (placed in `src/screens/`)
- Reusable UI components in `src/components/`
- API utilities in `src/lib/`
- Use Bootstrap CSS classes for all styling; avoid inline styles
- No wildcard imports; import specific exports
- Remove unused imports after every change
- No placeholder variable names

## Routing Conventions

- Routes defined in `App.jsx` using React Router DOM 6
- Use `NavLink` for navigation with active state
- Protected routes check Keycloak roles before rendering
- 404 handled by a catch-all route to `NotFoundScreen`

## Authentication Conventions

- Keycloak initialized in `src/auth/keycloak.js`
- Token attached via `Authorization: Bearer` header in API calls
- Token refresh handled before API requests (`keycloak.updateToken()`)
- Roles extracted from Keycloak token for route protection
- Never store tokens in localStorage; keep in Keycloak instance

## API Conventions

- Base URL configured via `VITE_API_BASE_URL` environment variable
- All API calls include the Keycloak bearer token
- Use `fetch` API with appropriate error handling
- API utilities in `src/lib/api.js`

## Environment Variables

All frontend environment variables use the `VITE_` prefix:
- `VITE_API_BASE_URL` - Backend API base URL
- `VITE_KEYCLOAK_URL` - Keycloak server URL
- `VITE_KEYCLOAK_REALM` - Keycloak realm name
- `VITE_KEYCLOAK_CLIENT_ID` - Keycloak client ID

## Security

- Never use `dangerouslySetInnerHTML` with untrusted content
- Sanitize user input before rendering
- Never log sensitive data (tokens, PII, passwords)
- Follow OWASP Top 10 guidelines
- Tokens only in memory (Keycloak instance), never localStorage

## Output Logging

After every implementation or QA review, create a Markdown file in
`.github/copilot-outputs/` named `<BranchName>-react-<phase>-output.md`.
If the file exists, create a versioned copy: `-v2.md`, `-v3.md`, etc.
The file must include: phase run, changed files, commands executed, and
results.

## Development Pipeline

Every task must follow this pipeline:
1. Architecture phase - produce a clear design decision
2. Development phase - implement following the architectural decision
3. QA Review phase - validate quality and release readiness

Use the React Orchestrator agent for end-to-end story implementation.
