# Phase 2, Feature #4: Fee Dashboard — Test Scenarios

**Feature:** Headmaster Fee Dashboard (Tasks 4.1, 4.2)  
**Status:** 🟢 COMPLETE (Ready for QA)  
**Date:** July 5, 2026  
**Tester:** _____________________

---

## Test Environment Setup

### Prerequisites
- 200+ Student Fees created with mix of statuses
- Fees span 2+ academic terms
- Student Ledger Entries (payments) recorded for various fees
- Multiple Programs (IGCSE Science, IGCSE Commerce, O-Level Math)
- Mix of payment statuses:
  - Paid (60+ students)
  - Partially Paid (70+ students)
  - Unpaid (70+ students)
- Some fees with due dates in the past (for "overdue" testing)

---

## Test Scenarios

### Test 4.1: Access Control
**Objective:** Verify only authorized roles can access dashboard

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Log in as Teacher, visit `/headmaster-dashboard/fees/` | Permission error (forbidden) | ☐ Pass / ☐ Fail |
| 2 | Log in as Bursar, visit `/headmaster-dashboard/fees/` | Permission error (forbidden) | ☐ Pass / ☐ Fail |
| 3 | Log in as Student, visit `/headmaster-dashboard/fees/` | Permission error (forbidden) | ☐ Pass / ☐ Fail |
| 4 | Log in as Headmaster, visit `/headmaster-dashboard/fees/` | Page loads successfully | ☐ Pass / ☐ Fail |
| 5 | Log in as System Manager, visit `/headmaster-dashboard/fees/` | Page loads successfully | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 4.2: Page Load & Initial Display
**Objective:** Verify page loads with filters and empty state

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Page loads | Shows filters but no data yet | ☐ Pass / ☐ Fail |
| 2 | Check Term dropdown | All active terms listed | ☐ Pass / ☐ Fail |
| 3 | Check Program dropdown | "All Programs" + all programs listed | ☐ Pass / ☐ Fail |
| 4 | Check buttons | "Load Dashboard" and "Reset" buttons present | ☐ Pass / ☐ Fail |
| 5 | Check summary cards | Cards visible but show $0 initially | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 4.3: Load Dashboard
**Objective:** Verify data loads correctly when term selected

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Select "Term 1 2026" from dropdown | Dropdown shows selection | ☐ Pass / ☐ Fail |
| 2 | Click "Load Dashboard" | Page shows loading state | ☐ Pass / ☐ Fail |
| 3 | Wait for data | Summary cards update with actual data | ☐ Pass / ☐ Fail |
| 4 | Check Total Billed | Shows correct sum of all fees for term | ☐ Pass / ☐ Fail |
| 5 | Check Total Collected | Shows correct sum of payments | ☐ Pass / ☐ Fail |
| 6 | Check Outstanding | Calculated correctly (Billed - Collected) | ☐ Pass / ☐ Fail |
| 7 | Check Collection % | Calculated correctly (Collected/Billed × 100) | ☐ Pass / ☐ Fail |
| 8 | Verify calculation | If Billed=$500K, Collected=$320K: Shows 64% | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 4.4: Summary Cards Display
**Objective:** Verify all summary cards show correct values

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Load dashboard for Term 1 | All 4 cards display with data | ☐ Pass / ☐ Fail |
| 2 | Check card styling | Cards have distinct colors (blue, green, red, yellow) | ☐ Pass / ☐ Fail |
| 3 | Check number format | Values formatted as currency ($X,XXX.XX) | ☐ Pass / ☐ Fail |
| 4 | Hover on cards | Cards respond to hover (slight lift effect) | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 4.5: Program Breakdown Chart
**Objective:** Verify pie/doughnut chart shows collections by program

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Load dashboard | "By Program" chart appears | ☐ Pass / ☐ Fail |
| 2 | Check chart type | Pie/doughnut chart with different colors per program | ☐ Pass / ☐ Fail |
| 3 | Check data accuracy | Each slice size proportional to collected amount | ☐ Pass / ☐ Fail |
| 4 | Check legend | Programs listed in legend at bottom | ☐ Pass / ☐ Fail |
| 5 | Hover on slice | Tooltip shows program name + amount collected | ☐ Pass / ☐ Fail |
| 6 | Example | If IGCSE Science=$200K of $500K total: slice = 40% | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 4.6: Status Breakdown Chart
**Objective:** Verify status chart shows Paid/Partial/Unpaid counts

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Load dashboard | "By Status" chart appears | ☐ Pass / ☐ Fail |
| 2 | Check chart type | Doughnut chart with 3 slices (green, yellow, red) | ☐ Pass / ☐ Fail |
| 3 | Check colors | Green=Paid, Yellow=Partial, Red=Unpaid | ☐ Pass / ☐ Fail |
| 4 | Check data | Slices proportional to student counts | ☐ Pass / ☐ Fail |
| 5 | Hover on slice | Tooltip shows "Paid: 140 students" (example) | ☐ Pass / ☐ Fail |
| 6 | Verify counts | Total of all 3 slices = total students | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 4.7: Collection Trend Chart
**Objective:** Verify line chart shows collection % trend over weeks

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Load dashboard | "Collection Trend" line chart appears | ☐ Pass / ☐ Fail |
| 2 | Check chart type | Line chart with points (blue line) | ☐ Pass / ☐ Fail |
| 3 | Check X-axis | Shows "Week 1", "Week 2", etc. (or dates) | ☐ Pass / ☐ Fail |
| 4 | Check Y-axis | Shows 0-100% range | ☐ Pass / ☐ Fail |
| 5 | Check trend direction | Line should trend upward (collection increases over time) | ☐ Pass / ☐ Fail |
| 6 | Hover on point | Tooltip shows "Week 1: 30%", "Week 2: 50%", etc. | ☐ Pass / ☐ Fail |
| 7 | Check endpoints | First point near 0%, last point near final %, e.g. 64% | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 4.8: Unpaid Students Table
**Objective:** Verify table shows top unpaid students sorted by urgency

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Load dashboard | "Top Unpaid Students" table appears | ☐ Pass / ☐ Fail |
| 2 | Check columns | Name, Admission #, Amount Due, Days Overdue | ☐ Pass / ☐ Fail |
| 3 | Check count | Shows up to 20 students (or fewer if less than 20 unpaid) | ☐ Pass / ☐ Fail |
| 4 | Check sorting | Students sorted by days overdue (descending) | ☐ Pass / ☐ Fail |
| 5 | Check color coding | Days Overdue colored red (30+), yellow (7-30), green (<7) | ☐ Pass / ☐ Fail |
| 6 | Check amounts | Currency formatted correctly ($X,XXX.XX) | ☐ Pass / ☐ Fail |
| 7 | Check icons | High-overdue students show warning icon | ☐ Pass / ☐ Fail |
| 8 | All paid | If all fees paid, table shows "All students have paid" message | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 4.9: Filter by Program
**Objective:** Verify program filter updates all data correctly

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Load dashboard for all programs | Baseline data loaded | ☐ Pass / ☐ Fail |
| 2 | Select "IGCSE Science" from Program dropdown | Dropdown updates | ☐ Pass / ☐ Fail |
| 3 | Click "Load Dashboard" | Data refreshes, showing only IGCSE Science | ☐ Pass / ☐ Fail |
| 4 | Check summary cards | Totals updated to only IGCSE Science fees | ☐ Pass / ☐ Fail |
| 5 | Check charts | Program chart shows only selected program breakdown (should show 1 slice) | ☐ Pass / ☐ Fail |
| 6 | Check unpaid table | Shows only unpaid students from IGCSE Science | ☐ Pass / ☐ Fail |
| 7 | Switch program | Select "IGCSE Commerce", click Load, all data updates | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 4.10: Reset Filters
**Objective:** Verify reset clears selections

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Select Term + Program | Both dropdowns have selections | ☐ Pass / ☐ Fail |
| 2 | Click "Reset" button | Both dropdowns revert to blank/default | ☐ Pass / ☐ Fail |
| 3 | Check filters | Term shows "-- Select Term --", Program shows "All Programs" | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 4.11: Chart Accuracy
**Objective:** Verify calculations match database

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Load dashboard for Term 1 2026 | All data displayed | ☐ Pass / ☐ Fail |
| 2 | Spot-check Billed total | Query DB: `SELECT SUM(amount) FROM tabStudent Fee WHERE academic_term='Term 1 2026'` | ☐ Pass / ☐ Fail |
| 3 | Compare with dashboard | Dashboard "Total Billed" matches DB sum | ☐ Pass / ☐ Fail |
| 4 | Spot-check Collected total | Query DB: `SELECT SUM(debit) FROM tabStudent Ledger Entry` | ☐ Pass / ☐ Fail |
| 5 | Compare with dashboard | Dashboard "Total Collected" matches ledger sum | ☐ Pass / ☐ Fail |
| 6 | Calculate manually | Outstanding = Billed - Collected (verify math) | ☐ Pass / ☐ Fail |
| 7 | Calculate Collection % | (Collected / Billed) × 100 (verify %) | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 4.12: Performance
**Objective:** Verify dashboard loads quickly with large datasets

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Load dashboard with 500+ fees | Page responds in <3 seconds | ☐ Pass / ☐ Fail |
| 2 | Switch program filter | Charts re-render in <2 seconds | ☐ Pass / ☐ Fail |
| 3 | Switch to different term | All data re-calculates in <3 seconds | ☐ Pass / ☐ Fail |
| 4 | Check for lag | No UI freezing or delays | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 4.13: Responsiveness
**Objective:** Verify page works on different devices

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Open on mobile (375px) | Page renders without horizontal scroll | ☐ Pass / ☐ Fail |
| 2 | Check cards on mobile | Cards stack vertically, readable | ☐ Pass / ☐ Fail |
| 3 | Check charts on mobile | Charts scale down, still readable | ☐ Pass / ☐ Fail |
| 4 | Check table on mobile | Table scrolls horizontally if needed | ☐ Pass / ☐ Fail |
| 5 | Open on tablet (768px) | All elements properly displayed | ☐ Pass / ☐ Fail |
| 6 | Open on desktop (1920px) | Full layout with optimal spacing | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 4.14: Edge Cases
**Objective:** Verify graceful handling of unusual situations

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Load term with zero fees | Shows $0 for all cards, empty charts | ☐ Pass / ☐ Fail |
| 2 | Load term with all paid | Collection % shows 100%, Unpaid table empty | ☐ Pass / ☐ Fail |
| 3 | Load term with all unpaid | Collection % shows 0%, Outstanding = Total Billed | ☐ Pass / ☐ Fail |
| 4 | Load term with no payments | Total Collected = $0, Outstanding = Total Billed | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

## Summary

| Test Group | Total | Passed | Failed | Notes |
|-----------|-------|--------|--------|-------|
| Access Control | 5 | ☐ | ☐ | |
| Page Load | 5 | ☐ | ☐ | |
| Dashboard Loading | 8 | ☐ | ☐ | |
| Summary Cards | 4 | ☐ | ☐ | |
| Charts | 18 | ☐ | ☐ | |
| Unpaid Table | 8 | ☐ | ☐ | |
| Filters | 9 | ☐ | ☐ | |
| Data Accuracy | 7 | ☐ | ☐ | |
| Performance | 4 | ☐ | ☐ | |
| Responsiveness | 6 | ☐ | ☐ | |
| Edge Cases | 4 | ☐ | ☐ | |
| **TOTAL** | **78** | **☐** | **☐** | |

---

## Sign-Off

**Feature #4 (Fee Dashboard) Ready for Production?**

☐ **YES** — All tests passed, feature is production-ready  
☐ **NO** — Issues found, needs fixes:

_____________________________

**Tester Name:** ______________________  
**Date:** ______________________  
**Signature:** ______________________

---

**Document Version:** 1.0  
**Last Updated:** July 5, 2026
