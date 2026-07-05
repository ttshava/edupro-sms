# Edupro SMS v1.0 — Quick Start for Teachers, Students & Parents

**If your school has installed Edupro SMS, use this guide to get started.**

---

## 🎓 For Students

### Logging In

1. **Open your browser** and go to: `http://SCHOOL_SERVER_ADDRESS/my-reports`
   - Your school IT department will provide the SERVER_ADDRESS
   - Example: `http://192.168.1.100:8080/my-reports`

2. **Enter your login credentials:**
   - Email: Your school email
   - Password: A temporary password given by your teacher/admin (change it on first login)

3. **Click "Login"**

### Viewing Your Grades

1. **Click the "Grades" tab** (left sidebar)

2. **Select a term** from the dropdown

3. **You will see:**
   - All your subjects
   - Marks for each subject (Term Mark + Exam Mark)
   - Your grade (A, B, C, etc.)
   - Class position (your ranking in the class)
   - Subject comments from teachers

### Downloading Your Report Card

1. **Next to your report, click "View"** to see the full report card

2. **Click "Print" or "Download"** to save as PDF

3. **You can print it at home or show it to your parents**

### Changing Your Password

1. **Click your name** at top right

2. **Click "Set User Password"**

3. **Enter your current password and new password**

4. **Click "Set Password"**

---

## 👨‍👩‍👧 For Parents/Guardians

### Logging In

1. **Open your browser** and go to: `http://SCHOOL_SERVER_ADDRESS/my-reports`

2. **Enter your login credentials** (provided by school admin)

3. **Click "Login"**

### Viewing Your Children's Grades

1. **You will see all your linked children** in cards at the top

2. **Click on a child's card** to see their grades

3. **Tabs available:**
   - **Overview:** Child's summary and subjects
   - **Grades:** Detailed marks per term
   - **Profile:** Class, teacher info

### Viewing Fee Status

1. **Click the "Fees" tab** (left sidebar)

2. **You will see:**
   - Amount billed this term
   - Amount paid
   - Outstanding balance
   - Payment status (Paid / Partially Paid / Billed)

3. **Click "View Statement"** to see detailed payment history

### Downloading Report Cards

1. **In the Grades tab, next to a report, click "View"**

2. **Click "Print"** to download as PDF

3. **Print at home or email to family**

### Receiving Email Notifications

When your child's report is published:
- You will automatically receive an **email with the report card PDF attached**
- No action needed — check your email inbox and spam folder

---

## 👨‍🏫 For Teachers

### Logging In

1. **Open your browser** and go to: `http://SCHOOL_SERVER_ADDRESS/dashboard`

2. **Enter your login credentials** (provided by school admin)

3. **Click "Login"**

### Viewing Your Dashboard

1. **You will see your dashboard** showing:
   - Academic Year, Current Term
   - Assigned Subjects and Classes
   - Marks entry progress (X marks entered out of Y students)

2. **View each subject's status:**
   - **Cards show:** Subject name, class name, progress bar
   - **Color indicators:** 
     - 🟢 Green: Complete (all marks entered)
     - 🟡 Yellow: Pending (some marks missing)

### Entering Marks

1. **Click a class card** to go to marks entry page

2. **Enter marks for each student:**
   - **Term Mark:** 0-100 (auto-grades as you type)
   - **Exam Mark:** 0-100 (auto-grades as you type)
   - **Comments:** Optional notes about the student's performance

3. **Rows show:**
   - Student name and ID
   - Their current marks (if already entered)
   - Status: "Entered" or "Missing"

4. **Click "Save"** when done (auto-saves every 30 seconds too)

5. **After entering all students, click "Submit"** to finalize

**Note:** Once submitted, you can only edit by requesting a "cancel & amend" from your Headmaster.

### Viewing Grade Distribution

1. **Scroll down** on the marks entry page

2. **You will see a chart showing:**
   - How many A's, B's, C's, etc. in your class
   - Visual bar chart for quick overview

### CSV Export/Import (Bulk Marks)

