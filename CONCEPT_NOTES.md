# Windows 12 Preview concept notes

Build string:
- Product: Windows 12 Preview
- Build: 1ce6cfb
- Update label: 1U00

Design direction:
- centered taskbar
- acrylic floating surfaces
- large top search pill
- minimal desktop with a single app icon
- only one pinned desktop app: This PC
- Settings is reachable through Start, search, status flyouts, and about actions

Implementation notes:
- Start menu uses position animation instead of a dead stub
- every taskbar control has a handler
- weather opens a flyout and external forecast link
- network, sound, and display each open a dedicated flyout
- clock opens a calendar flyout

- Native folder added for optional C helpers and future desktop effects
- Update naming: R1U00 Official Project Update (project-side naming)
