# Phase 2, Feature #3: Fee Entry Portal — Test Scenarios

**Feature:** Bursar Fee Entry Portal (Tasks 3.1, 3.2, 3.3)  
**Status:** 🟢 COMPLETE (Ready for QA)  
**Date:** July 5, 2026  
**Tester:** _____________________

---

## Test Environment Setup

### Prerequisites
- 200+ Student Fees created (from batch billing or manually)
- Multiple Programs: IGCSE Science, IGCSE Commerce, O-Level Math
- Multiple Academic Terms
- Mix of fee statuses: Unpaid (60%), Partial (30%), Paid (10%)
- Student Ledger Entry records for partial payments

---

## Test Scenarios

### Test 3.1: Access Control
**Objective:** Verify only authorized roles can access fee portal

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Log in as Teacher, visit `/bursar-fees/` | Permission error (forbidden) | ☐ Pass / ☐ Fail |
| 2 | Log in as Student, visit `/bursar-fees/` | Permission error (forbidden) | ☐ Pass / ☐ Fail |
| 3 | Log in as Bursar, visit `/bursar-fees/` | Page loads successfully | ☐ Pass / ☐ Fail |
| 4 | Log in as Headmaster, visit `/bursar-fees/` | Page loads successfully | ☐ Pass / ☐ Fail |
| 5 | Log in as System Manager, visit `/bursar-fees/` | Page loads successfully | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 3.2: Page Load & Display
**Objective:** Verify page loads with correct data

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Load page, wait for data | Table shows first 20 fees (pagination default) | ☐ Pass / ☐ Fail |
| 2 | Check table headers | Headers: Student, Admission #, Email, Program, Term, Amount, Status, Due Date, Balance, Actions | ☐ Pass / ☐ Fail |
| 3 | Check data displayed | Student names, amounts, statuses all populated | ☐ Pass / ☐ Fail |
| 4 | Check status badges | Color coding: Red (Unpaid), Yellow (Partial), Green (Paid) | ☐ Pass / ☐ Fail |
| 5 | Check summary info | Shows "Showing 20 of 200 fees" (or actual count) | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 3.3: Search Functionality
**Objective:** Verify real-time search by student name, email, admission #

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Type "John" in search box | Table filters to show only students with "John" in name | ☐ Pass / ☐ Fail |
| 2 | Clear search, type email "john@school" | Table filters to show only that email | ☐ Pass / ☐ Fail |
| 3 | Clear search, type admission "ADM-001" | Table filters to show only that admission # | ☐ Pass / ☐ Fail |
| 4 | Search for non-existent "XYZ123" | Table shows "No fees found" message | ☐ Pass / ☐ Fail |
| 5 | Clear search box | Table resets to show all fees | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 3.4: Filter by Program
**Objective:** Verify program dropdown filters correctly

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Select "IGCSE Science" from Program dropdown | Table shows only IGCSE Science fees | ☐ Pass / ☐ Fail |
| 2 | Check count matches | Count shows only that program's fees | ☐ Pass / ☐ Fail |
| 3 | Switch to "IGCSE Commerce" | Table updates to show only Commerce fees | ☐ Pass / ☐ Fail |
| 4 | Select "All Programs" | Table resets to show all programs | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 3.5: Filter by Status
**Objective:** Verify status dropdown filters correctly

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Select "Unpaid" from Status dropdown | Table shows only Unpaid fees | ☐ Pass / ☐ Fail |
| 2 | Check count | Shows correct # of unpaid fees | ☐ Pass / ☐ Fail |
| 3 | Select "Partially Paid" | Table shows only Partial status fees | ☐ Pass / ☐ Fail |
| 4 | Select "Paid" | Table shows only Paid fees | ☐ Pass / ☐ Fail |
| 5 | Select "All Status" | Table resets to all statuses | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 3.6: Filter by Term
**Objective:** Verify academic term filter works

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Select "Term 1 2026" from Term dropdown | Table shows only Term 1 fees | ☐ Pass / ☐ Fail |
| 2 | Check count | Shows correct # for selected term | ☐ Pass / ☐ Fail |
| 3 | Switch to "Term 2 2026" | Table updates to show Term 2 fees | ☐ Pass / ☐ Fail |
| 4 | Select "All Terms" | Table resets to show all terms | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 3.7: Combined Filters
**Objective:** Verify multiple filters work together

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Select Program="IGCSE Science" + Status="Unpaid" | Table shows only unpaid IGCSE Science fees | ☐ Pass / ☐ Fail |
| 2 | Add search="John" | Table narrows to John's unpaid IGCSE Science fees | ☐ Pass / ☐ Fail |
| 3 | Add Term="Term 1 2026" | Table shows only Term 1, IGCSE Science, Unpaid, John | ☐ Pass / ☐ Fail |
| 4 | Remove search (clear) | Table updates, removes search but keeps other filters | ☐ Pass / ☐ Fail |
| 5 | Click "Reset Filters" | All filters cleared, shows all fees | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 3.8: Pagination
**Objective:** Verify pagination works correctly

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Page loads with default | Shows "Page 1 of 10" (or calculated pages) | ☐ Pass / ☐ Fail |
| 2 | Click "Next" button | Page 2 loads, shows next 20 fees | ☐ Pass / ☐ Fail |
| 3 | Click "Next" again | Page 3 loads correctly | ☐ Pass / ☐ Fail |
| 4 | Click "Previous" | Goes back to Page 2 | ☐ Pass / ☐ Fail |
| 5 | Click "Previous" again | Goes back to Page 1 | ☐ Pass / ☐ Fail |
| 6 | On last page, "Next" is disabled | Cannot click next (button grayed out) | ☐ Pass / ☐ Fail |
| 7 | On first page, "Previous" is disabled | Cannot click previous (button grayed out) | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 3.9: Edit Fee
**Objective:** Verify fee editing works and updates database

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Click Edit button on a fee | Edit Fee modal opens | ☐ Pass / ☐ Fail |
| 2 | Check pre-filled data | Student name and current amount displayed | ☐ Pass / ☐ Fail |
| 3 | Enter new amount "5500" | Field accepts input | ☐ Pass / ☐ Fail |
| 4 | Click "Save Changes" | Modal closes, success message shows | ☐ Pass / ☐ Fail |
| 5 | Verify in table | Fee amount updated from 5000 to 5500 | ☐ Pass / ☐ Fail |
| 6 | Verify in database | `SELECT amount FROM \`tabStudent Fee\` WHERE name=...` shows 5500 | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 3.10: Edit Fee Status
**Objective:** Verify fee status can be changed

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Click Edit on an Unpaid fee | Modal opens with status dropdown | ☐ Pass / ☐ Fail |
| 2 | Change status to "Partially Paid" | Dropdown accepts change | ☐ Pass / ☐ Fail |
| 3 | Click "Save Changes" | Status updates in table (badge color changes to yellow) | ☐ Pass / ☐ Fail |
| 4 | Change another fee to "Paid" | Status updates correctly | ☐ Pass / ☐ Fail |
| 5 | Verify in database | Status field updated correctly | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 3.11: Record Payment
**Objective:** Verify payment recording creates ledger entries

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Click Record Payment on a fee with $5000 balance | Payment modal opens | ☐ Pass / ☐ Fail |
| 2 | Check pre-filled data | Student name, amount, balance all shown | ☐ Pass / ☐ Fail |
| 3 | Payment date auto-filled? | Today's date pre-populated | ☐ Pass / ☐ Fail |
| 4 | Enter payment amount $2000 | Field accepts input | ☐ Pass / ☐ Fail |
| 5 | Select payment method "Cash" | Dropdown works | ☐ Pass / ☐ Fail |
| 6 | Add notes "Cheque #123" | Text area accepts input | ☐ Pass / ☐ Fail |
| 7 | Click "Record Payment" | Success message: "Balance: $3000" | ☐ Pass / ☐ Fail |
| 8 | Verify fee status updated | Fee status changed from Unpaid to "Partial" | ☐ Pass / ☐ Fail |
| 9 | Verify balance updated | Balance shows $3000 (5000 - 2000) | ☐ Pass / ☐ Fail |
| 10 | Verify ledger entry created | `SELECT * FROM \`tabStudent Ledger Entry\`...` shows new entry | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 3.12: Payment Validation
**Objective:** Verify payment amounts are validated

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Open payment modal for fee with $5000 balance | Modal shows balance $5000 | ☐ Pass / ☐ Fail |
| 2 | Try to pay $6000 (more than balance) | Error: "Payment exceeds outstanding balance" | ☐ Pass / ☐ Fail |
| 3 | Try to pay $0 | Validation error or warning | ☐ Pass / ☐ Fail |
| 4 | Try to pay -$100 | Validation error (negative amount) | ☐ Pass / ☐ Fail |
| 5 | Pay exact balance $5000 | Success, fee status changes to "Paid" | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 3.13: Multiple Payments
**Objective:** Verify multiple payments on same fee work correctly

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Record first payment $2000 on $5000 fee | Balance: $3000, status: Partial | ☐ Pass / ☐ Fail |
| 2 | Record second payment $1500 | Balance: $1500, status: still Partial | ☐ Pass / ☐ Fail |
| 3 | Record third payment $1500 | Balance: $0, status: Paid | ☐ Pass / ☐ Fail |
| 4 | Verify ledger entries | 3 entries in Student Ledger Entry (2000 + 1500 + 1500) | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 3.14: View Statement
**Objective:** Verify fee statement displays correctly

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Click View Statement button | Statement modal opens | ☐ Pass / ☐ Fail |
| 2 | Check displayed info | Student name, admission #, email shown | ☐ Pass / ☐ Fail |
| 3 | Check fee details | Program, term, amount, balance, status shown | ☐ Pass / ☐ Fail |
| 4 | Click Print button | Browser print dialog opens | ☐ Pass / ☐ Fail |
| 5 | Check print preview | All info visible and formatted correctly | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 3.15: Performance
**Objective:** Verify system performance with large datasets

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Load page with 200+ fees | Page loads in <3 seconds | ☐ Pass / ☐ Fail |
| 2 | Search for student | Results appear in <1 second | ☐ Pass / ☐ Fail |
| 3 | Filter by program | Results update in <1 second | ☐ Pass / ☐ Fail |
| 4 | Open edit modal | Modal appears instantly | ☐ Pass / ☐ Fail |
| 5 | Record payment | Success response in <2 seconds | ☐ Pass / ☐ Fail |
| 6 | Navigate pages | Page switches instantly | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 3.16: UI Responsiveness
**Objective:** Verify page works on different screen sizes

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Open page on mobile (375px) | Page renders without horizontal scroll | ☐ Pass / ☐ Fail |
| 2 | Check search box on mobile | Full width, easy to tap | ☐ Pass / ☐ Fail |
| 3 | Check table on mobile | Table scrolls horizontally if needed | ☐ Pass / ☐ Fail |
| 4 | Check action buttons on mobile | Buttons are touch-friendly size | ☐ Pass / ☐ Fail |
| 5 | Check modals on mobile | Modals fit screen, scrollable content | ☐ Pass / ☐ Fail |
| 6 | Test on tablet (768px) | All elements properly displayed | ☐ Pass / ☐ Fail |
| 7 | Test on desktop (1920px) | Full layout with good spacing | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 3.17: Data Integrity
**Objective:** Verify database consistency after operations

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Edit 5 fees with different amounts | All changes saved correctly in DB | ☐ Pass / ☐ Fail |
| 2 | Record 5 payments on different fees | All ledger entries created correctly | ☐ Pass / ☐ Fail |
| 3 | Verify audit trail | All changes logged with timestamp/user | ☐ Pass / ☐ Fail |
| 4 | Check foreign key integrity | All references to Student, Term valid | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 3.18: Error Handling
**Objective:** Verify graceful error handling

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Disable network, try to edit | Error message: "Network error" or similar | ☐ Pass / ☐ Fail |
| 2 | Try to edit non-existent fee | Error message: "Fee not found" | ☐ Pass / ☐ Fail |
| 3 | Try to pay for deleted student | Error message: "Student not found" | ☐ Pass / ☐ Fail |
| 4 | Refresh page during payment | Payment completes or shows clear status | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

## Summary

| Test Group | Total | Passed | Failed | Notes |
|-----------|-------|--------|--------|-------|
| Access Control | 5 | ☐ | ☐ | |
| Page Load | 5 | ☐ | ☐ | |
| Search | 5 | ☐ | ☐ | |
| Filters | 16 | ☐ | ☐ | |
| Pagination | 7 | ☐ | ☐ | |
| Edit Fee | 6 | ☐ | ☐ | |
| Record Payment | 9 | ☐ | ☐ | |
| Statement | 5 | ☐ | ☐ | |
| Performance | 6 | ☐ | ☐ | |
| UI/UX | 7 | ☐ | ☐ | |
| Data Integrity | 4 | ☐ | ☐ | |
| Error Handling | 4 | ☐ | ☐ | |
| **TOTAL** | **79** | **☐** | **☐** | |

---

## Sign-Off

**Feature #3 (Fee Entry Portal) Ready for Production?**

☐ **YES** — All tests passed, feature is production-ready  
☐ **NO** — Issues found, needs fixes:

_____________________________

**Tester Name:** ______________________  
**Date:** ______________________  
**Signature:** ______________________

---

**Document Version:** 1.0  
**Last Updated:** July 5, 2026
