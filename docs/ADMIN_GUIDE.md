# Admin Dashboard User Guide

This guide covers the FGN Savings Bond Application admin dashboard, used for viewing applications, managing payments, generating DMO reports, and exporting data.

---

## Accessing the Admin Dashboard

### URL

| Environment | URL |
|-------------|-----|
| Docker | http://localhost/admin |
| Local Development | http://localhost:5173/admin |
| Production | https://yourdomain.com/admin |

### Login

1. Navigate to the admin dashboard URL
2. Enter your credentials:
   - **Username:** As configured in `ADMIN_USERNAME` (default: `admin`)
   - **Password:** Plain text password (default: `admin123`)

> **WARNING:** Change default credentials before production deployment!

---

## Dashboard Overview

The admin dashboard has three main tabs:

### 1. Overview Tab

Dashboard metrics with visual analytics.

**Key Metrics:**
- Total applications count
- Total subscription value
- Average subscription value
- Applications this month

**Charts:**
- Applications by type (Individual, Joint, Corporate)
- Applications by tenor (2-Year vs 3-Year)
- Monthly trends over time

### 2. Applications Tab

View and manage all submitted bond applications.

**Features:**
- **Search & Filter**
  - Filter by date range (from/to)
  - Filter by subscription value range (min/max)
  - Filter by tenor (2-Year, 3-Year)
  - Filter by payment status (Pending, Paid, Verified, Rejected)
  - Search by applicant name or reference

- **Application List**
  - Sortable columns
  - Click row to view full details and manage payments
  - Payment status badges (color-coded)

- **Export Options**
  - Export to CSV
  - Export to Excel (with summary sheet)

### 3. DMO Reports Tab

Generate monthly reports for submission to the Debt Management Office.

**Features:**
- **Monthly Summary**
  - Select month and year
  - View total applications and value
  - Breakdown by tenor and applicant type
  - Payment status overview

- **Export DMO Report**
  - Generate Excel report with detailed subscriber list
  - Format ready for DMO submission

- **Submission Tracking**
  - Mark reports as submitted to DMO
  - View submission history with timestamps

---

## Payment Management

### Payment Workflow

```
Application Submitted
         │
         ▼
    ┌─────────┐
    │ Pending │ ← No payment recorded
    └────┬────┘
         │ Record Payment
         ▼
    ┌─────────┐
    │  Paid   │ ← Payment recorded, awaiting verification
    └────┬────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│Verified│ │ Rejected │
└────────┘ └──────────┘
```

### Recording a Payment

1. Go to **Applications** tab
2. Click on an application row to open details
3. Scroll to **Payment Information** section
4. Click **Record Payment**
5. Fill in payment details:
   - **Amount** (in Naira)
   - **Payment Method** (Bank Transfer, Cash, etc.)
   - **Reference Number** (bank reference or transaction ID)
   - **Payment Date**
   - **Notes** (optional)
6. Click **Record Payment** to save

### Uploading Payment Evidence

After recording a payment:

1. In the application details modal, find **Payment Documents**
2. Click the upload area or drag and drop a file
3. Supported formats: PDF, JPG, PNG (max 5MB)
4. File uploads automatically after selection

### Verifying or Rejecting Payments

1. Open application with **Paid** status
2. Review payment details and evidence documents
3. Click **Verify Payment** or **Reject Payment**
4. Add verification notes (optional but recommended)
5. Status updates immediately

---

## Exporting Data

### Export to CSV

1. Apply desired filters (optional)
2. Click **Export CSV** button
3. File downloads with filtered data
4. Opens in Excel, Google Sheets, etc.

### Export to Excel

1. Apply desired filters (optional)
2. Click **Export Excel** button
3. File includes:
   - Summary sheet with totals
   - Detailed applications list
   - Formatted columns

### DMO Report Export

1. Go to **DMO Reports** tab
2. Select month and year
3. Click **Export Excel**
4. Report includes:
   - Monthly summary
   - Subscriber details
   - Payment status breakdown

---

## Filtering Applications

### By Date Range

1. Click "From" date picker
2. Select start date
3. Click "To" date picker
4. Select end date
5. Results filter automatically

### By Value Range

1. Enter minimum value (optional)
2. Enter maximum value (optional)
3. Results filter automatically

### By Tenor

1. Select from dropdown: "2-Year" or "3-Year"
2. Results filter immediately

### By Payment Status

1. Select from dropdown:
   - **Pending** - No payment recorded
   - **Paid** - Payment recorded, not verified
   - **Verified** - Payment confirmed
   - **Rejected** - Payment rejected
2. Results filter immediately

### Clear Filters

Click **Clear Filters** button to reset all filters

---

## Troubleshooting

### Cannot Log In

1. **Verify Credentials**
   - Check `ADMIN_USERNAME` in `backend/.env`
   - Check `ADMIN_PASSWORD_HASH` matches your password

2. **Clear Browser Data**
   - Clear localStorage for the admin URL
   - Try incognito/private window

3. **Check Backend Logs**
   ```bash
   docker-compose logs backend
   ```

### No Data Showing

1. **Check API Connection**
   ```bash
   curl http://localhost/api/health
   ```

2. **Verify Database**
   - Submit a test application via user form
   - Refresh admin dashboard

3. **Check Filters**
   - Clear all filters to see all data
   - Verify date range includes existing applications

### Export Not Working

1. **Check Browser Downloads**
   - Ensure downloads aren't blocked
   - Check default download location

2. **File Size**
   - Very large exports may be slow
   - Use filters to reduce data size

3. **Check Console**
   - Open Developer Tools (F12)
   - Look for network errors

### Payment Upload Failed

1. **Check File Size**
   - Maximum 5MB per file

2. **Check File Type**
   - Only PDF, JPG, PNG allowed

3. **Check Backend Storage**
   ```bash
   docker exec fgnbond_sub-backend-1 ls -la /app/uploads/
   ```

---

## Generating Password Hash

To change your admin password:

```bash
python -c "import bcrypt; print(bcrypt.hashpw('YourNewPassword'.encode(), bcrypt.gensalt()).decode())"
```

Then update `ADMIN_PASSWORD_HASH` in `backend/.env` and restart:
```bash
docker-compose restart backend
```

---

## Best Practices

### Regular Tasks

| Frequency | Task |
|-----------|------|
| Daily | Review new applications |
| Daily | Process pending payments |
| Weekly | Verify recorded payments |
| Monthly | Generate DMO report |
| Monthly | Export and backup data |

### Payment Processing

- **Verify promptly** - Don't let payments sit in "Paid" status
- **Add notes** - Document any issues or special circumstances
- **Upload evidence** - Always attach payment proof

### Data Management

- **Regular Exports** - Keep offline backups of application data
- **Filter before export** - Export only needed data
- **Archive monthly** - Keep organized records by month

### Security

- **Log Out** - Always log out when finished
- **Password Rotation** - Change admin password periodically
- **Access Review** - Regularly review who has admin access
- **Use HTTPS** - Always use secure connection in production

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Escape` | Close modal/details |
| `Ctrl+F` / `Cmd+F` | Search in current view |

---

## Support

For technical issues:
1. Check [Troubleshooting](#troubleshooting) section
2. Review application logs: `docker-compose logs`
3. Contact system administrator

For feature requests or bugs, create an issue in the project repository.
