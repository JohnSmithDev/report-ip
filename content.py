#!/usr/bin/env python
"""

"""

__author__ = "John Smith, 2012 <code@john-smith.me>"

import logging
import os

from google.appengine.api import users

from django.template.loaders.filesystem import Loader
from django.template.loader import render_to_string

import app_settings

def is_dev_appserver():
    return os.environ.get("SERVER_SOFTWARE", "").startswith("Development")

def is_user_admin():
    try:
        return users.is_current_user_admin()
    except Exception, e:
        # not sure if this exception handler is really needed?
        logging.error("is_user_admin: [%s/%s]" % (type(e), e))
        return False


def dict_for_django_template(rh):
    # CGI arg takes precedence over anything in cookie
    if rh.request.get("OverrideDeviceStyle") and \
            len(rh.request.get("OverrideDeviceStyle"))>0:
        style_override = rh.request.get("OverrideDeviceStyle") == "yes"
    elif rh.request.cookies.get("OverrideDeviceStyle") and \
            len(rh.request.cookies.get("OverrideDeviceStyle"))>0:
        style_override = rh.request.cookies.get("OverrideDeviceStyle") == "yes"
    else:
        style_override = False

    d = {
        "userIsAdmin": is_user_admin(),
        "appName": app_settings.APP_NAME,
        "debuggingEnabled": app_settings.APP_DEBUG,
        "uiDebuggingEnabled": app_settings.UI_DEBUG,
        "overrideDeviceStyles": style_override,
        "canonicalRoot": app_settings.APP_URL,
        "foo":"bar"
        }
    server = os.environ.get('SERVER_SOFTWARE', '')
    if server.startswith("Development"):
        d["canonicalRoot"] = "/"

    if not rh.request.url.startswith(app_settings.APP_URL):
        d["canonicalURL"] = app_settings.APP_URL + rh.request.path + \
            rh.request.query_string
    return d


def output_page(rh, 
                pagename=None,
                template_file=None,
                values=None):
    """
    Respond with rendered page content

    values is a dictionary to pass through to the template,
    it could/should supercede some of the other arguments

    If there are no cookies or similar personalizations,
    the rendered content will be returned, allowing the
    caller to memcache it for later use
    """

    # Ensure that this is set correctly in this thread
    os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

    if not template_file:
        template_file = "index.html"

    t_dict = dict_for_django_template(rh)
    if values:
        t_dict.update(values)

    t_dict["pagename"] = pagename

    personalized = False
    if rh.request.get("OverrideDeviceStyle"):
        personalized = True
        rh.response.headers.add_header(
            "Set-Cookie",
            "OverrideDeviceStyle=%s; path=/;" %
            (str(rh.request.get("OverrideDeviceStyle"))))

    data = render_to_string(template_file, t_dict)
    rh.response.out.write(data)

    if is_user_admin() or personalized or t_dict["overrideDeviceStyles"] or \
            app_settings.APP_DEBUG:
        return None  # This response can't be memcached
    else:
        return data

