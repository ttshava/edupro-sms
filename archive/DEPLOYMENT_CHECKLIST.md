# Edupro SMS v1.0 — Deployment Checklist for IT Administrators

**Use this checklist for production deployment on a school server.**

---

## 📋 Pre-Deployment (1-2 weeks before go-live)

### Hardware & Infrastructure
- [ ] **Server acquired** — meets minimum specs (2 CPU cores, 4GB RAM, 50GB disk)
- [ ] **Static IP assigned** — server has consistent internal IP address
- [ ] **Network connectivity** — server connected to school network
- [ ] **Power backup** — UPS or backup power configured
- [ ] **Firewall rules** — Port 8080 allowed from school network
- [ ] **DNS/hostname** — Server accessible as `edupro.school.local` or similar

### Software Setup
- [ ] **Operating system installed** — Ubuntu 20.04 LTS (recommended) or Windows Server 2019+
- [ ] **Docker installed** — version 20.10+ (run `docker --version` to verify)
- [ ] **Docker Compose installed** — version 1.29+ (run `docker-compose --version`)
- [ ] **Git installed** — for cloning repository
- [ ] **Repository cloned** — Edupro SMS code downloaded to `/opt/edupro-sms` or `C:\edupro-sms`

### Security Preparation
- [ ] **SSL certificate acquired** (optional but recommended for HTTPS access)
- [ ] **Email SMTP configured** — school email provider details collected (server, port, credentials)
- [ ] **Admin password chosen** — strong password (12+ chars, mixed case, numbers, symbols)
- [ ] **Backup location** — identified (external hard drive, cloud storage, NAS)

### Data Preparation
- [ ] **Academic calendar created** — Years, Terms, Dates finalized
- [ ] **Class list created** — All Form names (e.g., Form 1A, Form 2B, etc.)
- [ ] **Student list prepared** — CSV file with: name, email, DOB, gender, ID, boarding type, class
- [ ] **Teacher list prepared** — CSV file with: name, email, subject assigned, class teacher flag
- [ ] **Subject list created** — All subjects offered at school
- [ ] **Program/Stream list created** — Which subjects belong to which curriculum track

---

## 🚀 Installation & Configuration (Day 1)

### Docker Setup
- [ ] **Environment file created** — `.env` file with passwords and settings
- [ ] **Database password set** — Strong MARIADB_ROOT_PASSWORD chosen
- [ ] **Admin password set** — Strong ADMIN_PASSWORD chosen
- [ ] **Timezone configured** — TZ variable set to school's timezone

### Container Startup
- [ ] **Containers started** — `docker compose up -d` executed
- [ ] **All services running** — `docker compose ps` shows 6 containers with status "Up"
- [ ] **Wait time respected** — Waited 3-5 minutes for services to fully initialize
- [ ] **No restart loops** — No containers showing "Restarting" or "Exiting"

### System Access
- [ ] **Admin login works** — Can access Desk with admin credentials
- [ ] **Desk interface loads** — All menu items visible and clickable
- [ ] **No error pages** — No "500 Internal Server Error" or "Bad Gateway"

---

## ⚙️ Initial Configuration (Day 1-2)

### School Setup
- [ ] **School Settings configured** — Name, code, address, phone, email, logo, motto, timezone
- [ ] **Logo uploaded** — School logo visible on login page and report cards
- [ ] **Curriculum board selected** — Cambridge or ZIMSEC set

### Academic Structure
- [ ] **Academic Year created** — Year + start/end dates
- [ ] **Academic Terms created** — 3 terms with correct start/end dates
- [ ] **Student Groups created** — All classes (Form 1A, Form 2B, etc.) with class teachers assigned
- [ ] **Courses created** — All subjects with correct course codes
- [ ] **Programs created** — Each curriculum stream with correct subject lists

### User Setup
- [ ] **Headmaster account created** — Can log in and access dashboard
- [ ] **Bursar account created** — Can access fee management
- [ ] **Teacher accounts created** — One per teaching staff member
- [ ] **Class Teacher accounts created** — Separate role assignments where applicable
- [ ] **Test Student account created** — For system testing

### Grading Scales
- [ ] **Grading scales verified** — All 6 scales present (Cambridge & ZIMSEC × Form 1-2/O-Level/A-Level)
- [ ] **Grade boundaries correct** — A* at 90, A at 80, B at 70, etc.

---

