# Security Checklist for Production Deployment

This document provides a comprehensive security checklist for deploying the FGN Savings Bond Application in production environments.

---

## Pre-Deployment Checklist

### Credentials & Secrets

- [ ] **Admin Password Changed**
  - Generate new bcrypt hash for `ADMIN_PASSWORD_HASH`
  - Use password with 12+ characters, mixed case, numbers, symbols
  - Command: `python -c "import bcrypt; print(bcrypt.hashpw('YourPassword'.encode(), bcrypt.gensalt()).decode())"`

- [ ] **JWT Secret Generated**
  - Update `JWT_SECRET_KEY` in `backend/.env`
  - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`

- [ ] **Default Credentials Removed**
  - Verify no default passwords remain (`admin123`, `password`, etc.)
  - Change default admin username if needed

### Environment Configuration

- [ ] **Environment Set to Production**
  ```
  ENVIRONMENT=production
  ```

- [ ] **Debug Mode Disabled**
  - Verify no debug flags are enabled in FastAPI
  - Remove `--reload` from production uvicorn command

- [ ] **.env Not in Version Control**
  - Confirm `backend/.env` is in `.gitignore`
  - Use secrets management for CI/CD

---

## Network Security

### Firewall Configuration

- [ ] **Required Ports Only**
  - Port 80 (HTTP) - for Nginx
  - Port 443 (HTTPS) - for SSL
  - Internal only: 8000 (backend), 3000 (frontend)

- [ ] **Database Not Publicly Exposed**
  - SQLite database stored inside container
  - No external database ports exposed

- [ ] **Admin Dashboard Protected**
  - Consider IP whitelisting in `nginx/nginx.conf`:
    ```nginx
    location /admin {
        allow 192.168.1.0/24;
        allow 10.0.0.0/8;
        deny all;
        # ... rest of config
    }
    ```
  - Or use VPN for admin access

### SSL/TLS Configuration

- [ ] **HTTPS Enabled**
  - Obtain SSL certificate (Let's Encrypt, commercial CA)
  - Configure in nginx

- [ ] **HTTP to HTTPS Redirect**
  - Add redirect in `nginx/nginx.conf`:
    ```nginx
    server {
        listen 80;
        return 301 https://$server_name$request_uri;
    }
    ```

- [ ] **Strong TLS Configuration**
  - TLS 1.2+ only
  - Strong cipher suites
  - HSTS headers enabled

---

## Container Security

### Docker Configuration

- [ ] **Non-Root User**
  - Backend Dockerfile uses non-root user
  - Verify: `docker exec <container> whoami`

- [ ] **Resource Limits Set**
  - Memory and CPU limits in `docker-compose.yml`
  - Prevents resource exhaustion attacks

- [ ] **Read-Only Volumes Where Possible**
  - Nginx config mounted as read-only
  - Only data directories are writable

- [ ] **No Privileged Containers**
  - Verify no `privileged: true` in compose files

### Image Security

- [ ] **Base Images Updated**
  - Use specific version tags (not `latest` in production)
  - Regularly update base images for security patches

- [ ] **Vulnerability Scan Passed**
  - Run Trivy or similar scanner
  - Address critical/high vulnerabilities
  - Command: `trivy image fgn-bond-backend:latest`

---

## Application Security

### API Security

- [ ] **JWT Authentication Active**
  - Admin endpoints require valid JWT
  - Token expiration configured appropriately

- [ ] **CORS Configured**
  - `CORS_ORIGINS` in `.env` limits allowed origins
  - Only allow your frontend domain in production

- [ ] **Rate Limiting**
  - Consider adding rate limiting to sensitive endpoints
  - Nginx or FastAPI middleware

### Input Validation

- [ ] **Form Validation Active**
  - BVN validation (11 digits)
  - Email format validation
  - Phone number validation
  - Currency amount validation (Pydantic schemas)

- [ ] **File Upload Restrictions**
  - Max upload size: 5MB
  - Allowed file types: PDF, JPG, PNG only
  - Files stored outside web root

### Session Management

- [ ] **Secure Cookies**
  - JWT stored in localStorage (ensure XSS protection)
  - Consider httpOnly cookies for production

- [ ] **Token Expiration**
  - Access tokens expire appropriately
  - Logout clears tokens from client

---

## Database Security

### SQLite Hardening

- [ ] **Database File Protected**
  - File permissions restricted (chmod 600)
  - Located in non-public directory

- [ ] **Regular Backups**
  - Automated daily backups
  - Backups stored securely (encrypted)

### Data Protection

- [ ] **Sensitive Data Handling**
  - PII (names, BVN, addresses) stored in database
  - Consider field-level encryption for sensitive data

- [ ] **Backup Encryption**
  - Database backups encrypted at rest
  - Secure backup storage location

---

## Monitoring & Logging

### Log Configuration

- [ ] **Log Rotation Enabled**
  - Docker logging driver configured with size limits
  - Prevents disk exhaustion

- [ ] **Sensitive Data Not Logged**
  - Passwords not in logs
  - BVN/personal data masked or excluded

### Monitoring Setup

- [ ] **Health Checks Active**
  - API health endpoint: `/api/health`
  - Monitoring system alerts on failures

- [ ] **Resource Monitoring**
  - CPU, memory, disk usage monitored
  - Alerts configured for thresholds

- [ ] **Access Logging**
  - Nginx access logs enabled
  - Failed login attempts tracked

---

## Incident Response

### Preparation

- [ ] **Backup Procedures Documented**
  - Regular automated backups
  - Tested restore procedures

- [ ] **Incident Response Plan**
  - Contact list for security incidents
  - Procedures for common scenarios

- [ ] **Recovery Procedures**
  - Documented steps for service restoration
  - Tested disaster recovery

---

## Ongoing Maintenance

### Regular Tasks

| Frequency | Task |
|-----------|------|
| Weekly | Review access logs for anomalies |
| Weekly | Check for failed login attempts |
| Monthly | Update Docker images |
| Monthly | Review and rotate secrets if needed |
| Quarterly | Security audit |
| Quarterly | Penetration testing (if applicable) |
| Annually | Full security review |

### Update Procedures

- [ ] **Dependency Updates**
  - Regular `pip` updates for security patches
  - Regular `npm` updates for frontend
  - Test updates in staging before production

- [ ] **Docker Image Updates**
  - Monitor for security advisories
  - Rebuild images with updated base

---

## Compliance Considerations

### Data Protection

- [ ] **Data Retention Policy**
  - Define how long applications are stored
  - Implement automated data cleanup if required

- [ ] **Privacy Policy**
  - Clear policy on data collection and use
  - Accessible to users

### Audit Trail

- [ ] **Action Logging**
  - Admin actions logged
  - Application submissions tracked
  - Payment changes recorded

---

## Quick Security Commands

```bash
# Check container user
docker exec fgnbond_sub-backend-1 whoami

# Scan image for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image fgn-bond-backend:latest

# Check API health
curl http://localhost/api/health

# Test HTTPS redirect (if configured)
curl -I http://yourdomain.com  # Should return 301 to HTTPS

# View backend logs
docker-compose logs -f backend

# Check database file permissions
docker exec fgnbond_sub-backend-1 ls -la /app/data/

# View failed login attempts in logs
docker-compose logs backend | grep -i "login failed"
```

---

## Contact

For security concerns or to report vulnerabilities, contact the system administrator.
