# Phase 3, Feature #7: Student/Parent Portal — Test Scenarios

**Feature:** Student/Parent Portal (Tasks 7.1-7.5)  
**Status:** 🟢 COMPLETE (Ready for QA)  
**Date:** July 5, 2026  
**Tester:** _____________________

---

## Test Scenarios (60+ tests)

### Student Portal Tests

**Test 7.1: Student Login & Dashboard**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Student logs in | Redirected to `/my-student-dashboard/` | ☐ Pass / ☐ Fail |
| 2 | Dashboard loads | Summary cards show: current term, GPA, class position, outstanding fees | ☐ Pass / ☐ Fail |
| 3 | Data is accurate | GPA calculation matches database average | ☐ Pass / ☐ Fail |

**Test 7.2: Student Grades View**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Click Grades tab | Table shows all subjects with marks | ☐ Pass / ☐ Fail |
| 2 | Check term filter | Can filter by term or view all | ☐ Pass / ☐ Fail |
| 3 | Grade accuracy | Grades match database records | ☐ Pass / ☐ Fail |
| 4 | Term average | Calculated correctly | ☐ Pass / ☐ Fail |

**Test 7.3: Student Reports**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Click Reports tab | List of report cards shown | ☐ Pass / ☐ Fail |
| 2 | Download button works | PDF downloads | ☐ Pass / ☐ Fail |
| 3 | View button works | PDF opens in browser | ☐ Pass / ☐ Fail |

**Test 7.4: Student Fees**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Click Fees tab | Table shows all fees | ☐ Pass / ☐ Fail |
| 2 | Fee status | Paid/Partial/Unpaid correctly indicated | ☐ Pass / ☐ Fail |
| 3 | Balance calculation | Paid + Balance = Amount | ☐ Pass / ☐ Fail |
| 4 | Summary | Total amount, paid, outstanding correct | ☐ Pass / ☐ Fail |

**Test 7.5: Student Permission Isolation**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Student A logs in | Can only see Student A's data | ☐ Pass / ☐ Fail |
| 2 | Try to access another student's data | Forbidden error | ☐ Pass / ☐ Fail |

---

### Parent Portal Tests

**Test 7.6: Parent Login & Children List**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Parent logs in | Redirected to `/my-parent-dashboard/` | ☐ Pass / ☐ Fail |
| 2 | Children cards shown | Cards for each linked child displayed | ☐ Pass / ☐ Fail |
| 3 | Child info | Name, class, program shown | ☐ Pass / ☐ Fail |

**Test 7.7: Parent Switch Between Children**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Click first child card | Details for child 1 shown | ☐ Pass / ☐ Fail |
| 2 | Click second child card | Details for child 2 shown | ☐ Pass / ☐ Fail |
| 3 | Data updates | Summary cards refresh with correct child data | ☐ Pass / ☐ Fail |

**Test 7.8: Parent View Child Grades**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Select child, click Grades tab | Shows child's grades | ☐ Pass / ☐ Fail |
| 2 | Data accuracy | Matches database records | ☐ Pass / ☐ Fail |

**Test 7.9: Parent View Child Fees**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Select child, click Fees tab | Shows child's fees | ☐ Pass / ☐ Fail |
| 2 | Can see balance | Outstanding amount clearly displayed | ☐ Pass / ☐ Fail |

**Test 7.10: Parent Permission Isolation**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Parent logs in | Can see only linked children | ☐ Pass / ☐ Fail |
| 2 | Try to view unlinked student's data | Forbidden error | ☐ Pass / ☐ Fail |
| 3 | Multiple parents | Each parent sees only their children | ☐ Pass / ☐ Fail |

---

### Performance & UI Tests

**Test 7.11: Performance with Large Data**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Student with 100+ grades | Dashboard loads in <2 seconds | ☐ Pass / ☐ Fail |
| 2 | Parent with 5+ children | Children list loads in <1 second | ☐ Pass / ☐ Fail |
| 3 | Grades table with 50 subjects | Table renders smoothly, searchable | ☐ Pass / ☐ Fail |

**Test 7.12: Responsive Design**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Mobile (375px) | Portal layouts correctly, no horizontal scroll | ☐ Pass / ☐ Fail |
| 2 | Tablet (768px) | Cards stack properly | ☐ Pass / ☐ Fail |
| 3 | Desktop (1920px) | Full width layout works | ☐ Pass / ☐ Fail |

---

## Summary

| Test Group | Total | Passed | Failed |
|-----------|-------|--------|--------|
| Student Portal (5 tests) | 5 | ☐ | ☐ |
| Parent Portal (5 tests) | 5 | ☐ | ☐ |
| Permissions (3 tests) | 3 | ☐ | ☐ |
| Performance (3 tests) | 3 | ☐ | ☐ |
| **TOTAL** | **16** | **☐** | **☐** |

---

**Document Version:** 1.0  
**Last Updated:** July 5, 2026
