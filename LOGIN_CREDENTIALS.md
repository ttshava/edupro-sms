# Login Credentials for Testing

## Frappe / Edupro SMS

**URL**: http://localhost:8080

| Field | Value |
|-------|-------|
| **Username** | Administrator |
| **Password** | `edupro_dev_admin_2026` |
| **Site** | edupro.localhost |

---

## Moodle 5.0.1

**URL**: http://localhost:8081

| Field | Value |
|-------|-------|
| **Username** | admin |
| **Password** | `Admin@123` |

---

## Quick Links

| Service | URL | User |
|---------|-----|------|
| **Frappe Admin** | http://localhost:8080 | Administrator / `edupro_dev_admin_2026` |
| **Moodle Admin** | http://localhost:8081 | admin / `Admin@123` |
| **Moodle API Token** | (stored in Moodle Settings) | `edupro_moodle_6c9e8d7f2a4b5c3e1f9g2h4j5k7m8n0p` |

---

## Test Flow

1. **Login to Frappe** → http://localhost:8080 with Administrator credentials above
2. **Configure Moodle Settings**:
   - Search → "Moodle Settings"
   - URL: `http://moodle_app:80`
   - Token: `edupro_moodle_6c9e8d7f2a4b5c3e1f9g2h4j5k7m8n0p`
   - Enable: ✓ Check and Save

3. **Create Test Student** → Create New Student with any details
4. **Verify Sync** → Check `moodle_user_id` field (should be populated)
5. **Login to Moodle** → http://localhost:8081 to see synced user

---

## Database Access (Advanced)

### Frappe Database
```bash
docker exec edupro-db mariadb -uroot -pEduAdm@123 -e "USE edupro; SHOW TABLES;" 
```

### Moodle Database
```bash
docker exec moodle_db mariadb -u moodle_user -p moodle_password_2026 moodle -e "SELECT * FROM mdl_user;"
```

---

**Notes:**
- Both passwords are **dev-only** (not secure for production)
- Moodle admin panel: http://localhost:8081/admin/index.php
- Frappe Desk (admin UI): http://localhost:8080/app/home
