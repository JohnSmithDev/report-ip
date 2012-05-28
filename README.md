# Report IP #

## Overview ##

The gazillionth site that allows people to check their IP address.  To
add a little bit more beyond the usual, it also does a location lookup
based on the IP address, and also dumps out the HTTP headers.

This is a Python App Engine app, with no dependencies on external libraries
other than those provided by the App Engine SDK.

## TODO ##

* Support report formats besides HTML; a client should be able to specify
  this either through a format=whatever CGI parameter, or a more RESTful
  way using the Accept: HTTP header.
* Have a bit more blurb about what this is.
* Tart up the front end with some CSS.
* Save the received info in the datastore
* Based on the saved info, improve the slightly crap geodata the Google
  APIs provide e.g. convert "eng" to "England", "london" to "London" etc
* Hide the pseudo-headers that GAE added on (the X-Appengine-* ones)
* Register a domain and adjust the branding accordingly

