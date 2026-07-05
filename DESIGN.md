---
name: Edupro SMS
description: Fast, credible, no-nonsense interface for school staff and families.
colors:
  brand-primary: "#FF0527"
  brand-primary-dark: "#c8021e"
  brand-primary-light: "#fff0f2"
  ink: "#0f172a"
  neutral-700: "#374151"
  neutral-600: "#4b5563"
  neutral-500: "#6b7280"
  neutral-300: "#d1d5db"
  neutral-200: "#e5e7eb"
  neutral-100: "#f3f4f6"
  neutral-50: "#f9fafb"
  status-success: "#16a34a"
  status-success-light: "#d1fae5"
  status-success-dark: "#065f46"
  status-warning: "#fef3c7"
  status-warning-ink: "#92400e"
typography:
  body:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: "13px"
rounded:
  sm: "6px"
  md: "10px"
  lg: "14px"
  pill: "999px"
spacing:
  sm: "8px"
  md: "12px"
  lg: "20px"
components:
  button-primary:
    backgroundColor: "{colors.brand-primary}"
    textColor: "#ffffff"
    rounded: "{rounded.pill}"
    padding: "7px 16px"
  button-primary-hover:
    backgroundColor: "{colors.brand-primary-dark}"
  button-secondary:
    backgroundColor: "#ffffff"
    textColor: "{colors.neutral-700}"
    rounded: "{rounded.pill}"
    padding: "7px 16px"
---

# Design System: Edupro SMS

## 1. Overview

**Creative North Star: "The Front Desk"**

Edupro SMS behaves like a good school front desk: it gets you to the answer or the task and gets out of the way. The lineage is Gmail and Google Admin console — minimal chrome, high information density — with a deliberate second influence: where Frappe/ERPNext Desk conventions already work for staff, this system borrows the pattern rather than inventing a new one to relearn.

This system rejects a generic Bootstrap admin template — the look every page had before this redesign, each with its own hardcoded inline styles and no shared identity. It also rejects cluttered legacy school-management software and anything playful or cartoonish. Color is used sparingly and functionally: one reserved brand red marks action and identity; everything else is quiet neutrals, with status conveyed by icon and label, never by hue alone.

**Key Characteristics:**
- Flat, minimal, information-dense — nothing between the user and the task
- One shared shell (`templates/portal_base.html`) across every portal page
- A single reserved accent color, used for action and identity only
- Status never relies on color alone — every pill pairs an icon with text
- Solid dark sidebar (not a light one) holding navigation, sticky on desktop, collapsing to a horizontal bar on mobile

## 2. Colors

Restrained strategy: tinted neutrals carry the interface, with exactly one saturated accent reserved for action and identity, and a separate, deliberately distinct scale for status.

### Primary
- **Front Desk Red** (`#FF0527`, `--edu-red`): primary buttons, active nav state, stat-card icon tint, focus states, table row hover accents. Reserved — see the Named Rule below.
- **Front Desk Red Dark** (`#c8021e`, `--edu-red-dark`): hover state for primary red elements, `.pill-red` text, `.btn-reject`.
- **Front Desk Red Light** (`#fff0f2`, `--edu-red-light`): background tint for red pills and stat-card icon wells.

### Neutral
- **Ink** (`#0f172a`, `--edu-dark`): headings, sidebar background, `.btn-publish`. Doubles as both text-ink and the dark surface color — one value, two roles.
- **Neutral-700 / 600 / 500** (`#374151` / `#4b5563` / `#6b7280`): body text, secondary text, labels/placeholders, in decreasing emphasis.
- **Neutral-300 / 200 / 100 / 50** (`#d1d5db` / `#e5e7eb` / `#f3f4f6` / `#f9fafb`): borders, dividers, table header background, detail-row background.

