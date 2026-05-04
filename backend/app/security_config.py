"""Security configuration for brute force protection and authentication"""

# Brute Force Protection Settings
# ==============================

# Maximum number of failed login attempts before account lockout
MAX_LOGIN_ATTEMPTS = 5

# Duration (in minutes) for which an account is locked after exceeding max attempts
LOCKOUT_DURATION_MINUTES = 15

# Duration (in hours) after which failed attempts counter resets if no login attempt is made
ATTEMPT_RESET_HOURS = 1

# Enable/disable brute force protection
ENABLE_BRUTE_FORCE_PROTECTION = True


# Security Headers
# ================

# Add these headers to protect against common web vulnerabilities
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}


def get_max_login_attempts() -> int:
    """Get the maximum number of login attempts allowed"""
    return MAX_LOGIN_ATTEMPTS


def get_lockout_duration_minutes() -> int:
    """Get the account lockout duration in minutes"""
    return LOCKOUT_DURATION_MINUTES
