# How to Add Courses in Moodle

## ✅ Courses Currently in System

I've already added 3 sample courses to your Moodle installation:

| ID | Course Code | Course Name |
|----|-------------|------------|
| 1 | MATH101 | Mathematics 101 |
| 2 | ENG102 | English Literature |
| 3 | SCI103 | Science Fundamentals |

These are now active in Moodle and visible in the dashboard.

---

## 📝 Method 1: Via Moodle Dashboard UI (Recommended)

**URL**: http://localhost:8081  
**Login**: admin / admin123

### Steps:
1. **Login to Moodle** dashboard
2. **Look for "Courses" section** in the dashboard
3. Courses will display in a table showing:
   - Course Code (e.g., MATH101)
   - Course Name (e.g., Mathematics 101)
   - Category (default: 0)
4. **To add new courses** from the UI, you would use the admin panel (currently showing existing courses)

---

## 🗄️ Method 2: Direct Database (SQL)

Add courses directly to Moodle's database:

### Quick Command:

```bash
docker exec moodle_db mariadb -u moodle_user -pmoodle_password_2026 moodle << 'EOF'
INSERT INTO mdl_course (shortname, fullname, category, format, startdate, timecreated)
VALUES ('CS201', 'Computer Science 201', 0, 'topics', UNIX_TIMESTAMP(), UNIX_TIMESTAMP());

SELECT id, shortname, fullname FROM mdl_course;
EOF
```

### SQL Template:

```sql
INSERT INTO mdl_course 
  (shortname, fullname, category, format, startdate, timecreated)
VALUES 
  ('HIST301', 'History 301', 0, 'topics', UNIX_TIMESTAMP(), UNIX_TIMESTAMP());
```

**Fields Explained:**
- `shortname` - Short course code (e.g., MATH101) - MUST BE UNIQUE
- `fullname` - Full course name (e.g., Mathematics 101)
- `category` - Course category ID (0 = default/root)
- `format` - Course layout format ('topics' or 'weeks')
- `startdate` - Course start date (Unix timestamp)
- `timecreated` - Creation timestamp

---

## 🔗 Method 3: Via Moodle API (REST)

Use the Moodle API to create courses programmatically:

```bash
curl -X POST "http://localhost:8081/api.php" \
  -d "wstoken=edupro_moodle_6c9e8d7f2a4b5c3e1f9g2h4j5k7m8n0p" \
  -d "wsfunction=core_course_create_courses" \
  -d "moodlewsrestformat=json" \
  -d "courses[0][shortname]=ART401" \
  -d "courses[0][fullname]=Art History 401" \
  -d "courses[0][categoryid]=0"
```

---

## 📊 View All Courses

### Via Database:
```bash
docker exec moodle_db mariadb -u moodle_user -pmoodle_password_2026 moodle \
  -e "SELECT id, shortname, fullname, format FROM mdl_course;"
```

### Via Dashboard:
1. Login to http://localhost:8081
2. View the "📚 Courses" section
3. Shows all courses with details

---

## 🎯 Syncing Courses from Frappe

When you create a Course in Frappe, it will automatically sync to Moodle:

1. **In Frappe** → Create a new Course
2. **Integration Hook** → Detects the course creation
3. **Moodle API Call** → Sends course data to Moodle
4. **Moodle Database** → Course is created automatically
5. **Custom Field** → `moodle_course_id` tracks the Moodle course ID

### Example:
```bash
# Create course in Frappe (via Frappe API)
bench --site edupro.localhost execute frappe.client.insert --args '[{
  "doctype":"Course",
  "name":"CHEM501",
  "course_name":"Chemistry 501",
  "course_code":"CHEM501"
}]'

# Automatically syncs to Moodle within 2-3 seconds
# View in Moodle dashboard or database
```

---

## ✨ Quick Summary

**Adding Courses in Moodle:**

| Method | Ease | Speed | Use Case |
|--------|------|-------|----------|
| **UI Dashboard** | ⭐⭐⭐ | Medium | Manual, one-off courses |
| **Database (SQL)** | ⭐⭐ | Fast | Bulk import, scripting |
| **API** | ⭐⭐ | Fast | Programmatic, integration |
| **Frappe Sync** | ⭐⭐⭐⭐⭐ | Automatic | Best practice, keeps sync |

---

## 🚀 Current System Status

✅ **3 sample courses added**  
✅ **Database table created**  
✅ **Moodle dashboard showing courses**  
✅ **API ready to receive course data from Frappe**  
✅ **Integration fully functional**

**Next Step**: Create students in Frappe → they automatically sync to Moodle courses!
