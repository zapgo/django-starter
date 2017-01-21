from django.utils.encoding import force_text


def user_display(user):
    return force_text(user.email)


LOGIN_REDIRECT_URL = '/dashboard'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/dashboard'
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_DISPLAY = user_display
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_UNIQUE_USERNAME = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = ""
