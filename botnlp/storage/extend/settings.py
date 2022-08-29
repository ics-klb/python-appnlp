"""
Default ChatNlp settings for abstract.
"""
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

ALLOWED_HOSTS = []

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'PAGE_SIZE': 10
}

# Application definition