## Overview
ASP Technology provides a synchronized learning workspace for lecturers and students.

## Tech Stack
Django 6.1.3, SQLite, plain HTML/CSS/vanilla JavaScript, Argon2, python-decouple.

## Build Phase Log
- Implemented responsive split-screen sign-up and login flow.
- Added server-side registration validation for username, projector ID, phone number, and matching passwords.
- Reworked the brand panel with softer organic forms, warmer amber light, and human-centered visual balance.
- Added a rate-limited, non-enumerating password recovery request flow using Django's signed reset tokens; OTP remains deferred.
- Added non-binding placeholder routes and footer links for Terms, Privacy, Cookies, and Acceptable Use; no acceptance checkbox is shown until legal text is approved.
- Added an animated left-panel composition using cyan orbits, navy depth, amber signal nodes, and reduced-motion support.

## User Flow
Sign-up or login -> field-level validation/throttle feedback -> authenticated welcome page -> logout.

## Component Map
Sign-up form: default, hover, active, focus, loading, error, empty, disabled states.
Password controls and submit control expose keyboard focus, loading, validation, and disabled feedback.

## API Routes
- `/` sign-up
- `/login/` login
- `/logout/` POST logout
- `/welcome/` authenticated placeholder
- `/forgot-password/` password recovery request
- `/legal/terms/`, `/legal/privacy/`, `/legal/cookies/`, `/legal/acceptable-use/` legal placeholders

## Security Notes
CSRF protection, Argon2 password hashing, secure cookie flags outside DEBUG, clickjacking and MIME-sniffing headers, generic login errors, and IP-based lockout throttling are enabled.

## Design Decisions
The built-in Django User model stores the username and password; UserProfile stores the unique projector ID and phone number without requiring a custom user migration.

## Responsive Breakpoints
Desktop uses a two-panel layout. Screens below 768px stack the panels and reduce the brand panel to a compact header.

## Known Limitations
The in-memory throttle is suitable for the current single-process SQLite development setup; shared deployments should use a shared cache such as Redis.
Legal pages are placeholders and must be replaced with jurisdiction-reviewed text before public launch.
