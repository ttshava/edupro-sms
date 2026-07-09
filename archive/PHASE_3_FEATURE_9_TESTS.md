# Phase 3, Feature #9: Advanced Analytics — Test Scenarios

**Feature:** Advanced Analytics (Tasks 9.1-9.5)  
**Status:** 🟢 COMPLETE (Ready for QA)  
**Date:** July 5, 2026  
**Tester:** _____________________

---

## Test Scenarios (40+ tests)

### Analytics API Tests

**Test 9.1: Academic Trends**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Call get_academic_trends(year) | Returns array of trends by term | ☐ Pass / ☐ Fail |
| 2 | Check calculation | Class average = sum of marks / count | ☐ Pass / ☐ Fail |
| 3 | Verify sort | Trends ordered by term start date | ☐ Pass / ☐ Fail |

**Test 9.2: At-Risk Students**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Call get_at_risk_students() | Returns students below threshold | ☐ Pass / ☐ Fail |
| 2 | Check threshold | Only students <50% included | ☐ Pass / ☐ Fail |
| 3 | Verify accuracy | Spot-check calculations match DB | ☐ Pass / ☐ Fail |

**Test 9.3: Performance Alerts**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Call get_performance_alerts() | Returns improving/declining/at-risk | ☐ Pass / ☐ Fail |
| 2 | Check improving | 20+ point increase detected | ☐ Pass / ☐ Fail |
| 3 | Check declining | 20+ point decrease detected | ☐ Pass / ☐ Fail |

**Test 9.4: Subject Comparison**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Call get_subject_comparison() | Returns all subjects with stats | ☐ Pass / ☐ Fail |
| 2 | Check average calculation | Correct average per subject | ☐ Pass / ☐ Fail |
| 3 | Grade distribution | Count of A/B/C/D/E per subject | ☐ Pass / ☐ Fail |

**Test 9.5: Grade Predictions**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Call predict_final_grades(student) | Returns predicted grade | ☐ Pass / ☐ Fail |
| 2 | Check prediction logic | Grade based on current average | ☐ Pass / ☐ Fail |
| 3 | Confidence score | Returns 0.5-1.0 confidence | ☐ Pass / ☐ Fail |

---

### Dashboard UI Tests

**Test 9.6: Analytics Dashboard Load**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Headmaster visits `/headmaster-analytics/` | Page loads with filters | ☐ Pass / ☐ Fail |
| 2 | Select academic year | Year dropdown populated | ☐ Pass / ☐ Fail |
| 3 | Click Load Analytics | Charts and tables populate | ☐ Pass / ☐ Fail |

**Test 9.7: Trends Chart**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Load analytics | Trends line chart appears | ☐ Pass / ☐ Fail |
| 2 | Check data | X-axis shows terms, Y-axis shows % | ☐ Pass / ☐ Fail |
| 3 | Hover on point | Tooltip shows exact average | ☐ Pass / ☐ Fail |

**Test 9.8: Subject Comparison Chart**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Load analytics | Subject bar chart appears | ☐ Pass / ☐ Fail |
| 2 | Check bars | One bar per subject | ☐ Pass / ☐ Fail |
| 3 | Verify scale | Y-axis 0-100% | ☐ Pass / ☐ Fail |

**Test 9.9: At-Risk Table**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Load analytics | At-risk students table shows | ☐ Pass / ☐ Fail |
| 2 | Check data | Only <50% students listed | ☐ Pass / ☐ Fail |
| 3 | Action button | "Alert Teacher" button present | ☐ Pass / ☐ Fail |

**Test 9.10: Performance Alerts**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Load analytics | Two cards: Improving & Declining | ☐ Pass / ☐ Fail |
| 2 | Check data | Shows improvement/decline %, names | ☐ Pass / ☐ Fail |
| 3 | Sort order | Sorted by magnitude of change | ☐ Pass / ☐ Fail |

---

### Performance & Accuracy Tests

**Test 9.11: Performance with Large Data**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Load analytics with 500+ marks | Dashboard loads in <5 seconds | ☐ Pass / ☐ Fail |
| 2 | Generate charts | Charts render smoothly | ☐ Pass / ☐ Fail |

**Test 9.12: Data Accuracy**
| Step | Action | Expected | Status |
|------|--------|----------|--------|
| 1 | Spot-check trend average | Matches DB calculation | ☐ Pass / ☐ Fail |
| 2 | Spot-check at-risk count | Matches DB records <50% | ☐ Pass / ☐ Fail |
| 3 | Spot-check subject average | Matches sum of marks / count | ☐ Pass / ☐ Fail |

---

## Summary

| Test Group | Total | Passed | Failed |
|-----------|-------|--------|--------|
| API Tests (5 tests) | 5 | ☐ | ☐ |
| UI Tests (5 tests) | 5 | ☐ | ☐ |
| Performance (2 tests) | 2 | ☐ | ☐ |
| **TOTAL** | **12** | **☐** | **☐** |

---

**Document Version:** 1.0  
**Last Updated:** July 5, 2026
