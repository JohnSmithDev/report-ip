# Report IP #

## Overview ##

The gazillionth site that allows people to check their IP address.  To
add a little bit more beyond the usual, it also does a location lookup
based on the IP address, and also dumps out the HTTP headers.

This is a Python App Engine app, with no dependencies on external libraries
other than those provided by the App Engine SDK.

A live instance of the app has been deployed to [http://report-ip.appspot.com](http://report-ip.appspot.com),
but as this is an unbilled app that will easily hit the free quota limits,
please don't abuse it.

There's a blog post with more info at
[http://www.john-smith.me/reinvented-the-wheel-and-built-my-own-ip-address-checker](http://www.john-smith.me/reinvented-the-wheel-and-built-my-own-ip-address-checker)

## TODO ##

* Properly test the non-HTML output
* Generate the non-HTML output using proper libraries rather than Django
  templates - this will help avoid dumb errors with quoting, escaping etc.
* Have a bit more blurb about what this is.
* Tart up the front end with some CSS.
* Save the received info in the datastore
* Based on the saved info, improve the slightly crap geodata the Google
  APIs provide e.g. convert "eng" to "England", "london" to "London" etc
* Register a domain and adjust the branding accordingly
* Put a timestamp in the content, and set response headers to avoid any
  risk/confusion of cached output causing confusion
* Properly parse the Accept: header - currently it just finds the first
  match, which seems to do the right thing in practice, but I assume I should
  also parse the q=0.x weightings?  (Will need to read/understand the HTTP
  spec first.)