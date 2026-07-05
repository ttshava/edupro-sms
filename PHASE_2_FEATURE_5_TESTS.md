# Phase 2, Feature #5: Batch Report Card Printing — Test Scenarios

**Feature:** Batch Report Card Printing (Tasks 5.1, 5.2)  
**Status:** 🟢 COMPLETE (Ready for QA)  
**Date:** July 5, 2026  
**Tester:** _____________________

---

## Test Environment Setup

### Prerequisites
- 50+ Published Report Cards across multiple classes/groups
- Multiple Student Groups (Form 1A, Form 1B, Form 2A, etc.)
- Multiple Academic Terms
- Report Cards with varying content (different number of subjects)
- System has PyPDF2 library installed (for PDF merging)
- PDF generation is working (test with single report first)

---

## Test Scenarios

### Test 5.1: Access Control
**Objective:** Verify only authorized roles can access batch print page

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Log in as Teacher, visit `/headmaster-batch-print/` | Permission error (forbidden) | ☐ Pass / ☐ Fail |
| 2 | Log in as Bursar, visit `/headmaster-batch-print/` | Permission error (forbidden) | ☐ Pass / ☐ Fail |
| 3 | Log in as Student, visit `/headmaster-batch-print/` | Permission error (forbidden) | ☐ Pass / ☐ Fail |
| 4 | Log in as Headmaster, visit `/headmaster-batch-print/` | Page loads successfully | ☐ Pass / ☐ Fail |
| 5 | Log in as System Manager, visit `/headmaster-batch-print/` | Page loads successfully | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 5.2: Page Load & Form Display
**Objective:** Verify form loads with correct options

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Page loads | Form displays with all fields | ☐ Pass / ☐ Fail |
| 2 | Check Student Group dropdown | "All Classes" + all student groups listed | ☐ Pass / ☐ Fail |
| 3 | Check Academic Term dropdown | All active terms listed, required field marked | ☐ Pass / ☐ Fail |
| 4 | Check "Include published only" checkbox | Checkbox is checked by default | ☐ Pass / ☐ Fail |
| 5 | Check buttons | Preview and Generate buttons present | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 5.3: Preview Functionality
**Objective:** Verify preview shows correct counts without making changes

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Select "Form 1A" + "Term 1 2026" + "Published only" | Form is valid | ☐ Pass / ☐ Fail |
| 2 | Click "Preview" button | Preview modal opens with loading spinner | ☐ Pass / ☐ Fail |
| 3 | Wait for preview to load | Modal shows report count, pages, file size | ☐ Pass / ☐ Fail |
| 4 | Check report count | Shows actual number of Form 1A reports for Term 1 | ☐ Pass / ☐ Fail |
| 5 | Check page estimate | Pages ≈ report count (1 page per report estimate) | ☐ Pass / ☐ Fail |
| 6 | Check file size estimate | Shows ~200KB per report estimate | ☐ Pass / ☐ Fail |
| 7 | Check preview list | Shows first 5 students | ☐ Pass / ☐ Fail |
| 8 | Click "Cancel" in modal | Modal closes, no PDF generated, form untouched | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 5.4: Generate PDF
**Objective:** Verify PDF generation works and file is created

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Select "Form 1A" + "Term 1 2026" + Published | Preview modal shows correct count | ☐ Pass / ☐ Fail |
| 2 | Click "Generate PDF" in modal | Progress modal appears | ☐ Pass / ☐ Fail |
| 3 | Monitor progress | Progress bar moves from 0% → 100% | ☐ Pass / ☐ Fail |
| 4 | Check progress messages | Shows "Generating...", "Merging...", "Finalizing..." | ☐ Pass / ☐ Fail |
| 5 | Wait for completion | After 100%, results modal appears | ☐ Pass / ☐ Fail |
| 6 | Check success message | Shows "Successfully merged X report cards (Y pages)" | ☐ Pass / ☐ Fail |
| 7 | Check Download button | Button is present and clickable | ☐ Pass / ☐ Fail |
| 8 | Click Download button | Browser downloads PDF file | ☐ Pass / ☐ Fail |
| 9 | Check file name | Includes class name, term, timestamp | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 5.5: PDF Content Quality
**Objective:** Verify merged PDF is valid and contains all reports

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Download PDF from completed generation | File downloads without errors | ☐ Pass / ☐ Fail |
| 2 | Open PDF in viewer | PDF opens and displays correctly | ☐ Pass / ☐ Fail |
| 3 | Check page count | Total pages ≈ # of reports | ☐ Pass / ☐ Fail |
| 4 | Check first report | Shows complete report with student name, subjects, marks | ☐ Pass / ☐ Fail |
| 5 | Check middle report | Random report in middle displays correctly | ☐ Pass / ☐ Fail |
| 6 | Check last report | Last report in PDF is complete | ☐ Pass / ☐ Fail |
| 7 | Check page order | Reports are in correct order (alphabetical by student) | ☐ Pass / ☐ Fail |
| 8 | Try to print | Can print directly from PDF viewer | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 5.6: All Classes/All Terms Filter
**Objective:** Verify "All Classes" and filtering works

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Select "All Classes" + "Term 1 2026" + Published | Preview shows all reports for term | ☐ Pass / ☐ Fail |
| 2 | Check count | Count = sum of all classes for that term | ☐ Pass / ☐ Fail |
| 3 | Generate PDF | Merging takes longer (all classes included) | ☐ Pass / ☐ Fail |
| 4 | Check result | PDF includes reports from all classes | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 5.7: Published vs. Draft Reports Filter
**Objective:** Verify status filter works correctly

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Check "Include published only" + Select Form 1A + Term 1 | Preview shows only published reports | ☐ Pass / ☐ Fail |
| 2 | Uncheck "Include published only" | Check should be empty | ☐ Pass / ☐ Fail |
| 3 | Click Preview | Preview shows published + draft reports | ☐ Pass / ☐ Fail |
| 4 | Count should be higher | Include drafts increases count | ☐ Pass / ☐ Fail |
| 5 | Generate PDF | Works with both published and draft reports | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 5.8: Multiple Sequential Generations
**Objective:** Verify can generate multiple PDFs in sequence

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Generate PDF for "Form 1A" | PDF1 created successfully | ☐ Pass / ☐ Fail |
| 2 | Click "Generate Another PDF" button | Form resets, new selection ready | ☐ Pass / ☐ Fail |
| 3 | Generate PDF for "Form 1B" | PDF2 created successfully | ☐ Pass / ☐ Fail |
| 4 | Verify both PDFs exist | Both files downloaded and valid | ☐ Pass / ☐ Fail |
| 5 | Generate same criteria again ("Form 1A") | New PDF created (different timestamp) | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 5.9: Large Batch Performance
**Objective:** Verify performance with 50+ reports

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Select "All Classes" + "Term 1 2026" for 50+ reports | Preview loads in <2 seconds | ☐ Pass / ☐ Fail |
| 2 | Generate PDF with 50 reports | Progress bar displays, doesn't freeze | ☐ Pass / ☐ Fail |
| 3 | Monitor generation time | Completes in <60 seconds | ☐ Pass / ☐ Fail |
| 4 | Check resulting file | PDF opens and displays all 50 reports | ☐ Pass / ☐ Fail |
| 5 | File size reasonable? | ~10MB for 50 reports (size depends on images) | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 5.10: Error Handling
**Objective:** Verify graceful error handling

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Select term with zero reports | Preview shows "0 report cards" | ☐ Pass / ☐ Fail |
| 2 | Try to generate | Error message: "No report cards found" | ☐ Pass / ☐ Fail |
| 3 | Select term without reports | Preview shows count 0 | ☐ Pass / ☐ Fail |
| 4 | Network interruption during generation | Error displayed, user can retry | ☐ Pass / ☐ Fail |
| 5 | Report missing attachment | PDF generation handles gracefully | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 5.11: UI Responsiveness
**Objective:** Verify page works on different screen sizes

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Open on mobile (375px) | Page renders without horizontal scroll | ☐ Pass / ☐ Fail |
| 2 | Check form on mobile | Dropdowns and buttons are touch-friendly | ☐ Pass / ☐ Fail |
| 3 | Check modal on mobile | Modals fit screen, content scrollable | ☐ Pass / ☐ Fail |
| 4 | Check progress bar on mobile | Progress bar visible and updates smoothly | ☐ Pass / ☐ Fail |
| 5 | Check results on mobile | Download button prominent and clickable | ☐ Pass / ☐ Fail |
| 6 | Test on tablet (768px) | All elements properly displayed | ☐ Pass / ☐ Fail |
| 7 | Test on desktop (1920px) | Full layout with good spacing | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

