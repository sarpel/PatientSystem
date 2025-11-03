# Security Configuration Guide

## Overview

This document provides critical security guidance for deploying the Clinical AI Assistant system. **Failure to follow these guidelines may result in security vulnerabilities.**

## Environment Variables Security

### Critical Security Rules

1. **NEVER commit actual credentials to version control**
2. **ALWAYS use strong, randomly generated passwords**
3. **ALWAYS rotate credentials regularly**
4. **ALWAYS use environment-specific configurations**

### Required Environment Variables

The following environment variables **MUST** be set before deploying to production:

#### Database Credentials
```bash
DB_USER=clinicalai_user
DB_PASSWORD=<STRONG_RANDOM_PASSWORD>
SA_PASSWORD=<STRONG_RANDOM_PASSWORD>
```

**Requirements:**
- Minimum 32 characters
- Mix of uppercase, lowercase, numbers, and special characters
- Generated using cryptographically secure random generator

#### Application Security
```bash
SECRET_KEY=<STRONG_RANDOM_KEY>
```

**Requirements:**
- Minimum 64 characters
- Generate using: `openssl rand -base64 64`

#### Redis Password
```bash
REDIS_PASSWORD=<STRONG_RANDOM_PASSWORD>
```

**Requirements:**
- Minimum 32 characters
- No dictionary words

#### Monitoring Credentials
```bash
GRAFANA_ADMIN_PASSWORD=<STRONG_RANDOM_PASSWORD>
```

**Requirements:**
- Minimum 20 characters
- Change default immediately after first login

## Setup Instructions

### Development Environment

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Set development-safe values:**
   - Use the `.env.development` template
   - Development passwords can be simpler but still unique
   - Never use production credentials in development

3. **Git Ignore:**
   - Verify `.env` is in `.gitignore`
   - Never commit `.env` file

### Production Environment

1. **Copy the production example:**
   ```bash
   cp .env.production.example .env
   ```

2. **Generate secure passwords:**
   ```bash
   # Database passwords
   openssl rand -base64 32

   # Secret key
   openssl rand -base64 64

   # Redis password
   openssl rand -base64 32

   # Grafana password
   openssl rand -base64 24
   ```

3. **Set all required variables:**
   - Replace ALL `CHANGE_ME_*` values
   - Verify no placeholders remain: `grep -r "CHANGE_ME" .env`

4. **Secure the .env file:**
   ```bash
   chmod 600 .env
   chown root:root .env
   ```

5. **Verify configuration:**
   ```bash
   docker-compose config
   ```

## Docker Secrets Alternative

For enhanced security in Docker Swarm or production environments, use Docker secrets:

1. **Create secrets:**
   ```bash
   echo "your-strong-password" | docker secret create db_password -
   echo "your-redis-password" | docker secret create redis_password -
   echo "your-secret-key" | docker secret create app_secret_key -
   ```

2. **Update docker-compose.yml to use secrets:**
   ```yaml
   services:
     api:
       secrets:
         - db_password
         - app_secret_key

   secrets:
     db_password:
       external: true
     app_secret_key:
       external: true
   ```

## Security Checklist

Before deploying to production:

- [ ] All `CHANGE_ME_*` values replaced with strong passwords
- [ ] `.env` file has correct permissions (600)
- [ ] `.env` is NOT committed to version control
- [ ] All passwords are minimum required length
- [ ] Passwords generated using cryptographically secure method
- [ ] CORS_ORIGINS set to actual production domains only
- [ ] DEBUG=false in production
- [ ] COOKIE_SECURE=true in production
- [ ] SSL/TLS certificates configured for HTTPS
- [ ] Firewall rules configured to restrict database access
- [ ] Regular security audits scheduled
- [ ] Backup encryption enabled
- [ ] Monitoring and alerting configured

## Password Rotation

Passwords should be rotated regularly:

1. **Database passwords:** Every 90 days
2. **Application secret key:** Every 180 days
3. **Redis password:** Every 90 days
4. **Grafana admin password:** Every 90 days
5. **AI API keys:** As required by provider

### Rotation Procedure

1. Generate new password
2. Update `.env` file
3. Recreate affected containers:
   ```bash
   docker-compose up -d --force-recreate <service-name>
   ```
4. Verify service functionality
5. Update backup documentation

## Incident Response

If credentials are compromised:

1. **Immediately rotate all affected credentials**
2. **Review access logs for unauthorized access**
3. **Scan for data exfiltration**
4. **Update firewall rules if needed**
5. **Document incident and remediation steps**
6. **Notify stakeholders as required**

## GitGuardian Integration

This repository uses GitGuardian to scan for accidentally committed secrets.

**If GitGuardian flags a secret:**

1. **DO NOT merge the PR**
2. **Immediately rotate the compromised credential**
3. **Remove the secret from git history:**
   ```bash
   # Use BFG Repo-Cleaner or git filter-branch
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch <file-with-secret>" \
     --prune-empty --tag-name-filter cat -- --all
   ```
4. **Force push (with caution):**
   ```bash
   git push --force --all
   ```
5. **Update the file with environment variable reference**
6. **Re-commit the fixed version**

## Additional Resources

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Docker Secrets Documentation](https://docs.docker.com/engine/swarm/secrets/)
- [GitGuardian Best Practices](https://blog.gitguardian.com/secrets-api-management/)

## Contact

For security concerns or questions:
- Create a private security advisory in GitHub
- Contact the security team directly
- Never discuss security issues in public channels
