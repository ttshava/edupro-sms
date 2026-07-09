# Product

## Register

product

## Users

Two very different groups share this system, and the interface must serve both without compromise:

- **Desk-based staff** (Bursar, Headmaster, Instructor/Class Teacher, System Manager) — use the system during work hours to move through repeated, high-volume tasks: entering fees for a class, entering marks, reviewing and approving report cards, checking collection/analytics dashboards. They are trained users doing this daily; the job is to get through a list of records fast and accurately. Desktop-first.
- **Families** (Student, Guardian) — check the system occasionally, from a phone, to answer one of two questions: "how is my child doing?" or "what do we owe?". They received no training, may not be comfortable with typical app UI, and some guardians have low tech literacy. Mobile-first.

A single Guardian may have multiple children linked to their account (multi-child households are common).

## Product Purpose

Edupro SMS is an IGCSE-curriculum academic-reporting and finance platform for a junior/high school: marks entry → Class Teacher review → Headmaster approval → PDF report cards → parent email → student/parent portal access, plus fee billing, payment tracking, and collections. Long-term goal is a multi-tenant SaaS product serving multiple schools.

Success looks like: staff complete daily record-processing tasks with minimal clicks and no ambiguity; families can find their child's standing or balance in under a few seconds without needing help.

**Scope boundary:** this redesign covers the custom `edupro_sms` portal surfaces only (the pages under `www/`: bursar, bursar_billing, bursar_fees, bursar-students, my-reports, marks-entry, class-review, admin, import-data, dashboard, verify-report-card). `headmaster_dashboard_fees`, `headmaster_batch_print`, `headmaster_analytics`, `student_dashboard`, and `parent_dashboard` were removed pre-launch (2026-07-09) — unreachable from any nav, and each fully superseded by working, linked pages (`/dashboard`'s own Finance/Analytics sections, `/my-reports`). Frappe Desk itself (used by System Manager for raw DocType administration) is core Frappe/ERPNext and is out of scope — per project standing rule, core files are never modified. Where Desk conventions are genuinely good, we borrow the *pattern*, not the file.

## Brand Personality

**Fast, credible, unfussy.**

Reference points: Gmail / Google Admin console — minimal chrome, high information density, nothing between the user and the data or task. Where Frappe/ERPNext Desk conventions already exist and work, reuse them; staff already have muscle memory there and shouldn't have to relearn it. Family-facing screens keep the same seriousness and restraint as staff screens — no separate "friendlier" register, just plainer language and bigger tap targets.

## Anti-references

- **The current state**: a generic Bootstrap admin template — every one of the 16 portal pages has its own hardcoded inline `<style>` block, no shared tokens, no shared components. This is precisely what the redesign replaces.
- **Cluttered legacy school-management software**: dense toolbars, tiny text, deeply nested menus. Common in older SIS products; explicitly rejected.
- **Playful/childish design**: bright primary colors, cartoon iconography. Even on student/parent-facing screens, tone stays professional — families are trusting the school with their child's academic and financial standing.

## Design Principles

1. **Speed over decoration.** Every screen minimizes clicks-to-task-completion. Visual flourish never competes with information density, especially on staff surfaces.
2. **One shared shell.** Navigation, headers, and layout patterns are identical across all 16 portals. A user who learns one page has learned them all — this is the standardization the redesign exists to deliver.
3. **Status is never color-only.** Fee status, grade risk, and approval-workflow state each carry an icon or text label alongside color — today's red/yellow/green-only badges are a specific known defect this fixes.
4. **Familiar over novel.** Reuse existing Frappe/ERPNext Desk conventions where they already work well, instead of inventing new patterns staff have to relearn.
5. **Plain language for families.** Student/Guardian surfaces use everyday words, generous tap targets, and no jargon — these users received no training and didn't choose this software.

## Accessibility & Inclusion

- WCAG 2.1 AA baseline across all surfaces.
- No status, state, or meaning conveyed by color alone — always pair with icon and/or text.
- Design for less tech-literate parents: larger tap targets on mobile, plain-language labels, minimal jargon, no assumption of prior training or app-UI familiarity.
- English only for now — no i18n infrastructure required at this stage.