### Test 5.12: File Download & Management
**Objective:** Verify PDF files are accessible and downloadable

| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Generate PDF | File URL provided in results | ☐ Pass / ☐ Fail |
| 2 | Click Download button | File downloads with correct name | ☐ Pass / ☐ Fail |
| 3 | Open in new browser tab | PDF opens in browser | ☐ Pass / ☐ Fail |
| 4 | Right-click file link | Can save as different name | ☐ Pass / ☐ Fail |
| 5 | Check file location | File accessible in browser downloads folder | ☐ Pass / ☐ Fail |
| 6 | Check file permissions | File is readable/printable | ☐ Pass / ☐ Fail |

**Notes:** _______________________________

---

## Summary

| Test Group | Total | Passed | Failed | Notes |
|-----------|-------|--------|--------|-------|
| Access Control | 5 | ☐ | ☐ | |
| Page Load | 5 | ☐ | ☐ | |
| Preview | 8 | ☐ | ☐ | |
| PDF Generation | 9 | ☐ | ☐ | |
| PDF Content | 8 | ☐ | ☐ | |
| Filtering | 4 | ☐ | ☐ | |
| Status Filter | 5 | ☐ | ☐ | |
| Sequential Ops | 5 | ☐ | ☐ | |
| Performance | 5 | ☐ | ☐ | |
| Error Handling | 5 | ☐ | ☐ | |
| UI/UX | 7 | ☐ | ☐ | |
| Downloads | 6 | ☐ | ☐ | |
| **TOTAL** | **72** | **☐** | **☐** | |

---

## Sign-Off

**Feature #5 (Batch Report Card Printing) Ready for Production?**

☐ **YES** — All tests passed, feature is production-ready  
☐ **NO** — Issues found, needs fixes:

_____________________________

**Tester Name:** ______________________  
**Date:** ______________________  
**Signature:** ______________________

---

**Document Version:** 1.0  
**Last Updated:** July 5, 2026
