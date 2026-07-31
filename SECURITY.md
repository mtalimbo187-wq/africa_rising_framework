# Security Guide

## Credential Protection

### Environment Variables

**NEVER commit API keys to git.**

```bash
# 1. Store keys in .env (git-ignored)
export ANTHROPIC_API_KEY="sk-..."
export ELEVENLABS_API_KEY="..."

# 2. Load at runtime
source .env

# 3. Verify keys aren't in code
grep -r "sk-" --include="*.py" .
```

### Secure Credential Loading

```python
from core.security import CredentialManager

# Load from environment (safe)
key = CredentialManager.load_from_env("ANTHROPIC_API_KEY")

# Never do this (unsafe)
# key = "sk-abc123def456"  # ❌ Don't hardcode!
```

### Credential Masking in Logs

```python
from core.security import CredentialManager

log_text = f"Called API with key: {api_key}"
safe_log = CredentialManager.mask_credentials(log_text)
# Output: Called API with key: ***

# Save to log files only after masking
logger.info(safe_log)
```

## Input Validation

### Script Sanitization

```python
from core.security import InputValidator

# Sanitize user-provided scripts
user_script = request.get("script")
safe_script = InputValidator.sanitize_script(user_script)

# Check for injection attempts
if InputValidator.check_sql_injection(user_script):
    raise ValueError("Suspicious input detected")

if InputValidator.check_shell_injection(user_script):
    raise ValueError("Shell metacharacters not allowed")
```

### Filename Sanitization

```python
from core.security import InputValidator

# Prevent directory traversal
user_filename = "../../etc/passwd"
safe_filename = InputValidator.sanitize_filename(user_filename)
# Result: "etcpasswd"

# Verify safe file paths
if not InputValidator.validate_file_path(file_path, base_dir="output"):
    raise ValueError("Access denied")
```

### URL Validation

```python
from core.security import InputValidator

# Validate URLs against whitelist
allowed = ["pexels.com", "archive.org", "unsplash.com"]
url = "https://pexels.com/video/123"

if InputValidator.validate_url(url, allowed):
    download_video(url)
else:
    raise ValueError("Domain not allowed")
```

## Configuration Security

### Validate Configuration

```python
from core.security import validate_config
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)

issues = validate_config(config)
if issues:
    for issue in issues:
        print(f"⚠️ {issue}")
```

### Configuration Best Practices

```yaml
# ✓ SAFE: Use environment variables
narration:
  api_key: ${ELEVENLABS_API_KEY}

# ❌ UNSAFE: Hardcoded credentials
narration:
  api_key: "sk_abc123"

# ✓ SAFE: Production-only features
security:
  require_human_review: true
  max_file_size_mb: 500

# ✓ SAFE: Whitelisted domains
asset_sources:
  allowed_domains:
    - "pexels.com"
    - "archive.org"
    - "nasa.gov"
```

## Content Review Workflow

### Require Human Review

```python
from core.security import ContentReviewer

video_metadata = {
    "narration": "Music industry experts say...",
    "visuals": [...]
}

if ContentReviewer.require_review(video_metadata):
    # Flag for human review before publishing
    print("⚠️ Content requires human review")
    
    issues = ContentReviewer.flag_potential_issues(video_metadata)
    for issue in issues:
        print(f"  - {issue['type']}: {issue['recommendation']}")
```

### Review Checklist

Before publishing any video:

- [ ] All claims are fact-checked and verified
- [ ] Unattributed claims are marked or removed
- [ ] Music/audio licensed properly
- [ ] Images/video properly attributed
- [ ] No explicit or graphic content
- [ ] Quality Review Agent score ≥90
- [ ] Human viewer watched complete video
- [ ] Credits include all sources
- [ ] Captions are accurate and synced

## Audit Logging

### Track Security Events

```python
from core.security import AuditLog

audit = AuditLog("audit.log")

# Log API access
audit.log_access(
    action="downloaded_asset",
    resource="pexels.com/video/123",
    user="research_agent"
)

# Log credential access
audit.log_credential_access("ANTHROPIC_API_KEY", status="loaded")

# Log validation failures
audit.log_validation_failure("shell_injection", "user_input_sample")
```

### Review Audit Log

