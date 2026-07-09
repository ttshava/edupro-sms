# Phase 2: End-to-End Integration Testing

**Objective:** Verify all 4 Phase 2 features work together seamlessly  
**Status:** 🟡 READY TO START  
**Date:** July 5, 2026  
**Tester:** _____________________

---

## End-to-End Test Scenarios

### Scenario 1: Complete Billing Workflow
**Flow:** Batch Billing → Fee Portal → Dashboard → Batch Printing

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Go to `/bursar-billing/` | Batch billing page loads | ☐ Pass / ☐ Fail |
| 2 | Select Term 1 2026, All Programs, All Boarding | Preview shows 200+ students | ☐ Pass / ☐ Fail |
| 3 | Click "Create Fees" → Confirm | 200+ Student Fees created | ☐ Pass / ☐ Fail |
| 4 | Go to `/bursar-fees/` | Fee list shows all newly created fees | ☐ Pass / ☐ Fail |
| 5 | Search for student, click "Record Payment" | Payment modal opens | ☐ Pass / ☐ Fail |
| 6 | Record payment of $2000 | Ledger entry created, status updates | ☐ Pass / ☐ Fail |
| 7 | Go to `/headmaster-dashboard/fees/` | Dashboard shows partial collection % | ☐ Pass / ☐ Fail |
| 8 | Chart shows collection trend, unpaid students | Correct data displayed | ☐ Pass / ☐ Fail |
| 9 | Go to `/headmaster-batch-print/` | Form loads | ☐ Pass / ☐ Fail |
| 10 | Generate batch reports for Term 1 | PDF with all reports merges successfully | ☐ Pass / ☐ Fail |

**Notes:** ________________________

---

### Scenario 2: Multiple Payments Flow
**Flow:** Record multiple payments → Dashboard updates → Statement reflects changes

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Go to `/bursar-fees/`, search for student | Find fee with $5000 balance | ☐ Pass / ☐ Fail |
| 2 | Record payment $2000 | Balance → $3000, status → Partial | ☐ Pass / ☐ Fail |
| 3 | Record another payment $1500 | Balance → $1500, still Partial | ☐ Pass / ☐ Fail |
| 4 | Record final payment $1500 | Balance → $0, status → Paid | ☐ Pass / ☐ Fail |
| 5 | Go to dashboard | Collection % increased | ☐ Pass / ☐ Fail |
| 6 | Check unpaid table | Student no longer in top unpaid | ☐ Pass / ☐ Fail |
| 7 | Go back to fee portal, view statement | All payments shown | ☐ Pass / ☐ Fail |

**Notes:** ________________________

---

### Scenario 3: Multi-Program Billing
**Flow:** Batch bill different programs → Portal filters → Dashboard drill-down

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Batch bill IGCSE Science only | 80 Science fees created | ☐ Pass / ☐ Fail |
| 2 | Go to fee portal, filter by Program="IGCSE Science" | Shows only Science fees | ☐ Pass / ☐ Fail |
| 3 | Record some payments for Science students | Status updates in portal | ☐ Pass / ☐ Fail |
| 4 | Go to dashboard, filter by Program="IGCSE Science" | Dashboard updates, shows only Science totals | ☐ Pass / ☐ Fail |
| 5 | Batch bill IGCSE Commerce | 80 Commerce fees created | ☐ Pass / ☐ Fail |
| 6 | Dashboard (All Programs) now shows both | Totals = Science + Commerce | ☐ Pass / ☐ Fail |

**Notes:** ________________________

---

### Scenario 4: Report Card Generation After Marks Entry
**Flow:** Teachers enter marks → Headmaster approves reports → Batch print

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Verify Report Cards exist in system | List shows 50+ reports | ☐ Pass / ☐ Fail |
| 2 | Go to `/headmaster-batch-print/` | Class dropdown shows all classes | ☐ Pass / ☐ Fail |
| 3 | Select Form 1A + Term 1 2026 + Published only | Preview shows ~25 reports | ☐ Pass / ☐ Fail |
| 4 | Generate PDF | Single merged PDF with all 25 reports | ☐ Pass / ☐ Fail |
| 5 | Download and verify PDF | All 25 report cards visible, correct order | ☐ Pass / ☐ Fail |
| 6 | Generate again for Form 1B | Different PDF with Form 1B reports | ☐ Pass / ☐ Fail |

