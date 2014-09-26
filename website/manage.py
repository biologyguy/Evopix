#!/usr/bin/python3
import os
import sys

try:
    import settings

except ImportError:
    sys.stderr.write("Error: Can't find settings.py in this dir")
    sys.exit(1)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
