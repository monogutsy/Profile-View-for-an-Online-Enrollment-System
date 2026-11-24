"""Settings for the PythonAnywhere web app and deployment commands."""
import json
import os

from django.core.exceptions import ImproperlyConfigured

from .settings import *

# Use the same private configuration in both Bash commands and WSGI workers.
config_path = BASE_DIR / "pythonanywhere_config.json"
config = json.loads(config_path.read_text()) if config_path.exists() else {}

DEBUG = False
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", config.get("secret_key", ""))
hostname = os.environ.get("DJANGO_HOSTNAME", config.get("hostname", ""))
if len(SECRET_KEY) < 50 or not hostname or any(char in hostname for char in "/: *"):
    raise ImproperlyConfigured(
        "Set a secret_key of at least 50 characters and your exact hostname in "
        "pythonanywhere_config.json. See DEPLOYMENT.md."
    )

ALLOWED_HOSTS = [hostname]
CSRF_TRUSTED_ORIGINS = [f"https://{hostname}"]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
# PythonAnywhere terminates HTTPS before forwarding requests to Django.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# Keep HSTS off during initial setup; enable after verifying the live HTTPS site.
SECURE_HSTS_SECONDS = 0
