"""
Settings to keep Django happy.  The settings for the app code
are in app_settings.py
"""

__author__ = "John Smith, 2012 <code@john-smith.me>"

import os

PROJECT_ROOT = os.path.dirname(__file__)

TEMPLATE_DIRS = (os.path.join(PROJECT_ROOT, "templates"),)

INSTALLED_APPS = ('customtags')
