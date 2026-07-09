# Edupro SMS v1.0 — First Time Setup Guide

**After installation, follow these steps to configure your school.**

---

## 📋 Setup Checklist

- [ ] **Step 1:** Configure School Settings
- [ ] **Step 2:** Create Academic Calendar (Years & Terms)
- [ ] **Step 3:** Create Classes (Student Groups)
- [ ] **Step 4:** Create Subjects (Courses)
- [ ] **Step 5:** Create Programs (Streams: Science, Commerce, etc.)
- [ ] **Step 6:** Import Students
- [ ] **Step 7:** Import Teachers & Assign Classes
- [ ] **Step 8:** Set Up Grading Scales
- [ ] **Step 9:** Test the System

**Estimated time:** 1-2 hours (depending on data size)

---

## Step 1: Configure School Settings

**What this does:** Sets your school's name, logo, timezone, and curriculum.

1. **Log in as Administrator** and go to Desk

2. **Search for "School Settings"** in the search bar at top

3. **Click "School Settings"** (there should be one record)

4. **Click "Edit"** and fill in:
   - **School Name:** Your school name (e.g., "Sunshine International School")
   - **School Code:** Short code for reports (e.g., "SUNNYS")
   - **Address:** Full school address
   - **Phone:** School phone number
   - **Email:** Official school email
   - **Logo:** Click "Attach" and upload your school logo (PNG/JPG, 200x200px recommended)
   - **Motto:** Your school's motto (optional)
   - **Curriculum Board:** Select "Cambridge" or "ZIMSEC" (this determines grading scales)
   - **Timezone:** Select your timezone from dropdown (e.g., "Africa/Harare")
   - **Status:** Set to "Active"

5. **Click "Save"**

**You should see:** Green checkmark and "School Settings updated" message

---

## Step 2: Create Academic Calendar

### 2a. Create Academic Year

1. **Search for "Academic Year"**

2. **Click "New"** to create a new year

3. **Fill in:**
   - **Year:** Enter the year (e.g., "2026")
   - **Start Date:** First day of the academic year (e.g., 2026-01-01)
   - **End Date:** Last day of the academic year (e.g., 2026-12-31)

4. **Click "Save"**

### 2b. Create Terms (usually 3 per year)

1. **Search for "Academic Term"**

2. **Click "New"** (create one for each term)

3. **Fill in for Term 1:**
   - **Term Name:** "Term 1"
   - **Academic Year:** Select the year you just created
   - **Start Date:** First day of term (e.g., 2026-01-01)
   - **End Date:** Last day of term (e.g., 2026-03-31)

4. **Click "Save"**

5. **Repeat for Term 2 and Term 3** (change dates accordingly)

---

## Step 3: Create Classes

1. **Search for "Student Group"** (a Student Group = a Class)

2. **Click "New"** to create a class

3. **Fill in:**
   - **Name:** Class name (e.g., "Form 1A", "Form 2B", "Form 3 Science")
   - **Group Based On:** Select "Batch"
   - **Batch:** (Leave blank for now)
   - **Academic Term:** Select the current term

4. **Click "Save"**

5. **Repeat for all classes** (Form 1A, Form 1B, Form 2A, etc.)

**Pro tip:** After creation, you'll assign a Class Teacher and subjects to each group in later steps.

---

## Step 4: Create Subjects

1. **Search for "Course"** (a Course = a Subject in Edupro)

2. **Click "New"** to create a subject

3. **Fill in:**
   - **Name:** Subject name (e.g., "Mathematics", "English", "Biology")
   - **Course Code:** Optional (e.g., "0580" for IGCSE Math)
   - **Description:** Optional

4. **Click "Save"**

5. **Repeat for all subjects** offered at your school

**Common subjects:** Mathematics, English, Physics, Chemistry, Biology, History, Geography, Economics, etc.

---

## Step 5: Create Programs (Streams)

**What this does:** Define curriculum tracks (e.g., Science Stream takes Math, Physics, Chemistry; Commerce Stream takes Math, Accounting, Economics).

1. **Search for "Program"**

2. **Click "New"** to create a program

3. **Fill in:**
   - **Name:** Stream name (e.g., "IGCSE Science", "IGCSE Commerce", "IGCSE Arts")
   - **Curriculum:** Select from dropdown (e.g., "O Level" or "A Level")
   - **Status:** Active

4. **In the "Courses" section, click "Add Row"** and select the subjects for this stream:
   - For Science: Mathematics, Physics, Chemistry, Biology
   - For Commerce: Mathematics, Accounting, Economics, Business Studies
   - Etc.

5. **Click "Save"**

6. **Repeat for each stream** at your school

---

## Step 6: Import Students

**Option A: Manual Entry** (for small schools)

1. **Search for "Student"**

2. **Click "New"** to create a student

3. **Fill in:**
   - **Student Name:** Full name
   - **Email:** Student email (for portal access)
   - **Date of Birth:** DOB
   - **Gender:** Select M/F
   - **Admission Number:** Student ID number
   - **Boarding Type:** "Day Boarder" or "Full Boarder" (affects fees)
   - **Status:** "Active"

4. **Under "Guardians," click "Add Row"** and link their parents

5. **Under "Program Enrollment," click "Add Row":**
   - **Program:** Select the student's stream (e.g., "IGCSE Science")
   - **Academic Year:** Select the year
   - **Courses:** Will auto-populate from the Program

6. **Under "Student Group," link the student to their class**

7. **Click "Save"**

**Option B: Bulk Import** (for large schools)

