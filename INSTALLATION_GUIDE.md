# Edupro SMS v1.0 — Installation Guide for School Administrators

**Version:** 1.0 Stable  
**Release Date:** 2026-07-05  
**Support:** https://github.com/ttshava/edupro-sms  

---

## ⚠️ READ THIS FIRST

**This guide is for school IT administrators or system managers installing Edupro SMS on a school server.**

If you are:
- A **teacher, student, or parent** — your school administrator will provide you with login credentials. Read `USER_QUICKSTART.md` instead.
- **Not familiar with Docker or Linux servers** — ask your IT department to follow this guide, or contact support.

**Estimated installation time:** 30-45 minutes (first-time setup)

---

## 🎯 What You're Installing

Edupro SMS is a school management system for:
- Teachers entering student marks
- Administrators approving report cards
- Students and parents viewing grades
- Billing and fee tracking

**Technology:** Runs on Docker (container technology). Your school server runs the application in isolated containers — safe, reliable, and easy to maintain.

---

## 📋 Pre-Installation Checklist

**You will need:**

### Hardware
- [ ] A Linux server (Ubuntu 20.04 LTS or later recommended), OR
- [ ] A Windows Server 2019+, OR
- [ ] A Mac with Docker installed

**Minimum specs:**
- CPU: 2 cores
- RAM: 4GB minimum, 8GB recommended
- Disk: 50GB free space (for OS, app, and database)
- Network: Stable internet connection (for initial setup only; local network after that)

