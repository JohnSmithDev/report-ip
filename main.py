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
import header_parsing

import app_settings








class ShowIP(LoggingHandler):
    def get(self):
        req = header_parsing.ReportIPRequest(self.request)
        try:
            filename_suffix, mime_type = req.work_out_format()
        except ValueError, e:
            logging.error("Unable to make sense of format: %s" % (e))
            self.error(406) # Not Acceptable
            return

        dict_for_template = {
                "ip_addr": self.request.remote_addr,
                "headers": req.sort_and_filter_headers()
                }

        dict_for_template.update(req.parse_location_headers())
        content.output_page(self,
                            template_file="index." + filename_suffix,
                            mime_type=mime_type,
                            values=dict_for_template)

app = webapp2.WSGIApplication(
    [
        (".*", ShowIP)
        ],
    debug = app_settings.APP_DEBUG)
