# Tester - React Frontend Persona

## Overview

Implement high-quality tests for React functional components, custom hooks,
and screens. Focus on behavioral coverage, user interaction simulation, and
hook validation.

## Tech Stack

- **Framework**: React 18 (functional components + hooks)
- **Language**: JavaScript (JSX)
- **UI**: Bootstrap 5
- **Auth**: keycloak-js
- **Routing**: React Router DOM 6
- **Recommended testing**: Vitest + React Testing Library

## Testing Conventions

**File naming:** `*.test.js` or `*.test.jsx` colocated with the
file under test.

**Method naming:** plain English sentence starting with `should`:
`'should render error message when API call fails'`

**Structure:** All tests must have clear Arrange / Act / Assert sections
separated by a blank line.

**Coverage:** Minimum 85%; target 100%.

## React-Specific Rules

- Query elements by role, label, or text - not by test IDs unless unavoidable
- Prefer `userEvent` over `fireEvent` for user interactions
- Test hooks in isolation using `renderHook`
- Test through public component behavior, not internal implementation details
- Mock API calls at the fetch/network layer
- Avoid snapshot tests unless the component is purely presentational

## QA Checklist for Tests

- [ ] Test framework APIs used correctly
- [ ] All new public methods/components have tests
- [ ] Test method names describe expected behavior
- [ ] Arrange / Act / Assert sections present and separated
- [ ] Coverage at or above 85% for touched files
- [ ] No setTimeout for synchronization
- [ ] Keycloak auth properly mocked in tests
