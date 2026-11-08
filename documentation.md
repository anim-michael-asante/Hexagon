## Overview
Hexagon provides a synchronized learning workspace for lecturers and students.

## Tech Stack
Django 6.1.3, SQLite, plain HTML/CSS/vanilla JavaScript, Argon2, python-decouple.

## Build Phase Log
- Implemented responsive split-screen sign-up and login flow.
- Added server-side registration validation for username, projector ID, phone number, and matching passwords.
- Reworked the brand panel with softer organic forms, warmer amber light, and human-centered visual balance.
- Added a rate-limited, non-enumerating password recovery request flow using Django's signed reset tokens; OTP remains deferred.
- Added non-binding placeholder routes and footer links for Terms, Privacy, Cookies, and Acceptable Use; no acceptance checkbox is shown until legal text is approved.
- Added an animated left-panel composition using cyan orbits, navy depth, amber signal nodes, and reduced-motion support.
- Refreshed the shared auth typography with Bricolage Grotesque and DM Sans, and strengthened the white logo surround while retaining the dark background.
- Increased logo badge contrast and aligned the right-side auth panel with Hexagon navy, cyan, and pale aqua surfaces.
- Restyled the login “WELCOME BACK” label as a branded Bricolage Grotesque pill with a subtle cyan border.
- Replaced the post-login placeholder with a responsive ASP classroom-control dashboard using the supplied dashboard structure.
- Simplified the dashboard to a logo-led header with profile settings/logout, projector scan/disconnect controls, empty connection history, and an empty Classroom readiness shell.
- Replaced Classroom readiness with a Connected status card and live connection-duration timer; scan is now a compact header notification-style control, and the profile menu includes Settings, Terms and Conditions, and Log out.
- Added a connection-strength pie chart, changed the header icon to notifications, and moved Disconnect beside Scan for projector inside the classroom-control hero.
- Updated dashboard surfaces to Midnight Navy (#101B2D) and Panel White (#F4F7FA), restored the legal footer, and kept Terms and Conditions out of the profile menu.
- Removed the classroom-control eyebrow, made Disconnect red, kept projector scans as non-cancellable actions, added a notification dropdown with mark-all/delete-all feedback, and increased the Connected card shadow.
- Removed the auth logo glow, preserved Scan for projector colours while scanning, and updated only signup copy to the lecture-hall message while leaving login wording unchanged.
- Removed all remaining logo shadow/filter effects and aligned auth display typography with the rounded, heavy reference font treatment.
- Simplified signup messaging to “Every lesson. One connected classroom.” and applied the cleaner DM Sans treatment while preserving login copy.
- Applied the same simplified message and DM Sans treatment to the login brand panel while retaining the “WELCOME BACK” label and login form wording.
- Added an authenticated Settings page covering Appearance, Security and login, and Account sections; on mobile, Connected now appears before Connection history.
- Reworked Settings into a left navigation with one visible right-side subsection at a time, persisted settings to UserProfile, added authenticated multipart saving, and added a settings update test.
- Added development media storage/routing for persisted profile images and applied the settings migration to the local database.
- Removed Appearance from Settings, leaving General and Security and login navigation; uploaded user images now persist through UserProfile and render as the current image.
- Hardened profile uploads with allowlisted raster extensions, magic-byte checks, generated UUID filenames, protected authenticated delivery, account deletion with media cleanup, and GDPR-style account data export.
- Refined account settings with button-based data export, profile-image clearing, hidden raw file-widget metadata, a styled dashboard footer, and aligned mobile General/Security navigation with General first.
- Simplified the sign-up brand message by removing the technical eyebrow, switched display typography to Bricolage Grotesque with DM Sans body text, and added a white logo surround for contrast.

## User Flow
Sign-up or login -> field-level validation/throttle feedback -> authenticated dashboard -> scan projector or cancel scan -> view connected duration -> use profile settings, Terms and Conditions, or logout.

## Component Map
Sign-up form: default, hover, active, focus, loading, error, empty, disabled states.
Password controls and submit control expose keyboard focus, loading, validation, and disabled feedback. Dashboard actions expose scan loading/cancellation, connected-duration feedback, profile menu, empty history, focus, hover, active, and disabled states.

## API Routes
- `/` sign-up
- `/login/` login
- `/logout/` POST logout
- `/welcome/` authenticated ASP classroom-control dashboard (UI-only mock state)
- `/forgot-password/` password recovery request
- `/legal/terms/`, `/legal/privacy/`, `/legal/cookies/`, `/legal/acceptable-use/` legal placeholders

## Security Notes
CSRF protection, Argon2 password hashing, secure cookie flags outside DEBUG, clickjacking and MIME-sniffing headers, generic login errors, and IP-based lockout throttling are enabled.

## Design Decisions
The built-in Django User model stores the username and password; UserProfile stores the unique projector ID and phone number without requiring a custom user migration.

## Responsive Breakpoints
Dashboard uses a full-width header and two-column content/summary layout on desktop. Below 1100px the summary rail moves below the main content; below 600px cards and lessons collapse to a single column.

## Known Limitations
The in-memory throttle is suitable for the current single-process SQLite development setup; shared deployments should use a shared cache such as Redis.
Projector discovery, panel status, connection timing, disconnect/reset, and lecture readiness are currently mock UI state and should be connected only after the UI is approved and backend work is explicitly unlocked. Recommended next project requirements are room selection, host failover, panel health/error recovery, role permissions, lecture-end cleanup, and an audit trail. Legal pages are placeholders and must be replaced with jurisdiction-reviewed text before public launch.
