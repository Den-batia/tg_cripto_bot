#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_api.settings')

    from django.conf import settings

    running_tests = 'test' in sys.argv

    if running_tests:
        from coverage import Coverage
        cov = Coverage()
        cov.erase()
        cov.start()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    if running_tests:
        import logging
        logging.disable(logging.CRITICAL)
        settings.DEBUG = False
        settings.TEMPLATE_DEBUG = False
        settings.PASSWORD_HASHERS = [
            'django.contrib.auth.hashers.MD5PasswordHasher',
        ]
        settings.DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'test_database',
            }
        }
        settings.MIDDLEWARE_CLASSES = [
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ]

    execute_from_command_line(sys.argv)

    if running_tests:
        cov.stop()
        cov.save()
        covered = cov.report()
        if covered < 90:
            sys.exit(1)


if __name__ == '__main__':
    main()
