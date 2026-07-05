# Phase 3: Implementation Tasks — Features #7 & #9

**Status:** 🟢 IN PROGRESS  
**Target Duration:** 2 weeks  
**Features:** #7 (Student/Parent Portal), #9 (Advanced Analytics)  
**Total Tasks:** 10  

---

## Feature #7: Student/Parent Portal (5 tasks, 5 days)

### Task 7.1: Student Portal Backend API
**Objective:** Build APIs for student to access own data  
**Status:** 🟡 READY TO START  
**Estimated:** 1.5 days

**What to Build:**
- Whitelisted method: `get_student_dashboard()`
  - Returns: student name, class, program, current term, GPA
  - Permission: Student can only see own data
- Whitelisted method: `get_student_grades(academic_term=None)`
  - Returns: [{subject, term_mark, exam_mark, grade, teacher_comment}, ...]
  - Filter by term or all terms
- Whitelisted method: `get_student_reports()`
  - Returns: list of Report Card documents (for download/preview)

**Files to Create:**
- `edupro_sms/student_portal_api.py` (API methods)

**Subtasks:**
- [ ] Get student's own grades (permission check)
- [ ] Calculate GPA from marks
- [ ] Get report cards for download
- [ ] Permission validation (can't access other students)
- [ ] Test with sample data

---

### Task 7.2: Parent/Guardian Portal Backend API
**Objective:** Build APIs for parent to access linked children's data  
**Status:** 🟡 READY TO START  
**Estimated:** 1.5 days

**What to Build:**
- Whitelisted method: `get_guardian_dashboard()`
  - Returns: list of linked children with basic info
- Whitelisted method: `get_child_grades(student_id, academic_term=None)`
  - Returns: grades for specified child
  - Permission: Guardian can only see linked children
- Whitelisted method: `get_child_reports(student_id)`
  - Returns: report cards for child
- Whitelisted method: `get_child_fees(student_id)`
  - Returns: fees, payment status, balance

**Files to Create:**
- `edupro_sms/guardian_portal_api.py` (API methods)

**Subtasks:**
- [ ] Get linked children list
- [ ] Get child's grades (permission check)
- [ ] Get child's report cards
- [ ] Get child's fee status
- [ ] Permission validation (can't access unlinked children)

---

### Task 7.3: Student Portal UI
**Objective:** Build student dashboard/portal website  
**Status:** 🟡 READY TO START  
**Estimated:** 1 day

**What to Build:**
- Website page: `/my-student-dashboard/`
- Dashboard card: Current term, GPA, class position
- Grades tab: Table of subjects, marks, grades
- Reports tab: Downloadable report card PDFs
- Fees tab: Fees amount, balance, payment status
- Settings tab: Change password

**Files to Create:**
- `edupro_sms/www/student_dashboard/index.py` (context)
- `edupro_sms/www/student_dashboard/index.html` (UI)

**Subtasks:**
- [ ] Dashboard cards with key info
- [ ] Grades table with filter by term
- [ ] Report card list with download links
- [ ] Fee summary display
- [ ] Responsive design

---

### Task 7.4: Parent/Guardian Portal UI
**Objective:** Build parent dashboard for viewing children's data  
**Status:** 🟡 READY TO START  
**Estimated:** 1 day

**What to Build:**
- Website page: `/my-parent-dashboard/`
- Dashboard: Cards for each linked child
- Child selector: Dropdown or tabs to switch children
- Show selected child's: Grades, reports, fees
- Same tabs as student portal (Grades, Reports, Fees)

**Files to Create:**
- `edupro_sms/www/parent_dashboard/index.py` (context)
- `edupro_sms/www/parent_dashboard/index.html` (UI)

**Subtasks:**
- [ ] Child selector with linked children
- [ ] Display selected child's grades
- [ ] Display selected child's reports
- [ ] Display selected child's fees
- [ ] Responsive design

---

### Task 7.5: Feature #7 Testing & Documentation
**Objective:** Test portals & document for users  
**Status:** 🟡 READY TO START  
**Estimated:** 0.5 days

**Subtasks:**
- [ ] Test student login and data access
- [ ] Test parent login and child data access
- [ ] Test permission isolation (can't see other data)
- [ ] Test with 100+ grades (performance)
- [ ] Update USER_QUICKSTART.md with portal guides

---

## Feature #9: Advanced Analytics (5 tasks, 5 days)

### Task 9.1: Analytics Calculations API — Trends & Predictions
**Objective:** Build backend for analytics calculations  
**Status:** 🟡 READY TO START  
**Estimated:** 1.5 days

**What to Build:**
- Whitelisted method: `get_academic_trends(academic_year=None, program=None)`
  - Returns: [{term, class_average, highest, lowest}, ...]
  - Shows progression of class averages over terms
- Whitelisted method: `get_performance_alerts(program=None)`
  - Returns: [{student, trend: "improving"/"declining"/"at_risk", detail}, ...]
  - Identifies students with significant grade changes
- Whitelisted method: `get_subject_comparison(academic_term, program)`
  - Returns: [{subject, average, distribution}, ...]
  - Compare performance across subjects
- Whitelisted method: `predict_final_grades(student_id)`
  - Returns: {predicted_grade, confidence, current_average, trend}
  - Simple linear regression for grade prediction

**Files to Create:**
- `edupro_sms/analytics_api.py` (API methods)

**Subtasks:**
- [ ] Calculate class averages by term
- [ ] Detect improving/declining trends
- [ ] Identify at-risk students
- [ ] Compare subject performance
- [ ] Implement grade prediction algorithm
- [ ] Test with sample data

---

### Task 9.2: Analytics Data Aggregation & Caching
**Objective:** Aggregate and cache analytics data for performance  
**Status:** 🟡 READY TO START  
**Estimated:** 1.5 days

**What to Build:**
- Cache analytics calculations (expensive queries)
- Methods for: grade distribution by program, class comparison, term trends
- Helper functions for: percentile calculation, trend detection, outlier identification

**Files to Create/Modify:**
- `edupro_sms/analytics_api.py` (add caching)

**Subtasks:**
- [ ] Grade distribution calculations (by program, class, term)
- [ ] Trend detection (improving, declining, stable)
- [ ] Outlier identification (high performers, struggling)
- [ ] Performance optimization (cache results)
- [ ] Test with 500+ students

---

### Task 9.3: Analytics Dashboard UI
**Objective:** Build analytics dashboard for Headmaster  
**Status:** 🟡 READY TO START  
**Estimated:** 1 day

**What to Build:**
- Website page: `/headmaster-analytics/`
- Trends chart: Class averages over time (line chart)
- Subject comparison: Performance by subject (bar chart)
- Grade distribution: A/B/C/D/E breakdown (pie chart)
- At-risk students: Table of students with declining grades
- High performers: Recognition of top students
- Alerts: Red flags for attention (failing subjects, etc.)

**Files to Create:**
- `edupro_sms/www/headmaster_analytics/index.py` (context)
- `edupro_sms/www/headmaster_analytics/index.html` (UI + Chart.js)

**Subtasks:**
- [ ] Trends line chart (class avg over terms)
- [ ] Subject comparison bar chart
- [ ] Grade distribution pie chart
- [ ] At-risk students table
- [ ] High performers list
- [ ] Performance alerts section

---

### Task 9.4: Advanced Features — Predictions & Comparisons
**Objective:** Add predictive analytics and cross-class comparisons  
**Status:** 🟡 READY TO START  
**Estimated:** 1 day

**What to Build:**
- Grade projections for end-of-year
- Class ranking (which class performing best)
- Program comparison (IGCSE vs O-Level performance)
- Individual student predictions (will student pass?)

**Files to Create/Modify:**
- `edupro_sms/analytics_api.py` (add prediction methods)
- `edupro_sms/www/headmaster_analytics/index.html` (add UI for predictions)

**Subtasks:**
- [ ] Implement grade projection (if current trend continues)
- [ ] Class ranking calculation
- [ ] Program performance comparison
- [ ] Student success prediction
- [ ] Add to dashboard

---

### Task 9.5: Feature #9 Testing & Documentation
**Objective:** Test analytics & document for users  
**Status:** 🟡 READY TO START  
**Estimated:** 0.5 days

**Subtasks:**
- [ ] Test trend calculations accuracy
- [ ] Test alert detection (at-risk students)
- [ ] Test predictions (compare to actual results)
- [ ] Test performance (1000+ students)
- [ ] Create ANALYTICS_GUIDE.md with interpretation guide

---

## 📊 Overall Task Summary

| Phase | Task | Days | Status |
|-------|------|------|--------|
| #7 | 7.1 Student API | 1.5 | 🟡 Ready |
| #7 | 7.2 Guardian API | 1.5 | 🟡 Ready |
| #7 | 7.3 Student UI | 1 | 🟡 Ready |
| #7 | 7.4 Parent UI | 1 | 🟡 Ready |
| #7 | 7.5 Testing & Docs | 0.5 | 🟡 Ready |
| #9 | 9.1 Analytics API | 1.5 | 🟡 Ready |
| #9 | 9.2 Data Aggregation | 1.5 | 🟡 Ready |
| #9 | 9.3 Dashboard UI | 1 | 🟡 Ready |
| #9 | 9.4 Predictions | 1 | 🟡 Ready |
| #9 | 9.5 Testing & Docs | 0.5 | 🟡 Ready |
| **TOTAL** | | **10 days** | **🟢 Ready to Start** |

---

**Document Version:** 1.0  
**Date:** July 5, 2026  
**Status:** 🟢 READY FOR IMPLEMENTATION
