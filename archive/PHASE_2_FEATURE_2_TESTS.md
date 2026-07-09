# Phase 2, Feature #2: Batch Billing — Test Scenarios

**Feature:** Batch Billing (Tasks 2.1, 2.2, 2.3)  
**Status:** 🟢 COMPLETE (Ready for QA)  
**Date:** July 5, 2026  
**Tester:** _____________________

---

## Test Environment Setup

### Prerequisites
- Academic Terms created: "Term 1 2026", "Term 2 2026"
- Programs created: "IGCSE Science", "IGCSE Commerce", "O-Level Math"
- Students enrolled in each program
  - Day Boarder: 50 students
  - Full Boarder: 30 students
  - Total: 80 students per program (240 total across 3 programs)
- Billing Rates configured:
  - IGCSE Science + Day Boarder: $5,000
  - IGCSE Science + Full Boarder: $5,500
  - IGCSE Commerce + Day Boarder: $4,500
  - IGCSE Commerce + Full Boarder: $5,000
  - O-Level Math + Day Boarder: $3,500
  - O-Level Math + Full Boarder: $4,000

---

## Test Scenarios

### Test 2.1: Access Control
**Objective:** Verify only authorized roles can access batch billing

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Log in as Teacher, visit `/bursar-billing/` | Permission error (forbidden) | ☐ Pass / ☐ Fail |
| 2 | Log in as Student, visit `/bursar-billing/` | Permission error (forbidden) | ☐ Pass / ☐ Fail |
| 3 | Log in as Bursar, visit `/bursar-billing/` | Page loads successfully | ☐ Pass / ☐ Fail |
| 4 | Log in as Headmaster, visit `/bursar-billing/` | Page loads successfully | ☐ Pass / ☐ Fail |
| 5 | Log in as System Manager, visit `/bursar-billing/` | Page loads successfully | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 2.2: Form Loading
**Objective:** Verify dropdowns auto-load correctly

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Page loads, check Academic Term dropdown | All active terms listed | ☐ Pass / ☐ Fail |
| 2 | Page loads, check Program dropdown | "All Programs" + all programs listed | ☐ Pass / ☐ Fail |
| 3 | Check boarding type radio buttons | "All Boarding Types" is selected by default | ☐ Pass / ☐ Fail |
| 4 | Click boarding type options | Can switch between All / Day Boarder / Full Boarder | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 2.3: Preview Without Changes
**Objective:** Verify preview modal shows correct counts/amounts

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Select "Term 1 2026" + "All Programs" + "All Boarding" | Form is valid | ☐ Pass / ☐ Fail |
| 2 | Click "Preview Billing (No Changes)" | Modal opens, shows "Loading..." | ☐ Pass / ☐ Fail |
| 3 | Wait for preview to load | Modal shows: students count + total amount | ☐ Pass / ☐ Fail |
| 4 | Check student count | Shows 240 students (80 × 3 programs) | ☐ Pass / ☐ Fail |
| 5 | Check total amount | Calculated correctly: (50×5000 + 30×5500) + (50×4500 + 30×5000) + (50×3500 + 30×4000) = $635,000 | ☐ Pass / ☐ Fail |
| 6 | Check boarding breakdown | "Day Boarder: 150, Full Boarder: 90" | ☐ Pass / ☐ Fail |
| 7 | Check first 5 students preview | Shows student name, admission #, program, boarding, amount | ☐ Pass / ☐ Fail |
| 8 | Close modal (click Cancel) | Modal closes, form remains unchanged | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 2.4: Preview — Program Filter
**Objective:** Verify preview correctly filters by program

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Select "Term 1 2026" + "IGCSE Science" + "All Boarding" | Form is valid | ☐ Pass / ☐ Fail |
| 2 | Click Preview | Modal shows 80 students (50 day + 30 full) | ☐ Pass / ☐ Fail |
| 3 | Check total amount | $435,000 (50×5000 + 30×5500) | ☐ Pass / ☐ Fail |
| 4 | Select "Term 1 2026" + "IGCSE Commerce" + "All Boarding" | Form is valid | ☐ Pass / ☐ Fail |
| 5 | Click Preview | Modal shows 80 students | ☐ Pass / ☐ Fail |
| 6 | Check total amount | $370,000 (50×4500 + 30×5000) | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 2.5: Preview — Boarding Filter
**Objective:** Verify preview correctly filters by boarding type

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Select "Term 1 2026" + "IGCSE Science" + "Day Boarder" | Form is valid | ☐ Pass / ☐ Fail |
| 2 | Click Preview | Modal shows 50 students (day boarders only) | ☐ Pass / ☐ Fail |
| 3 | Check total amount | $250,000 (50×5000) | ☐ Pass / ☐ Fail |
| 4 | Select "Term 1 2026" + "IGCSE Science" + "Full Boarder" | Form is valid | ☐ Pass / ☐ Fail |
| 5 | Click Preview | Modal shows 30 students (full boarders only) | ☐ Pass / ☐ Fail |
| 6 | Check total amount | $165,000 (30×5500) | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 2.6: Batch Billing Execution
**Objective:** Verify fees are created correctly in bulk

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Select "Term 1 2026" + "All Programs" + "All Boarding" | Form is valid | ☐ Pass / ☐ Fail |
| 2 | Click Preview | Modal shows 240 students, $635,000 | ☐ Pass / ☐ Fail |
| 3 | Click "Confirm & Create Fees" in modal | Modal closes, page shows "Creating fees..." | ☐ Pass / ☐ Fail |
| 4 | Wait for billing to complete | Results display: "Billing complete: 240 created, 0 skipped, 0 failed" | ☐ Pass / ☐ Fail |
| 5 | Check total billed amount | Shows $635,000 | ☐ Pass / ☐ Fail |
| 6 | Verify in database | Run `SELECT COUNT(*) FROM \`tabStudent Fee\` WHERE academic_term='Term 1 2026'` | Shows 240 records | ☐ Pass / ☐ Fail |
| 7 | Check fee amounts | Spot-check 5 fees: amounts match the configured rates | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 2.7: Duplicate Prevention
**Objective:** Verify re-running billing skips already-billed students

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Run billing for "Term 1 2026" (from Test 2.6) | 240 fees created | ☓ Already done |
| 2 | Verify DB has 240 fees | `SELECT COUNT(*) FROM \`tabStudent Fee\`... = 240` | ☐ Pass / ☐ Fail |
| 3 | Run billing AGAIN for same term + criteria | Modal shows still 240 students (not 480) | ☐ Pass / ☐ Fail |
| 4 | Click "Confirm & Create Fees" | Results: "240 created=0, skipped=240, failed=0" | ☐ Pass / ☐ Fail |
| 5 | Verify DB still has 240 fees | `SELECT COUNT(*)` = 240 (no duplicates) | ☐ Pass / ☐ Fail |
| 6 | Verify no duplicate fee IDs | All student fee records are unique | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 2.8: Partial Billing (Program-Specific)
**Objective:** Verify can bill specific programs without affecting others

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Start fresh: Delete all fees for "Term 1 2026" | All fees deleted | ☐ Pass / ☐ Fail |
| 2 | Bill only "IGCSE Science" | Results: "80 created, 0 skipped, 0 failed" | ☐ Pass / ☐ Fail |
| 3 | Verify DB has 80 fees for IGCSE Science | `SELECT COUNT(*) WHERE program='IGCSE Science'` = 80 | ☐ Pass / ☐ Fail |
| 4 | Bill "IGCSE Commerce" | Results: "80 created, 0 skipped, 0 failed" | ☐ Pass / ☐ Fail |
| 5 | Verify total fees now = 160 | DB has 80 Science + 80 Commerce | ☐ Pass / ☐ Fail |
| 6 | Bill "O-Level Math" | Results: "80 created, 0 skipped, 0 failed" | ☐ Pass / ☐ Fail |
| 7 | Verify total = 240 fees | DB has 80 + 80 + 80 = 240 | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 2.9: Missing Rates Error
**Objective:** Verify error handling when billing rates not configured

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Delete billing rate for "IGCSE Science + Day Boarder" | Rate deleted | ☐ Pass / ☐ Fail |
| 2 | Try to bill "IGCSE Science" | Preview shows 30 students (only full boarders, day boarders skipped) | ☐ Pass / ☐ Fail |
| 3 | Execute billing | Results: "30 created, 50 skipped, 0 failed" (no rates for day boarders) | ☐ Pass / ☐ Fail |
| 4 | Re-add missing rate | Rate created | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 2.10: Invalid Academic Term
**Objective:** Verify error when selecting non-existent term

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Try to manually pass invalid term via API | API call fails with clear error | ☐ Pass / ☐ Fail |
| 2 | Check error message | Shows "Academic Term 'Invalid Term' not found" | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 2.11: Performance — Large Scale
**Objective:** Verify performance with 500+ students

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Create 5 programs × 100 students each = 500 students | Setup complete | ☐ Pass / ☐ Fail |
| 2 | Configure rates for all 5 programs | Rates set | ☐ Pass / ☐ Fail |
| 3 | Bill all 500 students | Operation completes in <10 seconds | ☐ Pass / ☐ Fail |
| 4 | Check results | "500 created, 0 skipped, 0 failed" | ☐ Pass / ☐ Fail |
| 5 | Verify all 500 fees in DB | Count = 500 | ☐ Pass / ☐ Fail |

