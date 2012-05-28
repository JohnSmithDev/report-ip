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
        "country": req.headers.get("X-AppEngine-Country"),
        "region": req.headers.get("X-AppEngine-Region"),
        "city": req.headers.get("X-AppEngine-City"),
        "latlong": req.headers.get("X-AppEngine-CityLatLong")
        }


class ShowIP(LoggingHandler):
    def get(self):
        dict_for_template = {
                "ip_addr": self.request.remote_addr,
                "headers": self.request.headers
                }
        logging.error("Country is %s" % 
                      self.request.headers.get("X-AppEngine-Country"))
        dict_for_template.update(parse_location_headers(self.request))
        content.output_page(self,
                            template_file="index.html",
                            values=dict_for_template)

app = webapp2.WSGIApplication(
    [
        (".*", ShowIP)
        ],
    debug = app_settings.APP_DEBUG)
