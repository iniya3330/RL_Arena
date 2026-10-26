"""Account rules, free of Django imports so they can be tested on their own.

- Only an email that contains the word "admin" can hold an admin (caregiver) account.
- Every other email is a player account.
- Accuracy bands mark players in the admin panel.
"""
ADMIN_KEYWORD = "admin"
MIN_PASSWORD_LENGTH = 8


def is_admin_email(email):
    return ADMIN_KEYWORD in (email or "").strip().lower()


def role_for_email(email):
    return "admin" if is_admin_email(email) else "player"


def home_for(is_staff):
    return "admin_panel" if is_staff else "dashboard"


def accuracy_band(accuracy):
    if accuracy is None:
        return "none"
    if accuracy >= 80:
        return "high"
    if accuracy >= 60:
        return "mid"
    return "low"


def validate_signup(name, email, password, confirm, email_exists):
    """Returns a list of error messages (empty when the signup is valid)."""
    errors = []
    if not name.strip():
        errors.append("Please enter your name.")
    if not email or "@" not in email or "." not in email.split("@")[-1]:
        errors.append("Please enter a valid email address.")
    elif len(email) > 150:
        errors.append("That email address is too long.")
    elif email_exists:
        errors.append("An account with this email already exists. Sign in instead.")
    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append(f"Password needs at least {MIN_PASSWORD_LENGTH} characters.")
    if password != confirm:
        errors.append("The two passwords do not match.")
    return errors


def login_problem(email, is_staff, is_active):
    """Returns an error message when this email and account cannot sign in, else None."""
    if not is_active:
        return "This account is disabled. Ask an administrator for help."
    if is_admin_email(email) and not is_staff:
        return "This email is not an admin account."
    if is_staff and not is_admin_email(email):
        return "Admin accounts need the word 'admin' in the email address."
    return None
