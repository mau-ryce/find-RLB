#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'findrlb_django.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    django.setup()
    from django.core.management import call_command
    call_command('runserver', '0.0.0.0:8000', '--nothreading', '--noreload')
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
