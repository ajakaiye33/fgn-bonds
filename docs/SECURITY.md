# Security Checklist for Production Deployment

This document provides a comprehensive security checklist for deploying the FGN Savings Bond Application in production environments.

---

## Pre-Deployment Checklist

### Credentials & Secrets

- [ ] **MongoDB Password Changed**
  - Update `MONGO_INITDB_ROOT_PASSWORD` in `.env`
  - Use strong password: `openssl rand -base64 32`

- [ ] **Admin Password Changed**
  - Generate new hash for `ADMIN_PASSWORD_HASH`
  - Use password with 12+ characters, mixed case, numbers, symbols
  - Command: `echo -n "YourPassword" | shasum -a 256 | cut -d' ' -f1`

- [ ] **Secret Key Generated**
  - Update `SECRET_KEY` in `.env`
  - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`

- [ ] **Default Credentials Removed**
  - Verify no default passwords remain (`admin123`, `password`, etc.)

### Environment Configuration

- [ ] **Environment Set to Production**
  ```
  ENVIRONMENT=production
  ```

- [ ] **Debug Mode Disabled**
  - Verify no debug flags are enabled
  - Check Streamlit config for production settings

- [ ] **.env Not in Version Control**
  - Confirm `.env` is in `.gitignore`
  - Use secrets management for CI/CD

---

## Network Security

### Firewall Configuration

- [ ] **Required Ports Only**
  - Port 80 (HTTP) - if using Nginx
  - Port 443 (HTTPS) - for SSL
  - Port 8080 - Admin (consider restricting to internal network)

- [ ] **MongoDB Not Publicly Exposed**
  - In `docker-compose.prod.yml`, MongoDB uses `expose` not `ports`
  - Database accessible only within Docker network

- [ ] **Admin Dashboard Protected**
  - Consider IP whitelisting in `nginx/nginx.conf`:
    ```nginx
    allow 192.168.1.0/24;
    allow 10.0.0.0/8;
    deny all;
    ```
  - Or use VPN for admin access

### SSL/TLS Configuration

- [ ] **HTTPS Enabled**
  - Obtain SSL certificate (Let's Encrypt, commercial CA)
  - Place certificates in `nginx/certs/`

- [ ] **HTTP to HTTPS Redirect**
  - Uncomment redirect in `nginx/nginx.conf`:
    ```nginx
    return 301 https://$server_name$request_uri;
    ```

- [ ] **Strong TLS Configuration**
  - TLS 1.2+ only
  - Strong cipher suites
  - HSTS headers enabled

---

## Container Security

### Docker Configuration

- [ ] **Non-Root User**
  - Dockerfile uses `USER appuser` (already configured)
  - Verify: `docker exec <container> whoami` should show `appuser`

- [ ] **Resource Limits Set**
  - Memory and CPU limits in `docker-compose.prod.yml`
  - Prevents resource exhaustion attacks

- [ ] **Read-Only Volumes Where Possible**
  - Nginx config mounted as `:ro`
  - Application data volumes are writable only where needed

- [ ] **No Privileged Containers**
  - Verify no `privileged: true` in compose files

### Image Security

- [ ] **Base Images Updated**
  - Use specific version tags (not `latest` in production)
  - Regularly update base images for security patches

- [ ] **Vulnerability Scan Passed**
  - Run Trivy or similar scanner
  - Address critical/high vulnerabilities
  - Command: `trivy image fgn-bond-app:latest`

---

## Application Security

### Input Validation

- [ ] **Form Validation Active**
  - BVN validation (11 digits)
  - Email format validation
  - Phone number validation
  - Currency amount validation

- [ ] **File Upload Restrictions**
  - Max upload size configured in Streamlit
  - Allowed file types restricted

### Session Management

- [ ] **CSRF Protection Enabled**
  - Streamlit XSRF protection: `enableXsrfProtection = true`

- [ ] **Secure Cookies**
  - In production, cookies should be:
    - `HttpOnly`
    - `Secure` (HTTPS only)
    - `SameSite=Strict`

---

## Database Security

### MongoDB Hardening

- [ ] **Authentication Enabled**
  - Root user configured with strong password
  - Application uses authenticated connection

- [ ] **Authorization Configured**
  - Application user has minimal required permissions
  - Consider separate read-only user for reporting

- [ ] **Network Binding**
  - MongoDB binds to internal Docker network only
  - Not accessible from host or external networks

### Data Protection

- [ ] **Sensitive Data Handling**
  - PII (names, BVN, addresses) stored securely
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
  - All services have health checks
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

---

## Quick Security Commands

```bash
# Check container user
docker exec fgnbond_sub-web-1 whoami

# Scan image for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image fgn-bond-app:latest

# Check MongoDB is not exposed
netstat -tlnp | grep 27017  # Should show nothing on public interfaces

# Test HTTPS redirect
curl -I http://yourdomain.com  # Should return 301 to HTTPS

# Verify health endpoints
curl -f http://localhost/_stcore/health
```

---

## Contact

For security concerns or to report vulnerabilities, contact the system administrator.