## 📊 Data Import (Day 2-3)

### Student Data
- [ ] **Student CSV prepared** — All required columns included
- [ ] **Data validated** — No duplicates, all emails valid, all classes referenced exist
- [ ] **Students imported** — Bulk import completed without errors
- [ ] **Student count verified** — System shows correct number of students
- [ ] **Program enrollments set** — Each student linked to correct curriculum stream
- [ ] **Student groups assigned** — Each student added to correct class
- [ ] **Boarding types set** — Day Boarder vs Full Boarder classifications correct

### Teacher Data
- [ ] **Teacher CSV prepared** — All instructors with their details
- [ ] **Instructors imported** — Teacher records created
- [ ] **Subject assignments done** — Each teacher linked to their subjects
- [ ] **Class assignments done** — Teachers assigned to correct classes
- [ ] **Class teacher designations** — Class teacher flags set correctly

### Verification
- [ ] **Student list accuracy checked** — Random sample of 10 students verified in Desk
- [ ] **Teacher assignments verified** — Each teacher can see their correct class
- [ ] **No import errors** — Error log is empty or shows only warnings

---

## 🧪 System Testing (Day 3-4)

### Marks Entry Test
- [ ] **Test Assessment Plan created** — One plan per test subject/class
- [ ] **Test marks entered** — Teachers can submit marks
- [ ] **Auto-grading works** — Marks calculate grades correctly
- [ ] **CSV import/export works** — Can download, edit, re-upload marks

### Workflow Test
- [ ] **Report Cards generated** — `generate_report_cards()` creates cards without errors
- [ ] **Class positions calculated** — Ranking appears correctly
- [ ] **Approval workflow works** — Can transition: Pending → Reviewed → Approved → Published
- [ ] **Locking mechanism works** — Cannot edit after approval

### Portal Test
- [ ] **Student portal loads** — `/my-reports` accessible, shows grades
- [ ] **Parent portal loads** — Guardian can see child's grades
- [ ] **PDF download works** — Report card downloads as valid PDF file
- [ ] **Print function works** — Can print to local printer or PDF

### Email Test
- [ ] **Email configuration tested** — Test email sent successfully
- [ ] **Report email works** — Published report generates email with PDF attachment
- [ ] **Email received** — Parent email account receives report
- [ ] **PDF attachment valid** — PDF opens and displays correctly

### Permission Test
- [ ] **Student cannot see other students' grades** — Negative test passes
- [ ] **Parent can see all linked children** — Positive test passes
- [ ] **Teacher cannot approve reports** — Only headmaster can approve
- [ ] **Headmaster sees all classes** — Verified in dashboard

---

## 🔒 Security & Backup (Day 4-5)

### Security Setup
- [ ] **Default admin password changed** — No default passwords remain
- [ ] **SSL certificate installed** (if using HTTPS) — HTTPS works without warnings
- [ ] **Firewall configured** — Only port 8080 (or 443 for HTTPS) exposed to school network
- [ ] **Server hardened** — OS updates installed, unnecessary services disabled
- [ ] **Docker secrets managed** — `.env` file secured (not in Git, read-only by admin)

### Backup Configuration
- [ ] **Backup script tested** — `docker compose exec backend bench backup` runs without error
- [ ] **Backup location verified** — Files saved to `/opt/edupro-sms/frappe_docker/sites/` or specified location
- [ ] **Backup retention policy set** — Weekly backups kept for 4 weeks, monthly backups for 1 year
- [ ] **Restore procedure tested** — Can restore from a backup (test on separate instance)
- [ ] **Off-site backup configured** — Backups copied to external drive or cloud storage
- [ ] **Backup schedule automated** — Cron job (Linux) or Task Scheduler (Windows) running weekly

### Monitoring Setup
- [ ] **Log monitoring enabled** — Error log accessible: Desk → Maintenance → Error Log
- [ ] **Disk space monitored** — Script or dashboard shows available disk space
- [ ] **Service health check** — Can verify all containers running: `docker compose ps`

---

## 📧 Communication & Training (Day 5-6)

### Staff Training
- [ ] **Headmaster trained** — Can approve reports, view dashboards
- [ ] **Teachers trained** — Can enter marks, view feedback
- [ ] **Class teachers trained** — Can review and comment on reports
- [ ] **Bursar trained** — Can create fees, track payments
- [ ] **IT support staff trained** — Can troubleshoot basic issues and restart services

