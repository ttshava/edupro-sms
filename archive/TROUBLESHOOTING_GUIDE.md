# Edupro SMS v1.0 — Troubleshooting Guide

**Solutions for common issues in production.**

---

## 🔴 System Won't Start

### Symptom: Containers not starting, keep restarting

**Check 1: Docker running?**
```bash
docker ps
```
If no output or error, Docker daemon isn't running.

**Solution:**
- **Linux:** `sudo systemctl start docker`
- **Windows:** Start Docker Desktop
- **Mac:** Start Docker Desktop

---

### Symptom: Port 8080 already in use

**Check:** Is another service using port 8080?
```bash
# Linux/Mac
lsof -i :8080

# Windows
netstat -ano | findstr :8080
```

**Solutions:**
1. **Stop the other service** using port 8080, OR
2. **Change Edupro port:** In `docker-compose.override.yml`, change `8080:8080` to `8081:8080` (or another port), then restart

---

### Symptom: "Not enough disk space"

**Check available disk:**
```bash
df -h  # Linux/Mac
Get-Volume  # Windows
```

**Solution:** Free up space on the server
```bash
# Remove old backups (keep recent ones!)
rm /opt/edupro-sms/frappe_docker/sites/edupro.localhost/private/backups/old_backup.sql.gz

# Clean Docker unused containers/images
docker system prune -a  # Warning: removes unused images

# Check database size
du -sh /opt/edupro-sms/frappe_docker/sites/
```

---

## 🟠 Can't Access the System

### Symptom: "Connection refused" or "Server not responding"

**Check 1: Containers running?**
```bash
docker compose ps
```
All should show status "Up".

**Check 2: Firewall blocking?**
```bash
# Linux: Allow port 8080
sudo ufw allow 8080
sudo ufw enable

# Windows: Check Windows Firewall settings
# Mac: System Preferences → Security → Firewall
```

**Check 3: Wrong IP?**
```bash
# Get server IP
hostname -I  # Linux
ipconfig  # Windows PowerShell
ifconfig  # Mac
```

Use the correct IP: `http://YOUR_SERVER_IP:8080`

---

### Symptom: "Bad Gateway" error

**Solution 1:** Wait 2-3 minutes
- Containers take time to initialize on first startup

**Solution 2:** Check backend logs
```bash
docker compose logs backend
```
Look for error messages.

**Solution 3:** Restart containers
```bash
docker compose restart
```

Wait 30 seconds and try again.

---

## 🟡 Login Issues

### Symptom: "Invalid username or password"

**Check 1: Username is email**
- Edupro SMS uses email as username, not a simple username

**Check 2: Account exists**
- Go to Desk → User → List
- Is the user in the list?

**Check 3: User is active**
- Go to Desk → User → Select user
- Check "Enabled" checkbox is checked
- Check "Disabled" is NOT checked

**Solution:** Reset password
```bash
# As admin, in Desk:
# Select user → Click "Reset Password" button
# A temporary password will be generated
```

---

### Symptom: "User does not have permission to access this resource"

**Problem:** User doesn't have the correct role

**Check:** In Desk, go to User → Select user:
- Verify "Roles" section lists the appropriate role (Teacher, Headmaster, etc.)
- If missing, add role

**Solution:** Assign correct role
1. Edit user
2. In "Roles" section, click "Add Row"
3. Select role: Teacher, Headmaster, Bursar, etc.
4. Click "Save"

---

## 🔴 Database Issues

### Symptom: "Database connection error" or "Lost connection to MySQL server"

**Check database container:**
```bash
docker compose ps | grep mariadb
```
Should show status "Up".

**Solution 1:** Restart database
```bash
docker compose restart mariadb
docker compose restart backend  # Also restart backend to reconnect
```

**Solution 2:** Check database logs
```bash
docker compose logs mariadb
```
Look for error messages.

**Solution 3:** Verify database password matches `.env`
```bash
# In .env file:
MARIADB_ROOT_PASSWORD=YourPassword
```
Make sure password is correct.

---

### Symptom: "Access denied for user 'root'@'mariadb'"

**Problem:** Database password mismatch

**Solution:** 
1. Stop containers: `docker compose down`
2. Edit `.env` — update MARIADB_ROOT_PASSWORD to a new password
3. Delete database volume: `docker volume rm frappe_docker_db-data`
4. Start containers: `docker compose up -d`
5. Wait 2 minutes and try again

---

## 📧 Email Issues

### Symptom: "Email not sending" or "No outgoing account configured"

**Problem:** SMTP not configured

**Solution:**
1. Go to Desk → Email Account
2. Create a new Email Account:
   - Email Address: school email
   - Server: SMTP server (ask your email provider)
   - Port: Usually 587 or 465
   - Username: Your email
   - Password: Your email password
   - Use TLS: Checked (for port 587)
   - Use SSL: Checked (for port 465)
3. Click "Save"
4. Click "Test Email" button

**Common email providers:**

| Provider | SMTP Server | Port |
|----------|-------------|------|
| Gmail | smtp.gmail.com | 587 |
| Outlook | smtp.office365.com | 587 |
| Yahoo | smtp.mail.yahoo.com | 465 |
| Zimbra | mail.your-domain.com | 587 |
| Custom (ask IT) | Ask your IT dept | 587 |

---

### Symptom: "Email test fails with SSL/TLS error"

**Solution 1:** Try port 465 instead of 587
```
Use TLS: Unchecked
Use SSL: Checked
Port: 465
```

**Solution 2:** Try port 587
```
Use TLS: Checked
Use SSL: Unchecked
Port: 587
```

**Solution 3:** Disable SSL/TLS (less secure, not recommended)
- Uncheck both TLS and SSL
- Use port 25

