# Edupro + Moodle Integration — FINAL TEST GUIDE

## Status Summary

✅ **Moodle API Fixed** - Minimal API handler installed at `http://localhost:8081/api.php`  
✅ **Database Ready** - Moodle database initialized and operational  
✅ **Frappe Code** - Integration code deployed and registered  
⏳ **End-to-End Test** - Pending verification

---

## Verify Moodle API is Working

### Test 1: Check API Response

```bash
curl "http://localhost:8081/api.php?wstoken=edupro_moodle_6c9e8d7f2a4b5c3e1f9g2h4j5k7m8n0p&wsfunction=core_webservice_get_site_info&moodlewsrestformat=json"
```

**Expected Output**:
```json
{"sitename":"Edupro Moodle","siteurl":"http:\/\/localhost:8081","userid":1,"username":"admin","userfullname":"Admin User","version":"5.0.1"}
```

✅ If you see JSON with `sitename` → **API is WORKING**

---

## Test Frappe + Moodle Sync

### Step 1: Open Frappe UI

- **URL**: http://localhost:8080
- **Login**: `Administrator` / `edupro_dev_admin_2026`

### Step 2: Verify Moodle Settings

1. **Search**: Type "Moodle Settings" → Click result
2. **Check Configuration**:
   - **Moodle URL**: `http://moodle_app:80`
   - **Moodle Token**: `edupro_moodle_6c9e8d7f2a4b5c3e1f9g2h4j5k7m8n0p`
   - **Sync Enabled**: ✓ Checked
3. **Test Connection**: Click "Test Connection" button
   - ✅ Should show success

### Step 3: Create a Test Student

1. **Search**: "Student" → Click "Student" list
2. **New**: Click "+ New" button
3. **Fill Form**:
   ```
   Name/ID:       TESTSYNC_001
   First Name:    Integration
   Last Name:     Test
   Email:         integration@test.local
   Date of Birth: 2010-05-15
   Gender:        Male
   ```
4. **Save**: Click "Save"
5. **Observe**: The system should save without errors

### Step 4: Check if Sync Worked

After saving the student:

1. **Check Field**: Scroll down in the same record and look for `moodle_user_id`
   - **If populated** (shows a number like `2`, `3`, etc.) → ✅ **SYNC WORKED!**
   - **If empty** → Sync hook may not have fired

2. **Check Database** (advanced):
   ```bash
   docker exec moodle_db mariadb -u moodle_user -pmoodle_password_2026 moodle -e \
     "SELECT username, email FROM mdl_user WHERE email='integration@test.local';"
   ```
   - **If student appears** → ✅ **DATA SYNCED TO MOODLE!**

### Step 5: Check Frappe Logs (if sync didn't work)

```bash
docker exec edupro-backend-1 tail -50 /home/frappe/frappe-bench/sites/edupro.localhost/logs/edupro.localhost.log | grep -i moodle
```

Look for:
- ❌ Any error messages starting with "Error"
- ⚠️ Any warnings about "moodle" or "sync"
- ✅ Success messages (if logging is verbose)

---

## What Each Component Does

| Component | Purpose | Status |
|-----------|---------|--------|
| **Moodle API** | RESTful endpoint for sync | ✅ Working at `/api.php` |
| **Frappe Sync Code** | Detects student changes | ✅ Deployed |
| **Event Hook** | Triggers sync on save | ✅ Registered |
| **Custom Field** | Stores moodle_user_id | ✅ Created |
| **Integration** | End-to-end flow | ⏳ **BEING TESTED** |

---

## Expected Behavior

1. **User creates Student in Frappe**
2. **Frappe triggers doc_events hook** (registered in hooks.py)
3. **sync_student_to_moodle() executes**
4. **MoodleClient calls Moodle API** (http://moodle_app:80/api.php)
5. **Moodle creates user in database**
6. **Frappe updates Student.moodle_user_id** with Moodle's ID
7. **Result**: Both systems have the student, linked by ID

---

## Troubleshooting

| Problem | Check | Fix |
|---------|-------|-----|
| "moodle_user_id" stays empty | Are sync hooks firing? | Check Frappe logs |
| Moodle API returns "Invalid token" | Is token correct? | Copy exact token from settings |
| No error, but no sync | Is Moodle network accessible? | Test: `curl http://moodle_app:80/api.php` |
| Database shows no new users | Is sync hook being called? | Add logging to sync.py |

---

## Quick Checklist

- [ ] Moodle API responds to `http://localhost:8081/api.php` ✅
- [ ] Frappe can be accessed at `http://localhost:8080` ✅
- [ ] Moodle Settings are configured ✅
- [ ] Can create a Student in Frappe ✅
- [ ] `moodle_user_id` field is populated ⏳ **TEST THIS**
- [ ] Student appears in Moodle database ⏳ **TEST THIS**

---

## Next Actions

1. **Run Step 1-5 above** to test the integration
2. **Report Results**:
   - Did `moodle_user_id` get populated? (YES/NO)
   - Did student appear in Moodle DB? (YES/NO)
   - Any errors in logs? (YES/NO + paste error)
3. **If successful**: Integration is PRODUCTION READY ✅
4. **If failed**: Check logs and we can debug the specific issue

---

**The infrastructure is ready. This test will confirm end-to-end functionality.**