**Time taken:** _____ seconds  
**Notes:** _______________________________

---

### Test 2.12: Transaction Rollback (Error Handling)
**Objective:** Verify all-or-nothing semantics on error

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Setup: Break Student Fee doctype by removing required field | Doctype modified | ☐ Pass / ☐ Fail |
| 2 | Try to bill students | Billing fails partway through | ☐ Pass / ☐ Fail |
| 3 | Check fees created in DB | No partial fees: either all created or none | ☐ Pass / ☐ Fail |
| 4 | Restore Student Fee doctype | Doctype restored | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 2.13: UI Responsiveness
**Objective:** Verify page works on mobile/tablet

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Open page on mobile (375px width) | Page renders without overflow | ☐ Pass / ☐ Fail |
| 2 | Check dropdowns on mobile | Touch-friendly, clickable | ☐ Pass / ☐ Fail |
| 3 | Check buttons on mobile | Buttons are sized appropriately | ☐ Pass / ☐ Fail |
| 4 | Check preview modal on mobile | Modal fits screen, scrollable if needed | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 2.14: Edge Case — No Students Enrolled
**Objective:** Verify graceful handling when no students match criteria

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Create a new empty program (no students) | Program created | ☐ Pass / ☐ Fail |
| 2 | Configure rates for empty program | Rates set | ☐ Pass / ☐ Fail |
| 3 | Try to bill empty program | Preview shows "0 students" | ☐ Pass / ☐ Fail |
| 4 | Try to execute billing | Results: "0 created, 0 skipped, 0 failed" | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 2.15: Browser Compatibility
**Objective:** Verify page works across browsers