1. **At the top of marks entry, click "Download"** to export current marks to Excel

2. **Edit the Excel file** with new marks

3. **Click "Upload"** and select the same file

4. **Edupro will update all marks at once**

### Reviewing Before Submission

**Before you click "Submit," check:**
- [ ] All students have marks for Term Mark
- [ ] All students have marks for Exam Mark
- [ ] No blank cells (except Comments, which are optional)
- [ ] No marks above 100
- [ ] Grades calculated correctly (visible on screen)

**Once submitted, you cannot edit without Headmaster approval.**

---

## 🎯 For Headmaster/Principal

### Logging In

1. **Open your browser** and go to: `http://SCHOOL_SERVER_ADDRESS/dashboard`

2. **Enter your login credentials**

3. **Click "Login"**

### Viewing Your Dashboard

1. **You will see a school-wide summary:**
   - Academic Year, Current Term, Number of Classes
   - Summary stats: Total Students, Teachers, Reports Published, Pending Approvals

2. **Click on any section** to see details:
   - **Classes:** Performance overview per class
   - **Pending Approvals:** Report cards waiting for your approval

### Approving Report Cards

1. **Click "Pending Approvals"** section

2. **You will see list of report cards** waiting for approval

3. **Click a report card** to view it:
   - Student name and class
   - All subjects and marks
   - Class position
   - Comments from Class Teacher

4. **Actions:**
   - **Approve:** Click "Approve" → Enter your comment (optional) → Save
   - **Reject:** Click "Reject" → Explain reason → Save (goes back to Class Teacher)
   - **Publish:** After approval, click "Publish" → Report is locked and emailed to parent

### Bulk Approve Classes

1. **Click "Classes"** section

2. **Select a class** to see all pending reports for that class

3. **Click "Approve All for This Class"** button (if all are ready)

4. **Review the list**, then confirm

5. **All reports are approved at once**

### Viewing Class Performance

1. **Click "Classes"** section