### Parent/Student Communication
- [ ] **Pilot group notified** — First cohort of parents informed about system
- [ ] **Login credentials distributed** — Username/password sent to parents securely
- [ ] **Quick start guide provided** — `USER_QUICKSTART.md` shared with parents/students
- [ ] **Technical support contact provided** — School IT email/phone given to parents

---

## ✅ Pre-Go-Live Verification (Day 7 before launch)

### Final Checklist
- [ ] **System load test passed** — Can handle expected number of concurrent users
- [ ] **All 12 test scenarios passed** — See `docs/07_Testing.md` for full test suite
- [ ] **Backup works & restores** — Successfully restored from backup on test instance
- [ ] **Disaster recovery documented** — Steps to recover in case of failure
- [ ] **Performance targets met** — PDF generation < 5 sec/report, marks save < 1 sec

### User Acceptance Testing (UAT)
- [ ] **Sample marks entered** — Real test data in system
- [ ] **Sample report generated** — PDF looks correct, print format works
- [ ] **Sample approval workflow** — Headmaster approved a test report
- [ ] **Sample parent email** — Test parent received email with PDF
- [ ] **Stakeholders signed off** — Headmaster, admin, IT confirm ready for go-live

---

## 🚀 Go-Live Day

### Pre-Launch
- [ ] **Final full backup taken** — Backup stored on external drive
- [ ] **All staff online and ready** — Teachers, headmaster, bursar available
- [ ] **Help desk staffed** — IT support ready to answer questions
- [ ] **Communication channels open** — Slack/WhatsApp group for urgent issues

### Launch
- [ ] **Announcement sent** — Email/SMS to all staff notifying of system launch
- [ ] **First teachers log in** — Monitor for issues
- [ ] **First marks entered** — Monitor data entry
- [ ] **First report approved** — Monitor workflow
- [ ] **First parent email sent** — Verify delivery to parent inbox

### Post-Launch
- [ ] **System running smoothly** — No major errors in Error Log
- [ ] **Users finding the system intuitive** — Minimal support requests
- [ ] **First week issues documented** — Any bugs or UX issues logged
- [ ] **Follow-up training scheduled** — Any staff needing additional help identified

---

## 📋 Ongoing Maintenance

### Daily (Automated)
- [ ] ✅ Automatic backups running (scheduled)
- [ ] ✅ Monitoring alerts configured

### Weekly
- [ ] **Manual backup verification** — Download and verify backup file
- [ ] **Error log review** — Check for unexpected errors
- [ ] **Performance review** — Spot check response times

### Monthly
- [ ] **Docker update check** — `docker compose pull && docker compose up -d`
- [ ] **Disk space review** — Ensure adequate space remains
- [ ] **User feedback review** — Collect and prioritize feature requests
- [ ] **Security update check** — Apply OS and Docker security updates

### Quarterly
- [ ] **Full system audit** — Review all data, users, permissions
- [ ] **Capacity planning** — Anticipate growth (more students, more data)
- [ ] **Disaster recovery drill** — Test restore from backup

---

## 🆘 Emergency Procedures

### If system won't start
```bash
# Check container status
docker compose ps

# View logs for errors
docker compose logs backend

# Restart all services
docker compose restart

# If still failing, restart Docker
systemctl restart docker  # Linux
```

### If database is corrupted
```bash
# Restore from latest backup
docker compose exec backend bench restore-backup <path-to-backup>

# Restart
docker compose restart
```

### If out of disk space
```bash
# Check disk usage
df -h

# Clean old backups (keep recent ones!)
rm /path/to/old/backups/*

# Clean Docker cache (removes unused containers/images)
docker system prune
```

### If reports won't generate
1. Check container logs: `docker compose logs backend`
2. Verify PDF service running: `docker compose ps | grep frontend`
3. Restart PDF service: `docker compose restart frontend`
4. Try report generation again

---

## 📞 Support Resources

| Issue | Resource |
|-------|----------|
| Installation problems | INSTALLATION_GUIDE.md |
| User questions | USER_QUICKSTART.md |
| Setup questions | FIRST_TIME_SETUP.md |
| Technical issues | TROUBLESHOOTING_GUIDE.md |
| Architecture questions | README.md + docs/ |
| Bugs/features | https://github.com/ttshava/edupro-sms |

---

**Document Version:** 1.0  
**For Edupro SMS v1.0 Stable**
