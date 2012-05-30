#!/usr/bin/env python
"""
Main request handlers for Python Package project

Written by John Smith 2010-2012 | http://www.john-smith.me
Licenced under GPL v2           | http://www.gnu.org/licenses/gpl-2.0.html
"""

__author__ = "John Smith, 2012 <code@john-smith.me>"

import logging

import webapp2

from handler import LoggingHandler
import content

import app_settings

def sanitised_location_value(req, key):
    """
    The appspot.com geolocation API returns "?" for country/region/city and
    0.00...,0.00000" for LatLong if they are unknown for the given IP,
    I prefer to use None for unknown values (which is what dev_appserver
    provides for these headers).
    """
    val = req.headers.get("X-AppEngine-" + key)
    if val is None:
        return val
    if key.lower() in ["country", "region", "city"] and val == "?":
        val = None
    elif key.lower() in ["citylatlong"]:
        latitude, longitude = val.split(",")
        if float(latitude) == 0.0 and float(longitude) == 0.0:
            val = None
    return val

def parse_location_headers(req):
    """
    Return a dict containing county, region, city, latlong values,
    based on the X-AppEngine-* fields in the request headers.
    Any values which are undefined in the headers will have an entry
    in the dictionary, with the value being None
    See http://www.rominirani.com/2012/04/25/appengine-location-detection-update-x-appengine-country-and-more/
    for more info
    """

    return {
        "country": sanitised_location_value(req, "Country"),
        "region": sanitised_location_value(req, "Region"),
        "city": sanitised_location_value(req, "City"),
        "latlong": sanitised_location_value(req, "CityLatLong")
        }

def sort_and_filter_headers(req):
    """
    Return a sorted list of 2-element tuples for the HTTP header values,
    filtering out the ones that GAE adds on (as these could confuse
    end-users when we display the headers back to them
    """
    ret_list = []
    for k in sorted(req.headers.keys()):
        if not k.lower().startswith("x-appengine"):
            ret_list.append((k, req.headers.get(k)))
    return ret_list

# Formats are defined in both "simple" and MIME-type forms, the former
# are to make it easier for people using a format=xxx CGI arg.
# The value is a 2-element tuple comprising template filename suffix and
# MIME-type
SUPPORTED_FORMATS = {"html": ("html", "text/html"),
                     "text/html": ("html", "text/html"),

                     "csv": ("csv", "text/csv"),
                     "text/csv": ("csv", "text/csv"),

                     "text": ("txt", "text/plain"),
                     "txt": ("txt", "text/plain"),
                     "plaintext": ("txt", "text/plain"),
                     "text/plain": ("txt", "text/plain"),

                     "xml": ("xml", "application/xml"),
                     "application/xml": ("xml", "application/xml"),
                     "text/xml": ("xml", "text/xml"),

                     "json": ("json", "application/json"),
                     "application/json": ("json", "application/json")
                     }

def work_out_format(req):
    """
    Using CGI args or Accept: header, work out what format to return.
    (If both specified, CGI arg takes precedence.)
    Throws ValueError if an unknown format was specified
    """
    if req.get("format"):
        format_ = req.get("format").lower()
        if format_ in SUPPORTED_FORMATS:
            return SUPPORTED_FORMATS[format_]
        else:
            raise ValueError("Unknown format in CGI arg: %s" % (format_))
    elif req.headers.get("Accept"):
        fmt_list = req.headers.get("Accept").lower().split(",")
        for format_ in fmt_list:
            if format_ == "*/*":
                break # use default format
            if format_ in SUPPORTED_FORMATS:
                return SUPPORTED_FORMATS[format_]
        else:
            raise ValueError("Unknown format in Accept header: %s" % (format_))

    # Default
    return SUPPORTED_FORMATS["html"]

class ShowIP(LoggingHandler):
    def get(self):
        try:
            filename_suffix, mime_type = work_out_format(self.request)
        except ValueError, e:
            logging.error("Unable to make sense of format: %s" % (e))
            self.error(406) # Not Acceptable
            return

        dict_for_template = {
                "ip_addr": self.request.remote_addr,
                "headers": sort_and_filter_headers(self.request)
                }
        hdr = sort_and_filter_headers(self.request)

        dict_for_template.update(parse_location_headers(self.request))
        content.output_page(self,
                            template_file="index." + filename_suffix,
                            mime_type=mime_type,
                            values=dict_for_template)

app = webapp2.WSGIApplication(
    [
        (".*", ShowIP)
        ],
    debug = app_settings.APP_DEBUG)