### Status (deliberately separate from Primary)
- **Success** (`#16a34a` text-dark `#065f46` on `#d1fae5`, `.pill-green`): Paid / approved / on-track.
- **Warning** (`#92400e` on `#fef3c7`, `.pill-amber`): Partially paid / in-progress / at-risk.
- **Danger** (uses Front Desk Red Dark on Red Light, `.pill-red`): Billed/unpaid / overdue / critical.
- **Neutral** (`.pill-gray`, neutral-600 on neutral-100): informational / no-action-needed states.

### Named Rules
**The Reserved Red Rule.** Front Desk Red appears on the primary action, the active nav state, and identity marks only. It is never reused as a status color — status has its own scale (above), so "this is clickable" and "this is overdue" are never the same visual signal.

**The Status-Is-Never-Color-Alone Rule.** Every `.pill` pairs its color with an icon (`.edu-icon`) and a text label. Verified in production: fee status (Billed/Partially Paid/Paid), with icons `alert-circle`/`clock`/`check-circle` respectively.

## 3. Typography

**Body Font:** Inter (400/500/600/700/800), with `-apple-system, BlinkMacSystemFont, sans-serif` fallback. Single family for the whole system — no separate display face.

**Character:** Warm enough to not feel cold or purely mechanical, tuned first for scanning dense tables and forms quickly.

### Hierarchy
- **h1** (800 weight, 1.25rem): one per page, the page title (e.g. "Student Fees").
- **h2** (700 weight, 0.95rem): section headers, paired with a red-tinted icon (`.edu-icon` at 15×15px, colored `--edu-red`).
- **h3** (700 weight, 0.82rem, neutral-700): sub-section headers (e.g. inside a detail panel: "Record Payment", "Adjust Fee Amount").
- **Body / table cells** (0.8rem): the default density for data.
- **Label** (0.66–0.7rem, uppercase, letter-spacing 0.4px, neutral-500): table column headers, stat-card labels, detail-field labels. Sentence meaning conveyed via uppercase+tracking here specifically because these are structural labels (column/field headers), not decorative section eyebrows — the No Eyebrow Rule below is about section headings, not these.

### Named Rules
**The No Eyebrow Rule.** No tiny uppercase tracked kicker text above section `<h2>` headings. Section identity comes from the heading itself, paired with its icon — never a decorative label above it.

## 4. Elevation

Flat by default. Surfaces sit flush against the page at rest (`.card`, `.stat-card` have a 1px border, no shadow at rest). A shadow appears only on hover/interaction as a lift cue (`--edu-shadow-sm` / `--edu-shadow-md`), never as static decoration.

### Shadow Vocabulary
- **`--edu-shadow-sm`** (`0 1px 3px rgba(15,23,42,.06)`): stat-card hover.
- **`--edu-shadow-md`** (`0 4px 14px rgba(15,23,42,.08)`): `.card-hover` hover/lift state.

### Named Rules
**The Flat-By-Default Rule.** No shadow at rest. Shadows are a hover/interaction response only.

## 5. Components

### Buttons (`.btn`)
- **Shape:** pill (`border-radius: 999px`), 1.5px border, 7px/16px padding, 0.78rem/700 weight text.
- **Primary** (`.btn-primary`): Front Desk Red fill, white text — the one primary action per row/section (e.g. "Record" on a payment form).
- **Secondary** (`.btn-secondary`): white fill, neutral-700 text, neutral-200 border; hover shifts border+text to red. Used for every non-primary action (Manage, Statement, Reset Filters, pagination).
- **Semantic actions:** `.btn-approve` (green fill — approve/publish-adjacent positive actions), `.btn-reject` (red-dark fill), `.btn-publish` (ink fill) — reserved for workflow-transition actions (Report Card approval flow), not general use.
- **Disabled:** 0.6 opacity, default cursor.

### Pills (`.pill`)
- Pill-shaped, 3px/10px padding, 0.7rem/700 weight, always icon + text (see Named Rule above). Four color variants: green/amber/red/gray.