1. **Prepare a CSV file** with columns:
   ```
   student_name,email,date_of_birth,gender,admission_number,boarding_type,program,student_group
   John Doe,john@school.edu.zw,2010-03-15,M,STU001,Day Boarder,IGCSE Science,Form 1A
   Jane Smith,jane@school.edu.zw,2010-05-22,F,STU002,Full Boarder,IGCSE Science,Form 1A
   ```

2. **In Desk, go to the "Student" list**

3. **Click the menu (three dots) → Import**

4. **Upload your CSV file and map the columns**

5. **Click "Import"**

**After import:** Review in the Student list to verify all records are correct.

---

## Step 7: Set Up Teachers and Class Teachers

1. **Search for "Instructor"** to create teacher records:

2. **Click "New"** for each teacher:
   - **Instructor Name:** Teacher's name
   - **Email:** Teacher email
   - (Leave other fields blank for now)

3. **Click "Save"**

### Assign Class Teachers

1. **Go to each "Student Group"** (class)

2. **Click "Edit"**

3. **Find the "Class Teacher" field** and select the appropriate teacher

4. **Assign subjects to the class:**
   - In the "Courses" section, select all subjects this class takes
   - (Should match the Program's subject list)

5. **Click "Save"**

### Assign Subject Teachers

This is done later via "Class Subject Assignment" when marks entry starts.

---

## Step 8: Set Up Grading Scales

Grading scales are usually **already created** during installation. Verify:

1. **Search for "Grading Scale"**

2. **You should see records like:**
   - "Cambridge Form 1-2"
   - "Cambridge O Level"
   - "Cambridge A Level"
   - "ZIMSEC Form 1-2"
   - "ZIMSEC O Level"
   - "ZIMSEC A Level"

**If any are missing:**

1. **Click "New"** to create one

2. **Name:** (e.g., "Cambridge Form 1-2")

3. **In "Grading Scale Intervals," add rows** with grade boundaries:
   - **Grade:** A* (Threshold: 90)
   - **Grade:** A (Threshold: 80)
   - **Grade:** B (Threshold: 70)
   - **Grade:** C (Threshold: 60)
   - **Grade:** D (Threshold: 50)
   - **Grade:** E (Threshold: 40)
   - **Grade:** F (Threshold: 0)

4. **Click "Save"**

---

## Step 9: Test the System

Before real marks entry, run a test:

### 9a. Create Test Assessment Plans

1. **Search for "Assessment Plan"**

2. **Click "New"**

3. **Fill in:**
   - **Student Group:** Select a class
   - **Course:** Select a subject
   - **Academic Term:** Select the current term
   - **Exam Name:** "Test Assessment" or similar
   - **Schedule Date & Time:** Pick a date/time

4. **In "Criteria," add two rows:**
   - **Criteria:** "Term Mark" | Maximum Score: 100
   - **Criteria:** "Exam Mark" | Maximum Score: 100

5. **Click "Save"**

### 9b. Enter Test Marks

1. **Search for "Assessment Result"**

2. **Click "New"**

3. **Fill in:**
   - **Assessment Plan:** Select the one you just created
   - **Student:** Select a test student
   - **Status:** "Draft"

4. **In "Details," enter scores:**
   - **Term Mark:** 85
   - **Exam Mark:** 90

5. **Click "Save" and then "Submit"**

### 9c. Generate Test Report Card

1. **Search for "Report Card"**

2. **You should see a new report card created** (or click "New" to create manually)

3. **Verify it shows:**
   - Student name
   - Marks
   - Calculated grade
   - Class position

4. **Review and click through the approval workflow** to test transitions

**If this works, your system is ready for real data!**

---

## 📊 Common Setup Questions

### Q: How many terms per year?
**A:** Usually 3 (Term 1, Term 2, Term 3). Some schools use 2 or 4. Configure based on your school calendar.

### Q: What's the difference between a Program and a Student Group?
- **Program:** A curriculum track (e.g., "IGCSE Science" = the subjects taught)
- **Student Group:** A physical class (e.g., "Form 3A" = the students in room 3A)
- A Program contains subjects; a Student Group contains students and follows a Program.

### Q: Can I change class assignments after students are enrolled?
**A:** Yes, but it's better to get them right initially. If you need to move a student:
1. Go to the Student record
2. Edit the Program Enrollment (same class, different program) or the Student Group assignment
3. Any marks already entered stay with the student (historical records)

### Q: How do I add a student mid-year?
1. Create the Student record (as in Step 6)
2. Create a Program Enrollment for the current Academic Year
3. Assign to the appropriate Student Group
4. The student can now receive marks

---

## ✅ You're Ready!

Once you've completed all 9 steps:

1. ✅ Teachers can log in and enter marks
2. ✅ Headmaster can review and approve
3. ✅ Students/Parents can view reports
4. ✅ System generates report cards and emails

**Next:** Read `USER_ONBOARDING_GUIDE.md` to train your staff.

---

## 🆘 Troubleshooting

### "I can't find the School Settings"
**Solution:** It may already exist. Search in the list view, or create a new one if it's truly missing.

### "Students aren't showing in the class"
**Solution:** 
1. Go to each Student record
2. Check that "Student Group" is set to the correct class
3. Ensure the enrollment is for the current Academic Year

### "Marks entry says 'No Assessment Plan found'"
**Solution:** You haven't created Assessment Plans yet. Go to Assessment Plan → Create one for each class/subject/term combination.

**For more help, see `TROUBLESHOOTING_GUIDE.md`**

---

**Document Version:** 1.0  
**For Edupro SMS v1.0 Stable**
