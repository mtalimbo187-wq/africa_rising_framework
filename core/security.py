#!/usr/bin/env python3
"""
Security Module

- Input validation and sanitization
- Credential protection
- File path safety
- Content review workflow
"""

import re
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import hashlib


class InputValidator:
    """Validates and sanitizes all external inputs"""

    # Dangerous characters in file paths
    DANGEROUS_CHARS = r'[<>:"|?*\x00-\x1f]'

    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b)",
        r"(--|;|/*|*/)",
    ]

    # Shell metacharacters
    SHELL_METACHARACTERS = r'[`$()|\';\"&<>\\]'

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Remove dangerous characters from filename"""
        # Remove dangerous characters
        sanitized = re.sub(InputValidator.DANGEROUS_CHARS, "_", filename)
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(". ")
        # Limit length
        return sanitized[:255]

    @staticmethod
    def sanitize_script(text: str) -> str:
        """Remove potentially dangerous content from script"""
        # Remove shell metacharacters (keep narrative text)
        # Only remove if they're isolated, not in normal context
        dangerous_sequences = [
            r"`[^`]*`",  # Backticks for command execution
            r"\$\([^)]*\)",  # $() command substitution
        ]

        sanitized = text
        for pattern in dangerous_sequences:
            sanitized = re.sub(pattern, "[REMOVED_DANGEROUS_SEQUENCE]", sanitized)

        return sanitized

    @staticmethod
    def validate_file_path(file_path: str, base_dir: str = ".") -> bool:
        """Prevent directory traversal attacks"""
        try:
            base = Path(base_dir).resolve()
            target = Path(file_path).resolve()

            # Ensure target is within base directory
            return str(target).startswith(str(base))
        except (ValueError, OSError):
            return False

    @staticmethod
    def validate_url(url: str, allowed_domains: Optional[List[str]] = None) -> bool:
        """Validate URL and check against whitelist"""
        # Basic URL pattern
        url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        if not re.match(url_pattern, url):
            return False

        if allowed_domains:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            return any(domain.endswith(allowed) for allowed in allowed_domains)

        return True

    @staticmethod
    def check_sql_injection(text: str) -> bool:
        """Check for potential SQL injection attempts"""
        for pattern in InputValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def check_shell_injection(text: str) -> bool:
        """Check for shell metacharacters"""
        return bool(re.search(InputValidator.SHELL_METACHARACTERS, text))


class CredentialManager:
    """Secure credential handling"""

    SENSITIVE_KEYS = [
        "api_key",
        "secret",
        "password",
        "token",
        "key",
        "credential"
    ]

    @staticmethod
    def mask_credentials(text: str, pattern: Optional[str] = None) -> str:
        """Mask sensitive data in logs"""
        if pattern is None:
            # Mask common patterns
            patterns = [
                (r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\'\s]+)', "api_key=***"),
                (r'token["\']?\s*[:=]\s*["\']?([^"\'\s]+)', "token=***"),
                (r'password["\']?\s*[:=]\s*["\']?([^"\'\s]+)', "password=***"),
                (r'sk-[a-zA-Z0-9]+', "***"),  # OpenAI keys
                (r'pk-[a-zA-Z0-9]+', "***"),  # Pexels keys
            ]

            masked = text
            for pattern, replacement in patterns:
                masked = re.sub(pattern, replacement, masked, flags=re.IGNORECASE)
            return masked

        return re.sub(pattern, "***", text)

    @staticmethod
    def load_from_env(key_name: str) -> Optional[str]:
        """Safely load credentials from environment"""
        value = os.environ.get(key_name)
        if not value:
            raise KeyError(f"Environment variable not set: {key_name}")
        return value

    @staticmethod
    def hash_value(value: str) -> str:
        """One-way hash for audit logging"""
        return hashlib.sha256(value.encode()).hexdigest()[:16]


class ContentReviewer:
    """Content safety and review workflow"""

    CONTENT_FLAGS = {
        "unattributed_claims": r"(?i)(according to|studies show|experts say)(?!\s+(from|in|at))",
        "copyrighted_concerns": r"(?i)(music|song|artist|album|copyright)",
        "explicit_content": r"(?i)(violent|graphic|explicit|profanity)",
        "false_positive": r"(?i)(allegedly|reportedly|unconfirmed)",
    }

    @staticmethod
    def flag_potential_issues(video_metadata: Dict[str, Any]) -> List[Dict]:
        """Identify content issues requiring human review"""
        issues = []

        narration = video_metadata.get("narration", "")
        for issue_type, pattern in ContentReviewer.CONTENT_FLAGS.items():
            matches = re.findall(pattern, narration)
            if matches:
                issues.append({
                    "type": issue_type,
                    "severity": "warning",
                    "count": len(matches),
                    "recommendation": f"Review content for {issue_type}"
                })

        return issues

    @staticmethod
    def require_review(video_metadata: Dict[str, Any]) -> bool:
        """Determine if human review is required"""
        issues = ContentReviewer.flag_potential_issues(video_metadata)
        return len(issues) > 0


class AuditLog:
    """Security audit trail"""

    def __init__(self, log_file: str = "audit.log"):
        self.log_file = Path(log_file)

    def log_access(self, action: str, resource: str, user: Optional[str] = None, status: str = "success"):
        """Log resource access"""
        entry = {
            "timestamp": self._timestamp(),
            "action": action,
            "resource": resource,
            "user": user or "unknown",
            "status": status
        }
        self._write(entry)

    def log_credential_access(self, credential_type: str, status: str = "accessed"):
        """Log credential access (don't log actual value)"""
        entry = {
            "timestamp": self._timestamp(),
            "event": "credential_access",
            "type": credential_type,
            "status": status,
            "hash": CredentialManager.hash_value(credential_type)
        }
        self._write(entry)

    def log_validation_failure(self, validation_type: str, input_sample: str):
        """Log validation failures"""
        entry = {
            "timestamp": self._timestamp(),
            "event": "validation_failure",
            "type": validation_type,
            "input_hash": CredentialManager.hash_value(input_sample),
            "severity": "warning"
        }
        self._write(entry)

    def _timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()

    def _write(self, entry: Dict):
        """Write audit entry"""
        import json
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")


def validate_config(config: Dict[str, Any]) -> List[str]:
    """Validate configuration for security issues"""
    issues = []

    # Check for hardcoded credentials
    for key, value in config.items():
        if isinstance(value, str):
            if InputValidator.check_sql_injection(str(value)):
                issues.append(f"Potential SQL injection in config.{key}")
            if "api_key" in key.lower() and len(value) > 10 and value != "YOUR_KEY":
                if not value.startswith("sk-") and not value.startswith("pk-"):
                    issues.append(f"Suspicious value in config.{key} - verify it's not a real key")

    # Check for directory traversal paths
    for key, value in config.items():
        if isinstance(value, str) and ("/" in value or "\\" in value):
            if not InputValidator.validate_file_path(value):
                issues.append(f"Potential directory traversal in config.{key}")

    return issues