**Notes:** ________________________

---

### Scenario 5: Dashboard Data Consistency
**Flow:** Verify dashboard calculations match actual data

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Batch bill 100 students $5000 each | Total Billed = $500,000 | ☐ Pass / ☐ Fail |
| 2 | Record $200,000 in total payments | Total Collected = $200,000 | ☐ Pass / ☐ Fail |
| 3 | Go to dashboard for that term | Summary cards show: Billed=$500K, Collected=$200K | ☐ Pass / ☐ Fail |
| 4 | Outstanding = $500K - $200K = $300K | Dashboard shows $300,000 | ☐ Pass / ☐ Fail |
| 5 | Collection % = $200K/$500K = 40% | Dashboard shows 40% | ☐ Pass / ☐ Fail |
| 6 | Query database directly | Dashboard numbers match DB totals | ☐ Pass / ☐ Fail |

**Notes:** ________________________

---

### Scenario 6: Permission Isolation
**Flow:** Verify role-based access across all features

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Log in as Teacher, try `/bursar-billing/` | Access denied | ☐ Pass / ☐ Fail |
| 2 | Log in as Teacher, try `/bursar-fees/` | Access denied | ☐ Pass / ☐ Fail |
| 3 | Log in as Bursar, try `/headmaster-dashboard/fees/` | Access denied | ☐ Pass / ☐ Fail |
| 4 | Log in as Bursar, try `/headmaster-batch-print/` | Access denied | ☐ Pass / ☐ Fail |
| 5 | Log in as Bursar, access `/bursar-billing/` + `/bursar-fees/` | Both work | ☐ Pass / ☐ Fail |
| 6 | Log in as Headmaster, access dashboard + batch print | Both work | ☐ Pass / ☐ Fail |

**Notes:** ________________________

---

### Scenario 7: Data Integrity & Rollback
**Flow:** Verify transaction safety across features

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Batch bill 100 students | All 100 Student Fees created | ☐ Pass / ☐ Fail |
| 2 | Stop process mid-payment recording (network error) | Transaction rolls back, data consistent | ☐ Pass / ☐ Fail |
| 3 | Check database | No partial/orphaned records | ☐ Pass / ☐ Fail |
| 4 | Record payment again | Works correctly, completes | ☐ Pass / ☐ Fail |

**Notes:** ________________________

---

### Scenario 8: Performance Under Load
**Flow:** Test all features with large datasets

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Batch bill 500 students | Completes in <10 seconds | ☐ Pass / ☐ Fail |
| 2 | Fee portal loads 500+ fees | Page loads in <3 seconds | ☐ Pass / ☐ Fail |
| 3 | Search in fee portal | Results appear in <1 second | ☐ Pass / ☐ Fail |
| 4 | Dashboard with 500+ fees | Loads in <3 seconds, charts render | ☐ Pass / ☐ Fail |
| 5 | Batch print 50 reports | Merges in <60 seconds | ☐ Pass / ☐ Fail |
| 6 | No UI lag or freezing | All operations responsive | ☐ Pass / ☐ Fail |

**Notes:** ________________________

---

### Scenario 9: Concurrent Operations
**Flow:** Verify features work when used simultaneously

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | User A: Batch billing in progress | Process continues | ☐ Pass / ☐ Fail |
| 2 | User B: Fee portal viewing/editing | Works without blocking | ☐ Pass / ☐ Fail |
| 3 | User C: Dashboard loading data | Gets current data, not stale | ☐ Pass / ☐ Fail |
| 4 | All operations complete successfully | No data corruption, no conflicts | ☐ Pass / ☐ Fail |

**Notes:** ________________________

---

## Sign-Off

**Phase 2 Integration Testing Complete?**

☐ **YES** — All end-to-end scenarios passed  
☐ **NO** — Issues found:

_____________________________

**Tester Name:** ______________________  
**Date:** ______________________

---

**Document Version:** 1.0  
**Last Updated:** July 5, 2026
