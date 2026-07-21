import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from PIL import Image as PILImage

DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(DIR, "Edupro_SMS_Features_Manual.pdf")

RED = colors.HexColor("#FF0527")
DARK = colors.HexColor("#0f172a")
GRAY = colors.HexColor("#4b5563")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", fontSize=28, leading=34, textColor=DARK, alignment=TA_CENTER, spaceAfter=6, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="CoverSub", fontSize=15, leading=20, textColor=RED, alignment=TA_CENTER, spaceAfter=4, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="CoverMeta", fontSize=11, leading=16, textColor=GRAY, alignment=TA_CENTER))
styles.add(ParagraphStyle(name="H1", fontSize=18, leading=22, textColor=RED, spaceBefore=6, spaceAfter=10, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="H2", fontSize=13, leading=17, textColor=DARK, spaceBefore=12, spaceAfter=6, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="Body", fontSize=10, leading=15, textColor=colors.HexColor("#1f2937"), spaceAfter=6))
styles.add(ParagraphStyle(name="Caption", fontSize=8.5, leading=11, textColor=GRAY, alignment=TA_CENTER, spaceBefore=4, spaceAfter=14, fontName="Helvetica-Oblique"))
styles.add(ParagraphStyle(name="MyBullet", fontSize=10, leading=14, textColor=colors.HexColor("#1f2937")))

MAX_W = 16.5 * cm
MAX_H = 22 * cm


def img_flowable(name, max_h=MAX_H):
    path = os.path.join(DIR, name)
    with PILImage.open(path) as im:
        w, h = im.size
    scale = MAX_W / w
    disp_w, disp_h = MAX_W, h * scale
    if disp_h > max_h:
        scale2 = max_h / disp_h
        disp_w, disp_h = disp_w * scale2, disp_h * scale2
    return Image(path, width=disp_w, height=disp_h)


def shot(name, caption, max_h=MAX_H):
    return KeepTogether([img_flowable(name, max_h), Paragraph(caption, styles["Caption"])])


def bullets(items):
    return ListFlowable(
        [ListItem(Paragraph(i, styles["MyBullet"]), bulletColor=RED) for i in items],
        bulletType="bullet",
        start="circle",
        leftIndent=14,
        spaceBefore=2,
        spaceAfter=10,
    )


story = []

# ---- Cover page ----
story.append(Spacer(1, 5 * cm))
story.append(Paragraph("EDUPRO", ParagraphStyle(name="Logo", fontSize=40, leading=44, alignment=TA_CENTER, textColor=RED, fontName="Helvetica-Bold")))
story.append(Paragraph("School Management System", ParagraphStyle(name="Logo2", fontSize=16, leading=20, alignment=TA_CENTER, textColor=DARK)))
story.append(Spacer(1, 2 * cm))
story.append(Paragraph("Features &amp; Functionality Manual", styles["CoverTitle"]))
story.append(Paragraph("Academic Reporting, Approvals &amp; School Fees", styles["CoverSub"]))
story.append(Spacer(1, 1.5 * cm))
story.append(Paragraph("Prepared for the School Head and System Administrator", styles["CoverMeta"]))
story.append(Paragraph("First Class High &middot; IGCSE / ZIMSEC Curriculum", styles["CoverMeta"]))
story.append(Paragraph("2026", styles["CoverMeta"]))
story.append(PageBreak())

# ---- Introduction ----
story.append(Paragraph("1. Introduction", styles["H1"]))
story.append(Paragraph(
    "Edupro SMS is a purpose-built academic reporting and school management platform. "
    "It replaces spreadsheets and paper report cards with a single system that carries marks "
    "from the classroom, through Class Teacher review and Headmaster approval, to a printable "
    "PDF report card automatically emailed to parents &mdash; plus a school fees module for "
    "termly billing and balance tracking.", styles["Body"]))
