# Admin Dashboard User Guide

This guide covers the FGN Savings Bond Application admin dashboard, used for viewing applications, generating reports, and exporting data.

---

## Accessing the Admin Dashboard

### URL

| Environment | URL |
|-------------|-----|
| Docker (via Nginx) | http://localhost:8080 |
| Docker (direct) | http://localhost:8502 |
| Production | https://admin.yourdomain.com |

### Login

1. Navigate to the admin dashboard URL
2. Enter your credentials:
   - **Username:** As configured in `ADMIN_USERNAME` (default: `admin`)
   - **Password:** Plain text password (will be hashed and compared)

> **Note:** If login fails, verify your `ADMIN_PASSWORD_HASH` in `.env` matches your password. See [Generating Password Hash](#generating-password-hash).

---

## Dashboard Overview

The admin dashboard provides three main sections:

### 1. Applications Tab

View and manage all submitted bond applications.

**Features:**
- **Search & Filter**
  - Filter by date range
  - Filter by applicant type (Individual, Joint, Corporate)
  - Filter by status
  - Search by applicant name or reference

- **Application List**
  - Sortable columns
  - Pagination for large datasets
  - Click row to view full details

- **Application Details**
  - Personal information
  - Bond details (amount, tenor)
  - Bank information
  - Submission timestamp

### 2. Analytics Tab

Visual insights into application data.

**Charts & Metrics:**
- **Application Trends**
  - Daily/weekly/monthly submission counts
  - 7-day moving average trend line

- **Bond Value Distribution**
  - Breakdown by amount ranges
  - Pie chart by applicant type

- **Growth Metrics**
  - Week-over-week comparison
  - Month-over-month growth rate

- **Top Applicants**
  - Highest value applications
  - Most frequent applicants (corporate)

### 3. Reports Tab

Generate and export reports.

**Report Types:**
- Monthly subscription summary
- Custom date range reports
- Applicant type breakdown

---

## Common Tasks

### Viewing Application Details

1. Go to **Applications** tab
2. Use filters to narrow down results (optional)
3. Click on any row to expand details
4. View complete application information

### Exporting Data

**Export to CSV:**
1. Apply desired filters
2. Click **Export CSV** button
3. File downloads automatically

**Export to Excel:**
1. Apply desired filters
2. Click **Export Excel** button
3. File downloads with formatting preserved

**Export Options:**
- All applications (no filter)
- Filtered results only
- Date range specific

### Generating Monthly Reports

1. Navigate to **Reports** tab
2. Select the month and year
3. Click **Generate Report**
4. View summary statistics
5. Export if needed

### Filtering Applications

**By Date Range:**
1. Click date picker for "From" date
2. Click date picker for "To" date
3. Results update automatically

**By Applicant Type:**
1. Select from dropdown: Individual, Joint, or Corporate
2. Results filter immediately

**By Status:**
1. Select status from dropdown
2. View applications matching criteria

---

## Analytics Explained

### Application Trends Chart

Shows the number of applications over time.

- **Blue line:** Daily application count
- **Orange line:** 7-day moving average (smoothed trend)
- **Hover:** View exact counts for any date

**Interpreting:**
- Upward trend indicates growing interest
- Spikes may correlate with bond offering announcements
- Moving average smooths daily fluctuations

### Bond Value Distribution

Displays how application amounts are distributed.

**Bar Chart:**
- X-axis: Amount ranges (e.g., 5K-10K, 10K-50K)
- Y-axis: Number of applications
- Color-coded by applicant type

**Pie Chart:**
- Percentage breakdown by applicant type
- Hover for exact percentages

### Growth Metrics

**Week-over-Week (WoW):**
- Compares current week to previous week
- Green: Growth
- Red: Decline
- Percentage change displayed

**Month-over-Month (MoM):**
- Compares current month to previous month
- Useful for longer-term trend analysis

---

## Troubleshooting

### Cannot Log In

1. **Verify Username**
   - Check `ADMIN_USERNAME` in `.env`
   - Default is `admin`

2. **Verify Password Hash**
   - Generate hash of your password
   - Compare with `ADMIN_PASSWORD_HASH` in `.env`

3. **Clear Browser Data**
   - Clear cookies for the admin URL
   - Try incognito/private window

4. **Check Logs**
   ```bash
   docker-compose logs admin
   ```

### No Data Showing

1. **Check Database Connection**
   ```bash
   docker-compose logs mongodb
   ```

2. **Verify Data Exists**
   - Submit a test application via user form
   - Refresh admin dashboard

3. **Check Filters**
   - Ensure date range includes existing applications
   - Clear all filters to see all data

### Charts Not Loading

1. **Check Browser Console**
   - Open Developer Tools (F12)
   - Look for JavaScript errors

2. **Verify Plotly Loaded**
   - Charts require Plotly library
   - Check network tab for failed requests

3. **Restart Admin Service**
   ```bash
   docker-compose restart admin
   ```

### Export Not Working

1. **Check Browser Downloads**
   - Ensure downloads aren't blocked
   - Check default download location

2. **File Size**
   - Very large exports may time out
   - Use filters to reduce data size

---

## Generating Password Hash

To change your admin password:

**macOS/Linux:**
```bash
echo -n "YourNewPassword" | shasum -a 256 | cut -d' ' -f1
```

**Windows (PowerShell):**
```powershell
python -c "import hashlib; print(hashlib.sha256('YourNewPassword'.encode()).hexdigest())"
```

**Python:**
```python
import hashlib
print(hashlib.sha256("YourNewPassword".encode()).hexdigest())
```

Then update `ADMIN_PASSWORD_HASH` in your `.env` file and restart:
```bash
docker-compose restart admin
```

---

## Best Practices

### Regular Tasks

| Frequency | Task |
|-----------|------|
| Daily | Review new applications |
| Weekly | Export weekly report |
| Monthly | Generate monthly summary |
| Monthly | Archive/backup data |

### Data Management

- **Regular Exports:** Keep offline backups of application data
- **Archiving:** Consider archiving old applications periodically
- **Monitoring:** Watch for unusual patterns (fraud indicators)

### Security

- **Log Out:** Always log out when finished
- **Password Rotation:** Change admin password periodically
- **Access Review:** Regularly review who has admin access
- **IP Restriction:** Consider IP whitelisting for admin access

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+F` / `Cmd+F` | Search in current view |
| `Escape` | Close modal/details |
| `Enter` | Confirm action |

---

## Support

For technical issues:
1. Check [Troubleshooting](#troubleshooting) section
2. Review application logs: `docker-compose logs admin`
3. Contact system administrator

For feature requests or bugs, create an issue in the project repository.