---

## 📝 Marks Entry Issues

### Symptom: "No Assessment Plan found for this class/subject"

**Problem:** You need to create Assessment Plans before marks entry

**Solution:**
1. Go to Desk → Assessment Plan
2. Click "New"
3. Fill in:
   - Student Group: The class
   - Course: The subject
   - Academic Term: The current term
   - Exam Name: "Term 2 Exam" or similar
   - Schedule Date: Pick a date
4. In Criteria section, add two rows:
   - Term Mark (max 100)
   - Exam Mark (max 100)
5. Click "Save"

**Note:** You need one Assessment Plan per class/subject/term combination.

---

### Symptom: "Cannot submit marks — missing required field"

**Problem:** Not all students have marks entered

**Solution:**
1. Go to marks entry page
2. Look for rows with status "Missing"
3. Fill in marks for those students
4. All rows should show "Entered"
5. Then click "Submit"

---

### Symptom: "Mark is above maximum score"

**Problem:** Student mark exceeds 100

**Solution:**
1. Check the mark you entered (should be 0-100)
2. Correct to valid number
3. Save again

---

## 📋 Report Card Issues

### Symptom: "Can't generate report cards" or "Error generating report"

**Check logs:**
```bash
docker compose logs backend | grep -i report
```

**Common causes:**

1. **Missing Assessment Results** — Not all students have submitted marks
   - Solution: Check all students have marks for all required subjects

2. **Missing grading scale** — Grading scale not linked to Program
   - Solution: Go to Program → Edit → Curriculum field → Select grading scale

3. **Permission error** — User doesn't have permission to generate
   - Solution: Only Headmaster and Admin can generate; verify role

---

### Symptom: "Report card PDF won't download"

**Problem:** PDF generation failing

**Check:** Is `frontend` container running?
```bash
docker compose ps | grep frontend
```
Should show "Up".

**Solution 1:** Restart frontend
```bash
docker compose restart frontend
```

**Solution 2:** Reload page in browser
- Press Ctrl+F5 (Windows/Linux) or Cmd+Shift+R (Mac)

**Solution 3:** Try different browser
- Try Chrome, Firefox, or Edge

---

## 🔒 Permission Issues

### Symptom: "Permission denied" or "You don't have access"

**Problem:** User role doesn't allow that action

**Check current user's role:**
- Desk → Click username (top right) → Show roles

**Verify role permissions:**
- Desk → Role Permissions Manager
- Select the role
- Check what they're allowed to do

**Common permission fixes:**

| Issue | Solution |
|-------|----------|
| Teacher can't enter marks | Add "Instructor" role to user |
| Headmaster can't approve | Ensure "Headmaster" role assigned |
| Student can't see grades | Must be "Student" role + Student record created |
| Parent can't see child's grades | Create "Student" record + link Guardian via Guardian field |

---

## 📊 Performance Issues

### Symptom: "System is slow" or "Marks entry is laggy"

**Check system resources:**
```bash
# Linux
top
docker stats

# Windows PowerShell
Get-Process docker* | select -Property Name, CPU, Memory
```

**If CPU/Memory high:**

1. **Increase Docker resources** (Windows/Mac):
   - Docker Desktop → Preferences → Resources
   - Increase CPUs and Memory
   - Restart Docker

2. **Optimize database:**
   ```bash
   docker compose exec mariadb optimize table frappe.tabassessment_result
   ```

3. **Clear cache:**
   ```bash
   docker compose exec backend bench clear-cache
   docker compose restart backend
   ```

---

### Symptom: "PDF generation is very slow"

**Normal performance:** 1-3 seconds per PDF

**If slower:**

1. Check server load: `top` or Task Manager
2. Ensure frontend container is running: `docker compose ps | grep frontend`
3. Try restarting: `docker compose restart`

---

## 🔄 Backup & Recovery Issues

### Symptom: "Backup fails" or "Can't restore backup"

**Check backup size:**
```bash
ls -lh /opt/edupro-sms/frappe_docker/sites/edupro.localhost/private/backups/
```

**If disk full:** Delete old backups
```bash
rm /opt/edupro-sms/frappe_docker/sites/edupro.localhost/private/backups/2026-06*.sql.gz
```

**To restore from backup:**
```bash
# List available backups
ls /opt/edupro-sms/frappe_docker/sites/edupro.localhost/private/backups/

# Restore specific backup
docker compose exec backend bench restore-backup /backup-file-path/backup.sql.gz

# Restart
docker compose restart
```

---

## 🐛 Common Gotchas

### Python file changes don't take effect

**Problem:** Gunicorn caches imported modules

**Solution:** Restart containers (not just `clear-cache`)
```bash
docker compose restart backend queue-short queue-long scheduler websocket
```

---

### Teachers see other classes' marks

**Problem:** Permission scoping issue

**Solution:** Check `teacher_permissions.py` is loaded correctly
```bash
docker compose logs backend | grep permission
docker compose restart backend
```

---

### Email says "Cannot connect to SMTP server"

**Problem:** Firewall blocking outgoing email

**Solution:** Ask IT to allow outbound connections to SMTP server (port 587 or 465)

---

## 📞 Still Can't Fix It?

1. **Check all logs:**
   ```bash
   docker compose logs > /tmp/edupro-logs.txt
   ```

2. **Collect info:**
   - Output of `docker compose ps`
   - Relevant error from `docker compose logs`
   - What you were trying to do
   - When it started happening

3. **Contact support:**
   - GitHub Issues: https://github.com/ttshava/edupro-sms/issues
   - Include: logs, Docker version, OS, steps to reproduce

---

**Document Version:** 1.0  
**For Edupro SMS v1.0 Stable**