| Browser | Version | Status | Notes |
|---------|---------|--------|-------|
| Chrome | Latest | ☐ Pass / ☐ Fail | |
| Firefox | Latest | ☐ Pass / ☐ Fail | |
| Safari | Latest | ☐ Pass / ☐ Fail | |
| Edge | Latest | ☐ Pass / ☐ Fail | |

---

## Summary

| Test Group | Total | Passed | Failed | Notes |
|-----------|-------|--------|--------|-------|
| Access Control | 5 | ☐ | ☐ | |
| Form Loading | 4 | ☐ | ☐ | |
| Preview | 8 | ☐ | ☐ | |
| Filters | 6 | ☐ | ☐ | |
| Execution | 7 | ☐ | ☐ | |
| Duplicates | 6 | ☐ | ☐ | |
| Error Handling | 4 | ☐ | ☐ | |
| Performance | 5 | ☐ | ☐ | |
| UI/UX | 4 | ☐ | ☐ | |
| **TOTAL** | **49** | **☐** | **☐** | |

---

## Sign-Off

**Feature #2 (Batch Billing) Ready for Production?** 

☐ **YES** — All tests passed, feature is production-ready  
☐ **NO** — Issues found, needs fixes:

_____________________________

**Tester Name:** ______________________  
**Date:** ______________________  
**Signature:** ______________________

---

**Document Version:** 1.0  
**Last Updated:** July 5, 2026