story.append(Paragraph("The system has five roles, each with its own dedicated, uncluttered screen:", styles["Body"]))
story.append(bullets([
    "<b>Instructor (Teacher)</b> &mdash; enters Term and Exam marks for their classes/subjects.",
    "<b>Class Teacher</b> &mdash; reviews their class's report cards before the Headmaster sees them.",
    "<b>Headmaster</b> &mdash; approves and publishes report cards, and sees whole-school performance.",
    "<b>Bursar</b> &mdash; manages boarding fees: billing, payments, and statements.",
    "<b>Student / Guardian (parent)</b> &mdash; views grades, profile, and fee statements; downloads report cards.",
]))
story.append(Paragraph(
    "Every role logs into the same web address and is taken straight to their own dashboard &mdash; "
    "there is no separate admin backend for staff to learn, and no role can see another role's private data.",
    styles["Body"]))
story.append(PageBreak())

# ---- Login ----
story.append(Paragraph("2. Signing In", styles["H1"]))
story.append(Paragraph(
    "All users sign in from the same branded login page using their email address and password. "
    "The system automatically detects the user's role and opens the correct dashboard &mdash; "
    "a teacher never sees the Headmaster's screen, and a parent never sees a teacher's marks-entry screen.",
    styles["Body"]))
story.append(shot("01_login.png", "The Edupro SMS login page, branded with the school's own logo and name.", max_h=14 * cm))
story.append(PageBreak())

# ---- Headmaster ----
story.append(Paragraph("3. Headmaster Dashboard", styles["H1"]))
story.append(Paragraph(
    "The Headmaster's dashboard is the whole-school control centre. At a glance it shows the "
    "current academic year and term, total classes, teachers and students, how many report cards "
    "have been published so far this term, how many are still pending approval, and the school's "
    "overall average grade.", styles["Body"]))
story.append(Paragraph("Below the summary, the dashboard has four working sections:", styles["Body"]))
story.append(bullets([
    "<b>Class Performance Overview</b> &mdash; every class, its teacher, average %, grade and completion status, filterable and exportable to CSV.",
    "<b>Report Approval Workflow</b> &mdash; bulk Approve and Publish buttons for classes whose report cards are ready, with a direct link into each class's detailed review.",
    "<b>Subject Performance Analysis</b> &mdash; the school's strongest subjects and the subjects needing the most attention, calculated from real submitted marks.",
    "<b>Recent Activity</b> &mdash; a live feed of report cards changing state and any assessments still missing marks past their due date.",
]))
story.append(shot("02_headmaster_dashboard.png", "Headmaster Dashboard &mdash; whole-school summary, class performance, approvals and analytics.", max_h=23 * cm))
story.append(PageBreak())

story.append(Paragraph("Class Review &amp; Bulk Approval", styles["H2"]))
story.append(Paragraph(
    "Clicking “Review” on any class opens a full drill-down: the class average, grade "
    "distribution chart, a ranked list of every student with their subject count and status, the "
    "Class Teacher's comments, and the Approve / Reject / Publish actions for that class's report cards.",
    styles["Body"]))
story.append(shot("03_headmaster_classreview.png", "Class Review drill-down &mdash; grade distribution, ranked student list, and approval actions for one class.", max_h=23 * cm))
story.append(PageBreak())

# ---- Teacher ----
story.append(Paragraph("4. Teacher Dashboard &amp; Marks Entry", styles["H1"]))
story.append(Paragraph(
    "A teacher's dashboard shows only the classes and subjects assigned to them: how many marks "
    "are entered so far, how many are still pending, and a quick subject-then-class picker that "
    "opens straight into marks entry for that class. A Class Teacher additionally sees a "
    "“Report Cards Awaiting Your Review” panel here &mdash; their own step in the approval "
    "chain, done with one click per class.", styles["Body"]))