### Software
- [ ] Docker installed (https://docs.docker.com/get-docker/)
- [ ] Docker Compose installed (usually comes with Docker Desktop)
- [ ] Git installed (https://git-scm.com/downloads)
- [ ] Text editor (VS Code, Notepad++, or similar)

### Credentials & Access
- [ ] School name (e.g., "Sunshine International School")
- [ ] School email address (e.g., sms@school.edu.zw)
- [ ] Administrator email (your email)
- [ ] A secure password for the admin account

### Network
- [ ] Static IP address for the server (ask your IT team)
- [ ] Port 8080 available (default; can change if needed)
- [ ] Firewall rules allowing access to port 8080 from school network

**If any of these are missing, STOP and ask your IT department before continuing.**

---

## 🚀 Installation Steps

### Step 1: Prepare Your Server

#### On Linux (Ubuntu 20.04 LTS)

1. **Update system packages:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Docker:**
   ```bash
   sudo apt install -y docker.io docker-compose git
   ```

3. **Add your user to the docker group** (so you don't need `sudo` for every command):
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

4. **Create a folder for Edupro SMS:**
   ```bash
   mkdir -p /opt/edupro-sms
   cd /opt/edupro-sms
   ```

#### On Windows Server

1. **Install Docker Desktop for Windows** (https://docs.docker.com/desktop/install/windows-install/)
2. **Install Git** (https://git-scm.com/download/win)
3. **Open PowerShell as Administrator**
4. **Create a folder:** `C:\edupro-sms`

#### On Mac

1. **Install Docker Desktop for Mac** (https://docs.docker.com/desktop/install/mac-install/)
2. **Install Git:** `brew install git`
3. **Create a folder:** `mkdir -p ~/edupro-sms && cd ~/edupro-sms`

---

### Step 2: Clone the Edupro SMS Repository

Run this command in your terminal/PowerShell:

```bash
git clone https://github.com/ttshava/edupro-sms.git .
```

This downloads all the code (~500MB). **Wait for it to complete.**

---

### Step 3: Configure the Environment

1. **Navigate to the Docker folder:**
   ```bash
   cd frappe_docker
   ```

2. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```
   (If `.env.example` doesn't exist, that's OK — proceed to next step)

3. **Edit the `.env` file** with your text editor. Set these values:

   ```env
   # Database password (create a strong password)
   MARIADB_ROOT_PASSWORD=YourStrongPassword123!

   # Site name (your school's unique identifier, no spaces)
   SITE_NAME=edupro.localhost

   # Admin password (strong password for the admin account)
   ADMIN_PASSWORD=YourAdminPassword456!

   # Server timezone (e.g., UTC, Africa/Harare, Africa/Johannesburg)
   TZ=Africa/Harare
   ```

   **Save the file.**

---

### Step 4: Start Docker Containers

**Important:** Ensure Docker Desktop is running (if on Windows/Mac).

1. **Start the containers:**
   ```bash
   docker compose up -d
   ```

   This downloads container images (~2GB) and starts services. **Wait 3-5 minutes.**

2. **Verify containers are running:**
   ```bash
   docker compose ps
   ```

   You should see 6 services running (all showing `Up`):
   - `backend`
   - `frontend`
   - `mariadb`
   - `redis-cache`
   - `redis-queue`
   - `scheduler`

   If any show `Exiting` or `Not running`, see **Troubleshooting** section.

---

### Step 5: Access the System

1. **Open your browser** and navigate to:
   ```
   http://YOUR_SERVER_IP:8080
   ```

   Replace `YOUR_SERVER_IP` with your server's IP address (e.g., `http://192.168.1.100:8080`).

2. **You should see the login page.**

3. **Login with:**
   - Username: `administrator`
   - Password: (the `ADMIN_PASSWORD` you set in `.env`)

4. **You will see the Frappe Desk interface** (the admin control panel).

---

### Step 6: Initial School Setup

Once logged in:

1. **Click "School Settings"** in the sidebar (or search for it at top).

2. **Click "New" to create your school record:**
   - School Name: Enter your school name
   - School Code: A short code (e.g., `SUNNYS`)
   - Address: School address
   - Phone: School phone number
   - Email: School email
   - Logo: Upload your school logo (PNG/JPG, recommended 200x200px)
   - Motto: School motto (optional)
   - Curriculum Board: Select "Cambridge" or "ZIMSEC" (can change later)
   - Timezone: Select your timezone
   - Status: Set to "Active"

3. **Click "Save".**

---

### Step 7: Create Roles and Admin Users

**Important:** Do this before teachers/students log in.

1. **Click "User" in the sidebar.**

2. **Create user accounts for your staff:**
   - Click "New User"
   - Email: Staff member's email
   - Full Name: Staff member's name
   - Password: A temporary password (they should change it on first login)
   - Roles: Select the appropriate role:
     - **Headmaster:** Principal/Head
     - **Bursar:** Finance manager
     - **Instructor (Teacher):** Subject teachers
     - **Class Teacher:** Class/form teacher (can also be an Instructor)

3. **Click "Save".**

4. **Repeat for all staff members.**

**Note:** Student and Parent (Guardian) accounts can be created later or imported from a CSV file. See `FIRST_TIME_SETUP.md` for batch import.

---

### Step 8: Create Academic Structure

Before teachers can enter marks, you need to set up the academic calendar:

1. **Click "Academic Year"** in the sidebar.
   - Click "New"
   - Enter the year (e.g., "2026")
   - Set Start Date and End Date
   - Click "Save"

2. **Click "Academic Term"** in the sidebar.
   - Click "New" for each term (usually 3 per year)
   - Name: "Term 1", "Term 2", "Term 3"
   - Academic Year: Select the year you created
   - Start Date and End Date for the term
   - Click "Save"

3. **Click "Student Group"** to create classes.
   - Click "New"
   - Name: Class name (e.g., "Form 1A", "Form 2B")
   - Group Based On: Select "Batch"
   - Academic Term: Select the current term
   - Click "Save"

**See `FIRST_TIME_SETUP.md` for a detailed walkthrough with screenshots.**

---

### Step 9: Verify Installation

1. **Open the Headmaster Dashboard:**
   - Log out and log back in as a Headmaster account
   - Go to `/dashboard` in the address bar (e.g., `http://192.168.1.100:8080/dashboard`)
   - You should see a summary dashboard

2. **Check the Teacher Dashboard:**
   - Log in as a teacher account
   - Go to `/dashboard`
   - You should see "Assigned Classes" and "Marks Entry" sections

3. **Check Student Portal:**
   - Go to `/my-reports`
   - You should see "Grades" tab (empty for now, since no marks entered yet)

**If you see these pages, installation is successful!**

---

## 🔧 Maintenance & Operations

### Daily Operations

**No daily maintenance needed.** The system runs automatically.

### Weekly Tasks

- [ ] **Backup your data** (see Backup section below)
- [ ] **Check disk space** (ensure server has free space)

### Monthly Tasks

- [ ] **Review error logs** (in Desk → Maintenance → Error Log)
- [ ] **Update Docker images** (keep security patches current):
  ```bash
  docker compose pull
  docker compose up -d
  ```

### Backup Your Data

**Your data is critical. Back it up regularly.**

1. **Automatic backup** (recommended):
   ```bash
   docker compose exec backend bench backup
   ```

2. **Save the backup file** to an external drive or cloud storage (Google Drive, OneDrive, etc.).

3. **Schedule this weekly:**
   - **Linux:** Create a cron job:
     ```bash
     crontab -e
     # Add this line:
     0 2 * * 0 cd /opt/edupro-sms/frappe_docker && docker compose exec backend bench backup
     ```
   - **Windows:** Use Task Scheduler to run a batch script

**See `DEPLOYMENT_CHECKLIST.md` for detailed backup procedures.**

---

## 🐛 Troubleshooting

### Problem: "Connection refused" when accessing http://SERVER_IP:8080

**Solution:**
1. Verify containers are running: `docker compose ps`
2. If not running, check logs: `docker compose logs backend`
3. Ensure port 8080 is not blocked by firewall: `sudo ufw allow 8080` (Linux)
4. Wait 5 minutes after `docker compose up -d` — services need time to start

### Problem: "Bad gateway" error

**Solution:**
1. Containers may still be starting. Wait 2-3 minutes and refresh.
2. If it persists, restart services:
   ```bash
   docker compose restart
   ```

### Problem: Teachers/Students can't log in

**Solution:**
1. Verify user accounts were created: Go to Desk → User → List
2. Check the password is correct
3. Ensure user has the correct role assigned
4. Try resetting password: Go to User → Select user → Click "Reset Password"

### Problem: "Database connection error"

**Solution:**
1. Verify MariaDB is running: `docker compose ps | grep mariadb`
2. If not running, start it: `docker compose up -d mariadb`
3. Wait 30 seconds and try again
4. If still failing, check logs: `docker compose logs mariadb`

### Problem: "Out of disk space" error

**Solution:**
1. Check available space: `df -h` (Linux/Mac) or `Get-Volume` (Windows)
2. Free up space or add more disk to server
3. Clean Docker cache: `docker system prune` (warning: removes unused containers)

**For more issues, see `TROUBLESHOOTING_GUIDE.md`**

---

## 📞 Getting Help

### If something goes wrong:

1. **Check `TROUBLESHOOTING_GUIDE.md`** (included)
2. **Read the logs:** `docker compose logs backend`
3. **Contact support:** https://github.com/ttshava/edupro-sms/issues
4. **Include:**
   - Error message (from browser or logs)
   - What you were trying to do
   - Output of `docker compose ps`

---

## ✅ Installation Complete!

Congratulations! Your Edupro SMS system is installed and ready.

**Next steps:**

1. Read `FIRST_TIME_SETUP.md` — Complete initial school configuration
2. Read `USER_ONBOARDING_GUIDE.md` — Train staff on their roles
3. Import real student data (see `FIRST_TIME_SETUP.md`)
4. Run a test cycle (marks entry → approval → report generation)

**Your system is now ready for teachers to start entering marks!**

---

## 📄 Additional Resources

| Document | Purpose |
|----------|---------|
| `DEPLOYMENT_CHECKLIST.md` | Step-by-step production deployment |
| `FIRST_TIME_SETUP.md` | Initial school setup & data import |
| `USER_ONBOARDING_GUIDE.md` | Training guide for different roles |
| `TROUBLESHOOTING_GUIDE.md` | Common issues & solutions |
| `USER_QUICKSTART.md` | For teachers/students/parents |
| `README.md` | Technical overview (for IT staff) |

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-05  
**For Edupro SMS v1.0 Stable**