```bash
# View all credential access
jq 'select(.event=="credential_access")' audit.log

# View validation failures
jq 'select(.event=="validation_failure")' audit.log

# Count events by type
jq '.event' audit.log | sort | uniq -c
```

## Access Control

### File Permissions

```bash
# Protect sensitive files
chmod 600 .env                    # Read/write by owner only
chmod 600 config.yaml             # No world read
chmod 755 output/                 # World can read but not modify

# Verify permissions
ls -la .env config.yaml
```

### API Key Rotation

```bash
# 1. Update environment variable
export ANTHROPIC_API_KEY="new_key_here"

# 2. Test new key
python3 -c "from core.security import CredentialManager; print(CredentialManager.load_from_env('ANTHROPIC_API_KEY'))"

# 3. Update .env file
echo "export ANTHROPIC_API_KEY='new_key_here'" >> .env

# 4. Verify old key is removed
grep -r "old_key" .
```

## Network Security

### HTTPS Only

```python
from core.security import InputValidator

# Validate HTTPS URLs
urls = [
    "https://pexels.com/video/123",  # ✓ OK
    "http://pexels.com/video/123",   # ❌ Not HTTPS
]

for url in urls:
    if InputValidator.validate_url(url):
        print(f"✓ {url}")
    else:
        print(f"❌ {url}")
```

### Disable Insecure Protocols

```yaml
# In config.yaml
api_calls:
  require_https: true
  verify_ssl: true
  minimum_tls_version: 1.2
```

## Deployment Security

### Docker Security

```dockerfile
# Dockerfile - secure practices
FROM python:3.9-slim

# Don't run as root
RUN useradd -m -u 1000 appuser
USER appuser

# Read-only root filesystem
RUN chmod 555 /

# No secrets in image
# - Build arguments, not ENV
# - Use .dockerignore for .env
```

### Kubernetes Security (if deployed)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-keys
type: Opaque
stringData:
  anthropic-key: ${ANTHROPIC_API_KEY}
  elevenlabs-key: ${ELEVENLABS_API_KEY}
---
apiVersion: v1
kind: Pod
metadata:
  name: pipeline
spec:
  containers:
  - name: app
    image: africa-rising:latest
    env:
    - name: ANTHROPIC_API_KEY
      valueFrom:
        secretKeyRef:
          name: api-keys
          key: anthropic-key
```

## Incident Response

### If API Key is Leaked

1. **IMMEDIATE:** Revoke key
   ```bash
   # In Anthropic dashboard: revoke key
   # In ElevenLabs dashboard: revoke key
   ```

2. **UPDATE:** Generate new key
   ```bash
   # Create new key in respective dashboard
   export NEW_KEY="sk_..."
   ```

3. **REPLACE:** Update environment
   ```bash
   sed -i "s/old_key/new_key/g" .env
   ```

4. **VERIFY:** Confirm old key no longer works
   ```bash
   grep -r "old_key" . --include="*.py"
   ```

5. **AUDIT:** Check access logs
   ```bash
   jq '.timestamp' audit.log | tail -20
   ```

### If Unauthorized Access Suspected

1. Check audit logs for suspicious activity
2. Review API call logs for unexpected usage
3. Check file access logs
4. Rotate all API keys
5. Review git history for exposed credentials
6. Enable 2FA on all accounts

## Compliance

### GDPR Compliance

- ✓ Don't store personal data without consent
- ✓ Log all data access for audit trails
- ✓ Implement right to be forgotten (delete old logs)

### SOC 2 Compliance

- ✓ Audit logging for all operations
- ✓ Encryption of credentials
- ✓ Access control and authentication
- ✓ Incident response procedures

## Security Checklist

Before production deployment:

- [ ] All API keys stored in environment variables only
- [ ] .env file is git-ignored
- [ ] Input validation enabled for all user inputs
- [ ] Credentials masked in logs
- [ ] HTTPS enforced for all external APIs
- [ ] File permissions set correctly (600 for secrets)
- [ ] Audit logging enabled and working
- [ ] Content review workflow enforced
- [ ] Error messages don't leak sensitive info
- [ ] Regular security updates for dependencies
- [ ] Incident response plan documented
- [ ] Key rotation schedule established

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [API Key Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
