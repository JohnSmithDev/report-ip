#!/usr/bin/env python
"""
Functions to take a webapp/webob Request object and pull out
the bits pertinent to this project, which are mainly HTTP header
related.
"""

__author__ = "John Smith, 2012 <code@john-smith.me>"

import re

# Formats are defined in both "simple" and MIME-type forms, the former
# are to make it easier for people using a format=xxx CGI arg.
# The value is a 2-element tuple comprising template filename suffix and
# MIME-type
SUPPORTED_FORMATS = {"html": ("html", "text/html"),
                     "text/html": ("html", "text/html"),
                     "application/xhtml+xml": ("html", "text/html"),
                     "*/*": ("html", "text/html"),

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

class ReportIPRequest(object):
    def __init__(self, req):
        self.req = req
        self.headers = req.headers # more convenient than self.req.headers

    def sanitised_location_value(self, key):
        """
        The appspot.com geolocation API returns "?" for country/region/city and
        0.00...,0.00000" for LatLong if they are unknown for the given IP,
        I prefer to use None for unknown values (which is what dev_appserver
        provides for these headers).
        """
        val = self.headers.get("X-AppEngine-" + key)
        if val is None:
            return val
        if key.lower() in ["country", "region", "city"] and val == "?":
            val = None
        elif key.lower() in ["citylatlong"]:
            latitude, longitude = val.split(",")
            if float(latitude) == 0.0 and float(longitude) == 0.0:
                val = None
        return val


    def parse_location_headers(self):
        """
        Return a dict containing county, region, city, latlong values,
        based on the X-AppEngine-* fields in the request headers.
        Any values which are undefined in the headers will have an entry
        in the dictionary, with the value being None
        See http://www.rominirani.com/2012/04/25/appengine-location-detection-update-x-appengine-country-and-more/
        for more info
        """

        return {
            "country": self.sanitised_location_value("Country"),
            "region": self.sanitised_location_value("Region"),
            "city": self.sanitised_location_value("City"),
            "latlong": self.sanitised_location_value("CityLatLong")
            }

    def sort_and_filter_headers(self):
        """
        Return a sorted list of 2-element tuples for the HTTP header values,
        filtering out the ones that GAE adds on (as these could confuse
        end-users when we display the headers back to them
        """
        ret_list = []
        for k in sorted(self.headers.keys()):
            if not k.lower().startswith("x-appengine"):
                ret_list.append((k, self.headers.get(k)))
        return ret_list


    def get_format_from_accept_header(self):
        """
        Parsing of the format if it was supplied via the Accept: HTTP header
        Returns tuple of (filename_suffix, mime_type) or throws ValueError
        if no known format found
        Documentation for how to parse this header is at
        http://www.gethifi.com/blog/browser-rest-http-accept-headers
        """
        best_format = None
        best_score = 0.0

        fmt_list = self.headers.get("Accept").lower().split(",")
        for format_ in fmt_list:
            if format_.find(";") >= 0:
                format_, score = format_.split(";", 1)
                score = float(re.sub("[^\d\.]", "", score)) # regex to kill "q="
            else:
                score = 1.0
            if format_ in SUPPORTED_FORMATS or format:
                if score == 1.0:
                    # Let's not waste time
                    return SUPPORTED_FORMATS[format_]
                elif score > best_score:
                    best_format = format_
                    best_score = score
        if best_score > 0.0:
            return SUPPORTED_FORMATS[best_format]
        else:
            raise ValueError("Unknown format in Accept header: %s" %
                             (format_))
    def work_out_format(self):
        """
        Using CGI args or Accept: header, work out what format to return.
        (If both specified, CGI arg takes precedence.)
        Returns tuple of (filename_suffix, mime_type) or throws ValueError
        if no known format found.
        """
        if self.req.get("format"):
            format_ = self.req.get("format").lower()
            if format_ in SUPPORTED_FORMATS:
                return SUPPORTED_FORMATS[format_]
            else:
                raise ValueError("Unknown format in CGI arg: %s" % (format_))
        elif self.headers.get("Accept"):
            return self.get_format_from_accept_header()

        # Default
        return SUPPORTED_FORMATS["html"]