story.append(shot("04_teacher_dashboard.png", "Teacher Dashboard &mdash; assigned subjects, class cards with entry progress, and grade boundaries reference.", max_h=20 * cm))
story.append(PageBreak())

story.append(Paragraph("Entering Marks", styles["H2"]))
story.append(Paragraph(
    "Marks entry captures a <b>Term Mark</b> and an <b>Exam Mark</b> per subject, each out of 100, "
    "with the letter grade calculated live as the teacher types. The page shows real-time class "
    "performance (a grade distribution chart) and the grade boundary table for the class's curriculum "
    "&mdash; Cambridge or ZIMSEC, and the correct band for that class's Form level. Marks can also be "
    "exported to CSV, edited offline, and re-imported, and the whole sheet can be printed.",
    styles["Body"]))
story.append(shot("05_marks_entry.png", "Enter Marks &mdash; Term Mark + Exam Mark per subject, live grades, class performance and grade boundaries.", max_h=23 * cm))
story.append(PageBreak())

# ---- Bursar ----
story.append(Paragraph("5. Bursar &mdash; School Fees", styles["H1"]))
story.append(Paragraph(
    "The Bursar signs in to their own screen only &mdash; there is no access to the school's internal "
    "administration area, only this fees page. Fees are termly: a Day Boarder is billed $750 per term "
    "and a Full Boarder $1,450 per term, decided by each student's Boarding Type.", styles["Body"]))
story.append(Paragraph("From one screen, the Bursar can:", styles["Body"]))
story.append(bullets([
    "See every student's class, boarding type, and outstanding balance in one table, with a running school-wide total billed / paid / balance.",
    "Change a student's Boarding Type at any time &mdash; this only affects future billing, it never rewrites an already-billed term.",
    "Record a payment against any billed term (supporting partial payments across more than one instalment, with the balance updating immediately).",
    "Print or download a PDF fee statement for any student, showing every term of the current academic year.",
]))
story.append(shot("06_bursar.png", "Bursar &mdash; school-wide fee summary, per-student boarding type, balances, payment recording and statement printing.", max_h=23 * cm))
story.append(PageBreak())

# ---- Parent/Student portal ----
story.append(Paragraph("6. Parent &amp; Student Portal (My Reports)", styles["H1"]))
story.append(Paragraph(
    "Students and their parents/guardians share the same portal, with four tabs. A guardian with "
    "more than one child at the school sees a card for each child and can jump between them.",
    styles["Body"]))

story.append(Paragraph("Overview", styles["H2"]))
story.append(Paragraph(
    "A compact summary per child: academic year and term, average, overall grade, class position, "
    "star rating, and the full subject-by-subject breakdown with the teacher's comment for each "
    "subject. From here a parent can view, print, or download the report card as a PDF, or resend "
    "it by email.", styles["Body"]))
story.append(shot("07_myreports_overview.png", "My Reports &mdash; Overview tab, with per-subject results and report actions.", max_h=21 * cm))
story.append(PageBreak())

story.append(Paragraph("Grades, Profile &amp; Fees", styles["H2"]))
story.append(Paragraph(
    "The <b>Grades</b> tab lists every report card published for a child, term by term. The "
    "<b>Profile</b> tab shows the child's class, class teacher, and full subject list with the "
    "teacher assigned to each. The <b>Fees</b> tab is new: it shows the child's boarding type, "
    "total balance due, and a full statement across all three terms of the year &mdash; including "
    "the upcoming term, clearly marked “Not Yet Billed” until the Bursar issues it.",
    styles["Body"]))

t1 = img_flowable("08_myreports_grades.png", max_h=8 * cm)
t2 = img_flowable("09_myreports_profile.png", max_h=8 * cm)
tbl = Table([[t1, t2]], colWidths=[MAX_W / 2 - 0.2 * cm, MAX_W / 2 - 0.2 * cm])
tbl.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
story.append(tbl)
story.append(Paragraph("Grades tab (left) and Profile tab (right).", styles["Caption"]))