2. **You will see a table showing:**
   - Class name
   - Average percentage
   - Grade distribution (how many A's, B's, C's, etc.)
   - Rank (strongest/weakest class)

3. **Click a class** to see detailed drill-down:
   - Individual student rankings
   - Subject-by-subject performance
   - Strong vs. weak subjects

### Viewing Fees Overview — Dashboard

**URL:** `http://SCHOOL_SERVER_ADDRESS/headmaster-dashboard/fees/`

1. **Go to the Fee Dashboard** using the URL above

2. **Select an Academic Term** from the dropdown (required)

3. **Optionally filter by Program** (leave blank for all programs)

4. **Click "Load Dashboard"**

5. **You will see:**

#### Summary Cards (Top Row)
Four cards showing financial snapshot:
- **Total Billed:** Sum of all fees for the term
- **Total Collected:** Amount received in payments
- **Outstanding:** Amount still owed (Billed - Collected)
- **Collection %:** (Collected / Billed) × 100

#### Charts

**By Program (Pie Chart):**
- Shows which programs generate most revenue
- Each slice = one program's collected amount
- Hover to see exact dollar amounts

**By Status (Doughnut Chart):**
- How many students have Paid/Partially Paid/Unpaid fees
- Green = Paid, Yellow = Partially Paid, Red = Unpaid
- Shows student count in tooltip

**Collection Trend (Line Chart):**
- Tracks collection % week-by-week through the term
- Line should trend upward (more collected over time)
- Shows if you're on track for full collection

#### Unpaid Students Table
List of students with outstanding balances, sorted by urgency:
- **Name:** Student name
- **Admission #:** Student ID
- **Amount Due:** Outstanding balance
- **Days Overdue:** How long past the due date
  - 🔴 Red (30+ days): Critical — follow up urgently
  - 🟡 Yellow (7-30 days): At risk — send reminder
  - 🟢 Green (<7 days): Recent or upcoming due

#### Quick Actions

**To see just one program:**
1. Filter by Program (e.g., "IGCSE Science")
2. Click "Load Dashboard"
3. Data updates to show only that program

**To reset and see all programs:**
1. Click "Reset" button
2. Filters clear
3. Select term and load

#### Example Dashboard Reading

```
Term 1 2026, All Programs:

Summary:
  • Total Billed: $500,000
  • Total Collected: $320,000
  • Outstanding: $180,000
  • Collection Rate: 64%

By Program:
  • IGCSE Science: $200,000 collected (80% of that program's total)
  • IGCSE Commerce: $120,000 collected (60% of that program's total)
  • O-Level Math: $0 collected (0% — follow up!)

By Status:
  • 140 students Paid (green slice)
  • 50 students Partially Paid (yellow slice)
  • 10 students Unpaid (red slice)

Collection Trend:
  Week 1: 10% collected
  Week 2: 30% collected
  Week 3: 50% collected
  Week 4: 64% collected ← Trending well

Unpaid Students:
  1. John Smith (ADM-001): $2,000 due, 45 days overdue 🔴
  2. Jane Doe (ADM-002): $1,500 due, 20 days overdue 🟡
  ...
```

**Interpretation:**
- Collection rate is healthy (64%)
- O-Level Math program lagging (0% collected) — investigate!
- Trend is positive (moving toward full collection)
- 10 students at risk — send reminders

### Viewing Individual Student Fees

1. **Go to Student list:** `http://SCHOOL_SERVER_ADDRESS/bursar-students`

2. **Find the student** (use search/filter)

3. **Click Edit** button

4. **Scroll to Fees section** at bottom

5. **See:**
   - Termly fees charged
   - Payment status
   - Balance outstanding

---

## 💼 For Bursar / Finance Officer

The Bursar manages student records, enrollments, and billing information.

### Accessing Student Management

1. **Go to:** `http://SCHOOL_SERVER_ADDRESS/bursar-students`
   - Your school IT will provide the SERVER_ADDRESS

2. **You will see a list of all students** with their:
   - Student ID
   - Name
   - Email
   - Admission Number
   - Boarding Type (Day Boarder / Full Boarder)
   - Status (Active / Inactive)

### Searching & Filtering Students

**Search by Name:**
- In the search box, type student's name (e.g., "John")
- Table filters instantly to matching students

**Search by Email or Admission Number:**
- Type email address or admission number
- Results update in real-time

**Filter by Status:**
- Click **Filters** button
- Select "Status" = Active or Inactive
- Click filter button to apply

**Filter by Boarding Type:**
- Use the Filters menu
- Select "Boarding Type" = Day Boarder or Full Boarder

**Pagination:**
- Results show 20 per page
- Use Next/Previous buttons to navigate

### Adding a New Student (Manually)

1. **Click "Add Student"** button

2. **Fill the form:**
   - **Student Name** (required): Full name
   - **Email** (required): Unique school email
   - **Admission Number** (required): Unique student ID
   - **Date of Birth** (optional): YYYY-MM-DD format
   - **Gender**: Male or Female
   - **Boarding Type**: Day Boarder or Full Boarder
   - **Program** (optional): Can be added later
   - **Class** (optional): Can be added later

3. **Click "Create Student"**

4. **Student is created** and you're redirected to the student list

### Adding Multiple Students at Once (CSV Import)

For 50+ students, use bulk import:

1. **Click "Bulk Import"** button (on student list page)

2. **Download the Student template** (Excel file)

3. **Fill template with your student data:**
   - Student Name, Email, Admission Number, Program, Class
   - One row per student
   - Save the file

4. **Upload the file** to the import page

5. **Validate the data** (checks for errors)

6. **Click "Import"** to add all students at once

*For detailed CSV import instructions, see INSTALLATION_GUIDE.md section "Bulk Import Students & Staff"*

### Editing Student Information

1. **Find the student** in the list (use search/filter)

2. **Click the pencil icon** (Edit button) in the Actions column

3. **Update the information:**
   - Name, Email, Date of Birth, Gender, Boarding Type, Status
   - Fields pre-filled with current data

4. **Click "Save Changes"**

5. **Student info updated** and you're returned to the list

**Note:** Only edit editable fields (Name, Email, etc.). Security-sensitive fields cannot be changed.

### Enrolling a Student in a Program

1. **Find the student** in the list

2. **Click the graduation cap icon** (Enroll button)

3. **Select a Program** from the dropdown (e.g., "IGCSE Science")

4. **Optionally select a Class** (Form 1A, etc.)

5. **Click "Enroll"**

6. **Success message** shows the enrollment is complete

**After enrollment:**
- Student can access the student portal
- Student sees marks, grades, reports
- Billing automatically configured
- Teacher can enter marks for this student

### Linking a Student to a Guardian (Parent)

1. **Find the student** in the list

2. **Click the shield icon** (Link Guardian button)

3. **Two options:**

   **Option A - Link Existing Guardian:**
   - Stay on "Link Existing" tab
   - Select guardian from dropdown
   - Click "Link Guardian"

   **Option B - Create New Guardian:**
   - Click "Create New" tab
   - Enter Guardian Name
   - Enter Guardian Email
   - Click "Link Guardian"
   - New guardian account created + linked

**After linking:**
- Guardian receives login credentials (email)
- Guardian can view student's grades and fees in parent portal
- Notifications about reports sent to guardian

### Deactivating a Student

When a student leaves the school:

1. **Find the student** in the list

2. **Click the ban icon** (Deactivate button)

3. **A confirmation modal appears**

4. **Enter reason** (optional): "Graduated", "Transferred", "Left school", etc.

5. **Click "Deactivate"**

6. **Student status changes to "Inactive":**
   - Student cannot log in anymore
   - Records preserved (not deleted)
   - Can be reactivated if needed

### Viewing Student Fees & Billing

1. **From the student list, click Edit** on any student

2. **Scroll to Fees section** (bottom of form)

3. **See:**
   - Termly fees charged
   - Payment status
   - Balance outstanding

*For detailed fee management, contact your finance system admin.*

### Fee Entry Portal (Manage Fees & Record Payments)

**URL:** `http://SCHOOL_SERVER_ADDRESS/bursar-fees/`  
**Purpose:** View, edit, and record payments for all student fees in one place

#### Viewing Student Fees

1. **Go to:** `/bursar-fees/`

2. **Default view shows:**
   - First 20 fees (paginated)
   - All columns: Student Name, Admission #, Email, Program, Term, Amount, Status, Due Date, Balance
   - Status badges with color coding:
     - 🔴 Red: Unpaid
     - 🟡 Yellow: Partially Paid
     - 🟢 Green: Paid

#### Searching for a Student Fee

1. **In the search box**, type:
   - Student's full name (e.g., "John Doe")
   - Email address (e.g., "john@school.com")
   - Admission number (e.g., "ADM-001")

2. **Table filters instantly** — no need to click search button

3. **Search is case-insensitive** — "john" = "John"

#### Filtering Fees

**By Program:**
- Click "All Programs" dropdown
- Select a program (e.g., "IGCSE Science")
- Table updates instantly

**By Status:**
- Click "All Status" dropdown
- Choose: Unpaid, Partially Paid, or Paid
- Table updates to show only selected status

**By Academic Term:**
- Click "All Terms" dropdown
- Select term (e.g., "Term 1 2026")
- Table shows only that term's fees

**Reset All Filters:**
- Click the "Reset Filters" button
- Clears all search and filter selections

#### Combining Filters

You can use multiple filters together:
- Example: "IGCSE Science" + "Unpaid" + Search "John"
- Shows only John's unpaid IGCSE Science fees
- Filters work together (AND logic)

#### Pagination

1. **See which page** — Bottom shows "Page 1 of 5" (example)

2. **Navigate pages:**
   - Click "Previous" to go back
   - Click "Next" to go forward

3. **Each page shows 20 fees**

#### Editing a Student Fee

When you need to change the fee amount or status:

1. **Find the fee** in the table

2. **Click the pencil icon** (Edit button)

3. **In the modal:**
   - **New Amount:** Enter if you want to change the fee amount
   - **Status:** Select new status (Unpaid, Partially Paid, Paid) — optional
   - Leave blank if you don't want to change something

4. **Click "Save Changes"**

5. **Fee updates** in the table and database instantly

**Example:** Change a fee from $5,000 to $5,500
```
Find fee → Click Edit → Enter 5500 in "New Amount" → Save
```

#### Recording a Payment

When a student/parent pays their fees:

1. **Find the student's fee** in the table

2. **Click the credit card icon** (Record Payment button)

3. **In the payment modal:**
   - **Payment Date:** Pre-filled with today (can change)
   - **Outstanding Balance:** Shows amount still owed (read-only)
   - **Amount Paid:** Enter the amount received
   - **Payment Method:** Select (Cash, Check, Bank Transfer, Card, Mobile Money)
   - **Notes:** Optional — e.g., check number, reference info

4. **Validation:**
   - Amount Paid cannot exceed Outstanding Balance
   - System prevents overpayment

5. **Click "Record Payment"**

6. **Results:**
   - Success message shows new balance
   - Fee status auto-updates:
     - If balance = $0 → Status = "Paid" (green badge)
     - If balance > $0 → Status = "Partially Paid" (yellow badge)
   - Balance updates instantly

**Example Workflow:**
```
Fee: $5,000 Unpaid
Student pays $2,000 cash
Click Record Payment → Amount: 2000 → Method: Cash → Save
Result: Balance = $3,000, Status = Partially Paid

Later: Student pays remaining $3,000
Click Record Payment → Amount: 3000 → Method: Check → Note: "Cheque #456" → Save
Result: Balance = $0, Status = Paid
```

#### Viewing Fee Statement

To see detailed fee information (useful for printing/sending to parents):

1. **Find the fee** in the table

2. **Click the PDF icon** (View Statement button)

3. **Modal shows:**
   - Student info (name, admission #, email)
   - Fee details (program, term, amount, balance)
   - Current status

4. **Click "Print"** to:
   - Print to paper
   - Save as PDF
   - Send to parent

#### Tips for Bursar Fee Management

| Task | How-To |
|------|--------|
| **Bulk fees created but payments needed** | Use /bursar-fees/ to record all payments in sequence |
| **Find all unpaid students** | Filter by Status="Unpaid", sort by Due Date |
| **Collect from specific class** | Filter by Program, sort by Due Date |
| **Late fees?** | Sort by Due Date, check balance > 0 with date passed |
| **End-of-term reconciliation** | Count Paid vs Unpaid, verify all balances = $0 |
| **Parent inquiry about balance** | Search student name, click View Statement, print/email |

---

### Batch Billing (Create Fees for All Students at Once)

**Time saved:** 3+ hours per term (vs. creating 200 fees manually one by one)

#### Prerequisites
First, ensure:
- All students are enrolled in a Program (e.g., "IGCSE Science")
- Fee rates are configured (e.g., "IGCSE Science" costs $5,000 for Day Boarders)

#### Steps

1. **Go to:** `http://SCHOOL_SERVER_ADDRESS/bursar-billing`

2. **Select criteria:**
   - **Academic Term:** Choose which term to bill (e.g., "Term 1 2026")
   - **Program:** Select a program (e.g., "IGCSE Science") or "All Programs"
   - **Boarding Type:** Filter to bill only Day Boarders, Full Boarders, or All

3. **Click "Preview Billing (No Changes)"**
   - Modal shows how many students will be billed
   - Shows total amount to be billed
   - Lists first 5 students as preview
   - **No changes made yet** — this is safe to preview multiple times

4. **Review the preview:**
   - Count of students: Should match your enrollment
   - Total amount: Should match (# students × configured rate)
   - Example: "200 students will be billed $1,000,000 total"

5. **Click "Confirm & Create Fees"** in the preview modal

6. **Wait for billing to complete**
   - Status shows "Creating fees..."
   - Page displays results when complete

7. **Review results:**
   - **Created:** Number of new fees generated
   - **Skipped:** Students already billed or missing rates
   - **Failed:** Errors (rare)
   - **Total Billed:** Total amount charged in this batch

#### Example Workflow

```
Scenario: Bill IGCSE Science students for Term 1 2026
  
Step 1: Go to /bursar-billing
Step 2: Select "Term 1 2026" + "IGCSE Science" + "All Boarding"
Step 3: Click Preview
        → Shows "80 students will be billed $435,000"
Step 4: Review preview is correct
Step 5: Click "Confirm & Create Fees"
Step 6: Wait 5-10 seconds
Step 7: Results: "Billing complete: 80 created, 0 skipped, 0 failed. Total: $435,000"
Step 8: Done! All 80 fees created instantly.
```

#### Safe to Re-Run?

**Yes!** If you accidentally run billing twice:
- First run: Creates 200 fees
- Second run: "200 created=0, skipped=200" (no duplicates)
- Result: Still only 200 fees (safe to retry)

#### Troubleshooting

| Issue | Solution |
|-------|----------|
| Preview shows 0 students | Check that students are enrolled in selected program |
| Preview shows fewer than expected | Some students may not have matching billing rates configured |
| "No active billing rates found" error | Contact Headmaster to configure billing rates first |
| Billing seems slow (takes >30 sec) | Normal for 500+ students; wait for completion |

### Common Bursar Tasks

| Task | Steps |
|------|-------|
| **Quickly add 100 students** | Click "Bulk Import" → Download template → Fill → Upload → Validate → Import |
| **Search for a student** | Use search box, type name/email |
| **Enroll student in class** | Find student → Click Enroll button → Select program & class |
| **Remove a student** | Find student → Click Deactivate button → Confirm |
| **Verify student info** | Find student → Click Edit → Review pre-filled data |
| **Link student to parent** | Find student → Click Link Guardian → Select or create |

### Tips for Bursar

- **Batch operations are faster:** Import 100 students at once instead of adding one by one
- **Search is real-time:** Type as you search, no need to click submit
- **Soft delete only:** Deactivating doesn't delete data, just marks as Inactive
- **Validation before import:** Always validate CSV data first, errors show clearly
- **Email must be unique:** Each student/teacher/guardian needs a different email
- **Audit trail:** All your actions (create, edit, deactivate) are logged

---

## 📱 Tips for All Users

### Password Security
- Change your password immediately after first login
- Use a strong password (mix of letters, numbers, symbols)
- Never share your password with others

### Browser Requirements
- Use Chrome, Firefox, Edge, or Safari (recent versions)
- JavaScript must be enabled
- Cookies must be allowed

### Internet Connection
- You only need internet for initial login
- After login, most functions work on a school network (no internet needed)
- Marks entry, viewing grades — all work on local network

### Getting Help
- Ask your school's IT administrator
- Check with your teacher/headmaster if you're unsure
- Contact school IT: (provided by your school)

---

## ⚠️ Common Issues

### Can't log in?
- Check email and password are correct
- Ask your school IT to verify your account exists
- Try clearing browser cookies and cache

### Can't see my grades?
- Check that marks have been submitted by your teacher
- Check with your Headmaster — report may not be published yet
- Refresh the page (Ctrl+F5 or Cmd+Shift+R)

### Report card PDF won't download?
- Try a different browser
- Check that pop-ups are not blocked
- Download button is next to the report — click "Print"

### Password reset says "Email not found"?
- Ask your IT administrator to reset your password
- They can set a temporary password for you

---

## ✅ Success Checklist

- [ ] I can log in with my credentials
- [ ] I can see my dashboard (teacher) or grades (student)
- [ ] I can download/view a report card
- [ ] I understand how marks are entered (for teachers)
- [ ] I know how to change my password

**If all checks pass, you're ready to use Edupro SMS!**

---

**Document Version:** 1.0  
**For Edupro SMS v1.0 Stable**
