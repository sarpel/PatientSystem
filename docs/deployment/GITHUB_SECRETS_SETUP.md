# GitHub Secrets Setup Guide

## Overview

This guide explains how to configure GitHub Secrets for the Clinical AI Assistant CI/CD pipeline. These secrets are required for automated testing and deployment workflows.

## Required GitHub Secrets

### For Testing (CI/CD Workflow)

1. **TEST_SA_PASSWORD**
   - **Purpose:** SQL Server SA password for CI/CD test database
   - **Used in:** GitHub Actions workflow for automated tests
   - **Requirement:** Strong password (minimum 20 characters)
   - **Example:** `Test_Str0ng_P@ssw0rd_2024!`

### For Production Deployment (Optional)

2. **PRODUCTION_SA_PASSWORD**
   - **Purpose:** Production database SA password
   - **Used in:** Production deployment workflows
   - **Requirement:** Extremely strong password (minimum 32 characters)

3. **PRODUCTION_REDIS_PASSWORD**
   - **Purpose:** Production Redis password
   - **Used in:** Production deployment workflows
   - **Requirement:** Strong password (minimum 32 characters)

4. **PRODUCTION_SECRET_KEY**
   - **Purpose:** Application secret key for production
   - **Used in:** Production deployment workflows
   - **Requirement:** Cryptographically secure random string (64+ characters)

5. **GRAFANA_ADMIN_PASSWORD**
   - **Purpose:** Grafana admin password for monitoring
   - **Used in:** Production deployment workflows
   - **Requirement:** Strong password (minimum 20 characters)

## Setup Instructions

### Step 1: Access Repository Settings

1. Go to your GitHub repository
2. Click **Settings** tab
3. In the left sidebar, expand **Secrets and variables**
4. Click **Actions**

### Step 2: Add Required Secrets

For each secret listed above:

1. Click **New repository secret**
2. Enter the **Name** (e.g., `TEST_SA_PASSWORD`)
3. Enter the **Value** (generate using instructions below)
4. Click **Add secret**

## Generating Secure Values

### Using OpenSSL (Recommended)

```bash
# For passwords (32 characters)
openssl rand -base64 32

# For secret keys (64 characters)
openssl rand -base64 64

# For SQL Server passwords (with special characters)
openssl rand -base64 32 | tr -d '/' | tr '+' '@'
```

### Using PowerShell (Windows)

```powershell
# For passwords (32 characters)
-join ((48..57) + (65..90) + (97..122) + (33,35,36,37,38,42,43,45,61,63,64,95) | Get-Random -Count 32 | ForEach-Object {[char]$_})

# For secret keys (64 characters)
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
```

### Using Python

```python
import secrets
import string

# For passwords (32 characters)
alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
password = ''.join(secrets.choice(alphabet) for i in range(32))
print(password)

# For secret keys (64 characters)
secret_key = secrets.token_urlsafe(64)
print(secret_key)
```

## Password Requirements

### SQL Server Passwords

SQL Server passwords must meet these requirements:
- Minimum 8 characters (recommend 20+)
- Contains uppercase letters (A-Z)
- Contains lowercase letters (a-z)
- Contains digits (0-9)
- Contains non-alphanumeric characters (!, @, #, $, %, etc.)

**Important:** Avoid these characters in SQL Server passwords: `'`, `"`, `;`, `--`

### Redis Passwords

Redis passwords should:
- Be at least 32 characters
- Use alphanumeric and special characters
- Not contain spaces

### Secret Keys

Application secret keys should:
- Be at least 64 characters
- Use cryptographically secure random generation
- Never be reused across environments

## Verification

After adding secrets, verify they're configured:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. You should see all required secrets listed (values are hidden)
3. Run a test workflow to ensure secrets are accessible

### Test Workflow Verification

```bash
# Trigger the CI/CD workflow
git push origin develop

# Check workflow run in GitHub Actions tab
# Verify no errors related to missing secrets
```

## Security Best Practices

### DO:
- ✅ Use strong, randomly generated passwords
- ✅ Use different passwords for each environment
- ✅ Rotate secrets regularly (every 90 days)
- ✅ Limit repository access to trusted team members
- ✅ Use environment-specific secrets for staging/production

### DON'T:
- ❌ Reuse passwords across environments
- ❌ Share secrets via insecure channels (email, Slack, etc.)
- ❌ Commit secrets to version control
- ❌ Use weak or dictionary-based passwords
- ❌ Share GitHub repository access unnecessarily

## Secret Rotation

### When to Rotate:
- Every 90 days (scheduled rotation)
- When a team member with access leaves
- After a suspected security incident
- When upgrading security policies

### How to Rotate:

1. **Generate new value:**
   ```bash
   openssl rand -base64 32
   ```

2. **Update GitHub Secret:**
   - Go to Settings → Secrets and variables → Actions
   - Click on the secret name
   - Click **Update secret**
   - Enter new value
   - Click **Update secret**

3. **Update production/staging environments:**
   - Update `.env` files in deployed environments
   - Restart affected services

4. **Verify:**
   - Run smoke tests
   - Check application logs
   - Verify CI/CD pipeline

## Troubleshooting

### Secret Not Available in Workflow

**Problem:** Workflow fails with "secret not found" error

**Solution:**
1. Verify secret name matches exactly (case-sensitive)
2. Check secret is added to the correct repository
3. Ensure workflow has permission to access secrets

### SQL Server Authentication Fails

**Problem:** Tests fail with SQL Server authentication error

**Solution:**
1. Verify `TEST_SA_PASSWORD` meets SQL Server requirements
2. Check for special characters that need escaping
3. Test password locally with sqlcmd:
   ```bash
   sqlcmd -S localhost -U sa -P "YourPassword" -Q "SELECT 1"
   ```

### Environment Variables Not Set

**Problem:** Workflow shows "variable is not set" warnings

**Solution:**
1. Verify all required secrets are added
2. Check secret names in workflow file match GitHub Secrets
3. Ensure secrets are referenced with `${{ secrets.SECRET_NAME }}`

## Required Actions After Setup

- [ ] Add `TEST_SA_PASSWORD` secret
- [ ] Verify CI/CD workflow runs successfully
- [ ] Document password rotation schedule
- [ ] Set up calendar reminders for rotation
- [ ] Configure production secrets (if deploying)
- [ ] Test deployment workflow with production secrets
- [ ] Update team documentation with secret locations
- [ ] Review access controls on repository

## Contact

For questions or issues with GitHub Secrets setup:
- Create an issue in the repository
- Contact the DevOps team
- Refer to [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

## Related Documentation

- [SECURITY.md](./SECURITY.md) - General security guidelines
- [installation.md](./installation.md) - Installation guide
- [README.md](./README.md) - Deployment overview