story.append(shot("10_myreports_fees.png", "Fees tab &mdash; balance summary and full term-by-term statement, with a PDF download.", max_h=10 * cm))
story.append(PageBreak())

# ---- Report Card ----
story.append(Paragraph("7. The Report Card", styles["H1"]))
story.append(Paragraph(
    "A report card only reaches this stage after passing through the full approval chain: the "
    "subject teacher enters marks, the Class Teacher reviews the class, and the Headmaster approves "
    "and publishes. Only once <b>Published</b> does it become visible to the student and their "
    "guardians, and only then is it automatically emailed home.", styles["Body"]))
story.append(Paragraph(
    "The printed PDF carries the school's logo, the Term Mark and Exam Mark (with grades) for every "
    "subject, an auto-loaded comment per subject, the class average/grade/position, signature lines "
    "for the Class Teacher and Headmaster, and a scannable QR code that lets anyone verify the report "
    "is genuine.", styles["Body"]))
story.append(shot("11_report_card_pdf.png", "A generated Term Report Card, ready to print, download, or email.", max_h=17 * cm))
story.append(PageBreak())

# ---- Fee Statement ----
story.append(Paragraph("8. The Fee Statement", styles["H1"]))
story.append(Paragraph(
    "The same PDF format is available to the Bursar (for any student) and to parents/students (for "
    "their own child only). It shows the student's boarding type, total balance due, and every term "
    "of the academic year with amount billed, amount paid, remaining balance, and status.",
    styles["Body"]))
story.append(shot("12_fee_statement_pdf.png", "A student's Fee Statement, showing two billed terms and one upcoming, not-yet-billed term.", max_h=12 * cm))
story.append(PageBreak())

# ---- Roles summary table ----
story.append(Paragraph("9. Roles &amp; What Each One Can Do", styles["H1"]))

cell = ParagraphStyle(name="Cell", fontSize=9, leading=12, textColor=colors.HexColor("#1f2937"))
head = ParagraphStyle(name="CellHead", fontSize=9, leading=12, textColor=colors.white, fontName="Helvetica-Bold")


def P(text, style=cell):
    return Paragraph(text, style)


raw_rows = [
    ["Role", "Signs in to", "Can do"],
    ["Instructor (Teacher)", "Teacher Dashboard + Enter Marks", "Enter Term/Exam marks for their own classes and subjects only."],
    ["Class Teacher", "Teacher Dashboard", "Everything a teacher can, plus reviewing their own class's report cards before the Headmaster sees them."],
    ["Headmaster", "Headmaster Dashboard + Class Review", "Whole-school visibility; approves, rejects and publishes report cards; sees performance analytics."],
    ["Bursar", "Bursar page", "Bills terms, records payments, changes boarding type, prints statements for any student. No access to marks or report cards."],
    ["Student / Guardian", "My Reports", "Views/prints/downloads their own (or their children's) report cards and fee statements only."],
]
data = [[P(c, head) if i == 0 else P(c) for c in row] for i, row in enumerate(raw_rows)]
tbl2 = Table(data, colWidths=[3.0 * cm, 4.0 * cm, 9.5 * cm], repeatRows=1)
tbl2.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), DARK),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
]))
story.append(tbl2)
story.append(Spacer(1, 0.6 * cm))
story.append(Paragraph(
    "No role can see or act on data outside its own scope &mdash; this is enforced by the system "
    "itself, not just hidden by the menus. A parent cannot open another family's report card or fee "
    "statement even by guessing a web address.", styles["Body"]))

doc = SimpleDocTemplate(
    OUT, pagesize=A4,
    topMargin=1.8 * cm, bottomMargin=1.8 * cm, leftMargin=2.2 * cm, rightMargin=2.2 * cm,
    title="Edupro SMS Features & Functionality Manual", author="Edupro",
)
doc.build(story)
print("built:", OUT)