### Cards (`.card`, `.stat-card`)
- 1px neutral-200 border, `--edu-radius-md` (10px) corners, white background, flat at rest. `.stat-card` additionally has a fixed-size icon well (30×30px, red-light background, red icon) and a value+label stack. Used sparingly — plain tables are preferred for dense staff data; cards are reserved for genuinely grouped summaries (the 4 dashboard stat-cards, not table rows).

### Filter Bar (`.filter-bar`, `.filter-input`, `.filter-select`)
- Horizontal flex row, wraps on narrow viewports. Search input flexes wider (min 180px) than select dropdowns (160px). Focus state: border shifts to Front Desk Red, no glow. Shared across every page with list filtering (Fees today; Billing and Students next).

### Detail Row / Expand Panel (`.detail-row`, `.detail-panel`, `.detail-section`)
- A table row toggled open in place beneath its parent row, revealing forms (payment recording, field edits) without leaving the table. Background neutral-50. Never a modal — this is a deliberate, proven interaction pattern (used identically on the Bursar dashboard and Fee Entry). Multiple `.detail-section`s within one panel are separated by a top border + spacing, each with its own `<h3>`.

### Chips (`.chip`)
- Pill-shaped info snippet, neutral-100 background, bold red numerals inline (`.chip strong`). `.chip-alert` variant swaps to red-light background for attention-needing info chips.

### Navigation (Sidebar)
- Solid ink-colored (`--edu-dark`) sidebar, 188px wide, sticky on desktop (`position: sticky; top: 20px`), rounded `--edu-radius-lg` (14px) corners. Brand mark (logo + school name) at top, nav links below, session/logout footer at bottom. Active nav item: red fill, white text and icon. On mobile (≤768px): becomes a static, full-width, horizontally-wrapping bar at the top of the page instead of a sidebar.

### Icons
- Inline SVG via the `icons.icon(name, cls="")` Jinja macro (`templates/includes/icons.html`), never an icon font or external sprite. 14×14px default (`.edu-icon`), scales contextually (15×15 in h2, 16×16 in stat-card icon wells, 11×11 in pills). **Every `{%- ... -%}` branch in the macro must use whitespace-trim tags** — a missing trim leaks a raw newline into the SVG output, which is invisible in HTML but a hard JS syntax error the moment an icon is embedded inside a JS string (discovered when Fees' dynamically-rendered table needed inline icons).

## 6. Do's and Don'ts

### Do:
- **Do** extend `templates/portal_base.html` for every portal page (`{% extends %}` + `{% block sidebar_nav %}` + `{% block portal_content %}`) — one shared shell, no per-page reimplementation.
- **Do** pair every status badge with an icon and a text label, never color alone.
- **Do** reserve Front Desk Red for actions and identity only — never for status.
- **Do** favor plain tables over cards on staff data-entry and review screens.
- **Do** use the expand-in-place detail-row pattern for inline edit/payment forms instead of a modal.
- **Do** verify real Frappe/DocType field names before wiring a new page's API calls — this codebase has repeatedly had UI built against assumed field names that didn't match the actual schema (`admission_number`, `Student.email`, `Student Ledger Entry.student_fee`, `Academic Term.is_active` all turned out not to exist).

### Don't:
- **Don't** recreate the pre-redesign look: hardcoded per-page inline styles, default Bootstrap card/badge/button styling with no shared identity.
- **Don't** build dense, deeply-nested-menu navigation like legacy SIS software.
- **Don't** use bright, playful, or cartoonish color or iconography anywhere, including student/parent-facing screens.
- **Don't** use Front Desk Red — or any single hue — as the only signal for fee, grade, or approval status.
- **Don't** add shadows to static cards or table rows "for depth." Shadows are reserved for hover/interaction feedback.
- **Don't** use uppercase-tracked "eyebrow" labels above section headings.
- **Don't** write a Jinja `{% elif %}` chain (e.g. in the icon macro) without whitespace-trim tags (`{%- -%}`) if its output will ever be embedded inside a JS string literal.
