# UI Modernization Specification

## ADDED Requirements

### Requirement: Tailwind Design System
The system SHALL provide a Tailwind CSS design system with centralized tokens for colors, typography, spacing, elevation, and state styling that can be consumed from all templates via CDN configuration.

#### Scenario: Tailwind CDN config applies project tokens

- **WHEN** `base.html` loads Tailwind through the official CDN script
- **THEN** the inline `tailwind.config` extends theme tokens for brand colors, typography, and spacing that are reused across templates

#### Scenario: Templates consume design tokens

- **WHEN** a Jinja template includes layout or component partials
- **THEN** Tailwind utility classes sourced from the shared CDN configuration define colors, typography, and spacing consistently

### Requirement: shadcn Component Library Abstraction
The system SHALL expose shadcn/ui component patterns through reusable Jinja partials or macros that map to Tailwind utility classes and interaction states.

#### Scenario: Component partials reuse base styles

- **WHEN** a template renders a button, card, form, or navigation component via the shared partial
- **THEN** the component outputs markup styled with Tailwind utilities that match shadcn/ui guidelines, including hover, focus, and disabled states

#### Scenario: Accessibility attributes are applied

- **WHEN** an interactive component is rendered
- **THEN** ARIA roles, aria-* attributes, and focus management required by the shadcn/ui pattern are included in the markup

### Requirement: Mobile-First Responsive Layouts
The system SHALL render all core pages (dashboard, reservations, events, check-in, authentication) using mobile-first layouts that progressively enhance for larger breakpoints.

#### Scenario: Mobile viewport rendering

- **WHEN** viewport width is ≤ 640px
- **THEN** critical navigation and content sections stack vertically with touch-friendly spacing and typography defined by the design system

#### Scenario: Desktop enhancement

- **WHEN** viewport width is ≥ 1024px
- **THEN** responsive Tailwind utilities promote multi-column layouts, persistent navigation, and data tables without horizontal scroll

### Requirement: PWA-Friendly UX Enhancements
The system SHALL provide offline/resume states, skeleton loading placeholders, and install affordances aligned with PWA best practices.

#### Scenario: Offline indicator

- **WHEN** the service worker detects offline mode
- **THEN** templates display an inline offline banner using the design system components without breaking layout

#### Scenario: Skeleton loading states

- **WHEN** data-dependent sections are awaiting API responses
- **THEN** skeleton placeholders styled via Tailwind utilities are shown until content resolves

#### Scenario: Install prompt guidance

- **WHEN** the app meets installability criteria
- **THEN** a shadcn-styled prompt or tooltip invites the user to install the PWA and respects user dismissal preferences
