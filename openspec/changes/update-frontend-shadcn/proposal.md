# Frontend Modernization

## Why

Current templates rely on Bootstrap 5 and jQuery, resulting in inconsistent styling, limited component variety, and poor mobile experience. A Tailwind + shadcn/ui design system with PWA-focused patterns will deliver a cohesive, modern, and responsive UI.

## What Changes

- Replace Bootstrap-based styling with Tailwind CSS utilities and shadcn/ui component patterns.
- Establish a reusable design system including typography, color tokens, layout primitives, and interactive states.
- Rebuild critical user flows (dashboard, reservations, events, check-in, auth) with mobile-first responsive layouts.
- Introduce PWA-friendly enhancements (offline placeholders, skeleton states, install prompts) across templates.
- Update asset pipeline (build tooling, CSS/JS bundling) to support Tailwind and component scripts.
- Add regression test coverage for key templates and linting for Tailwind class usage.

## Impact

- Affected specs: ui/
- Affected code: `app/templates/**`, `app/static/css/**`, `app/static/js/**`, `app/static/service-worker.js`, layout-related Flask views, build pipeline configuration.
- Tooling: Tailwind CLI integration, potential Node.js dependencies for shadcn/ui build scripts.
