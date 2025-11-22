# Accessibility Report

This document summarizes the main accessibility improvements applied to the
Spam Email Classifier frontend in order to better align with WCAG guidelines.

## Landmarks and navigation

- Added a **`main` landmark** (`<main id="main-content" tabindex="-1">`) in the
  base `layout.html` template.
- Added a **"Skip to main content"** link (`.sr-only-focusable`) so keyboard
  users can jump directly to the main content, improving navigation for screen
  readers and users who rely on the keyboard.
- The top navigation (`<nav class="navbar" aria-label="Main navigation">`)
  provides a clear label for assistive technologies.

## Color, contrast, and theming

- Introduced a **theme system** using CSS custom properties and a dark/light
  toggle. Colors were chosen to provide sufficient contrast between text and
  background in both light and dark modes.
- The theme toggle button is keyboard-focusable and exposes `aria-pressed` to
  indicate the current state to assistive technologies.

## Forms and labels

- Ensured that all form fields (signup, signin, and classify) have
  **visible labels** associated with the corresponding inputs.
- Added HTML5 attributes consistent with server-side validation rules:
  - `required`, `minlength`, `maxlength`, `autocomplete`, and `inputmode`.
- Client-side validation leverages native HTML5 validation plus a small script
  that calls `form.checkValidity()` and `form.reportValidity()` before
  submission for signup, signin, and classify forms.

## Error messaging

- Server-side validation errors in templates now use:
  - `role="alert"` on error spans
  - A consistent `error` class with high-contrast color
- This helps screen readers announce validation messages and makes errors more
  visually obvious.

## Live regions and dynamic content

- Flash messages are wrapped in a list with `aria-live="polite"` so that
  status messages are announced without disrupting navigation.
- The real-time prediction panel on the classify page uses:
  - `aria-live="polite"` on the container
  - A `role="progressbar"` with `aria-valuemin`, `aria-valuemax`, and
    `aria-valuenow` for the confidence bar
- These changes allow assistive technologies to track the progress and outcome
  of spam predictions as the user types.

## Keyboard accessibility

- The skip link is styled with `.sr-only-focusable` so it is hidden visually by
  default but becomes visible when focused (e.g., via the `Tab` key).
- Focus outlines are preserved and enhanced using CSS
  (`:focus-visible { outline: 2px solid var(--color-primary); ... }`), ensuring
  that keyboard users can see where focus is.

## Responsive design

- Introduced a **mobile-first layout**:
  - `meta viewport` tag added in `layout.html`.
  - The navigation and main content are constrained to a maximum width for
    readability while scaling from small screens (~320px) up to large desktops.
  - A media query adjusts the navbar layout on narrow screens (e.g., stacking
    links vertically).

## Real-time prediction and status

- The real-time prediction UI is implemented as a progressive enhancement on
  top of the existing server-rendered form. Keyboard users can still submit the
  form normally, and screen readers receive updates via the live region and
  progressbar semantics.

## Notes on future improvements

- Additional work could include:
  - More granular ARIA descriptions for specific validation rules.
  - Automated accessibility testing as part of CI.
  - Manual testing with popular screen readers (NVDA, JAWS, VoiceOver) to
    validate the experience end-to-end.
