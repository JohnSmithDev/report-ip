"""
Enhanced webapp.RequestHandler class(es)/decorator

Two advantages over webapp.RequestHandler
- Explcitly log (debug level) how long the request took.
  This is in the existing GAE logging, but this is more
  explicit/readable IMHO.
- Content for a URL can be memcached to (hopefully) speed
  up responses.  Obviously you'd have to be careful on something
  that uses cookies.  (I believe webapp2 might offer something similar,
  based on some code I briefly saw, but I haven't investigated properly.)

Now adapted to enhance webapp2.RequestHandler:
- Always sets DJANGO_SETTINGS_MODULE
- Always sets logging level

It's possible that this is an unnecessary optimization in many
cases, but it's easy enough to swap in/out.

An alternative take on this sort of problem can be found at
http://appengine-cookbook.appspot.com/recipe/webapp-page-caching-handler/
I've not tried it personally (I wasn't aware of its existence
until this was mostly finished.

Written by John Smith 2010-2012     | http://www.john-smith.me
Copyright Menboku Ltd 2010-2012     | 
Licenced under GPL v2               | http://www.gnu.org/licenses/gpl-2.0.html

"""

__author__ = "John Smith - http://www.john-smith.me"

import logging
import time
import datetime
import os

from google.appengine.api import memcache

import webapp2

# Some settings/functions from my blog code, with reasonable
# defaults if they can't be found.
try:
    import app_settings
    _USE_MEMCACHE_ = app_settings.USE_MEMCACHE
except ImportError, e:
    _USE_MEMCACHE_ = True

try:
    from cachability import can_use_cached_copy
except ImportError, e:
    def can_use_cached_copy(*dontcare):
        pass

try:
    from log_queuing import enqueue_log_task
except ImportError, e:
    def enqueue_log_task(*dontcare):
        pass

# How long to keep memcached copy for (in seconds)
_CACHE_LIFE_ = 3600

# If returning a memcached copy, should an external cache also cache it?
_ENABLE_CACHE_CONTROL_ = True


class LoggingHandler(webapp2.RequestHandler):
    """
    More explicit duration logging than webapp.RequestHandler
    New for webapp2: sets the logging level at initialization and
    DJANGO_SETTINGS_MODULE
    """

    def __init__(self, request, response):
        """
        FYI: For reasons I've yet to uncover the logging in this __init__()
        method doesn't appear, on dev_appserver 1.6.1 at least
        """
        # See http://webapp-improved.appspot.com/guide/handlers.html#a-micro-framework-based-on-webapp2
        # and https://groups.google.com/forum/#!msg/webapp2/ldbwy01iwkI/1svOxERRT6kJ
        # - calling the superclasses __init__() method just causes strange errors
        # webapp2.RequestHandler.__init__(self)
        self.initialize(request, response)

        logging.getLogger().setLevel(logging.DEBUG)
        self.init_time = time.time()
        os.environ["DJANGO_SETTINGS_MODULE"] = "settings"


    def __del__(self):
        logging.debug("Handler for %s took %.2f seconds" %
                      (self.request.url, time.time() - self.init_time))


class HeadersAndContent:
    """Memcachable structure for storing/returning responses"""

    def __init__(self, content, headers=None, status_code=200,
                 analytics_tag=None):
        """
        Arguments:
          content: content to cache.  If None, then this object
                   should not be used - if you want to cache an
                   empty response, set it to "" instead

        """
        if headers:
            self.headers  = headers
        else:
            self.headers = {}
        self.content = content
        self.status_code = status_code
        self.creation_date = datetime.datetime.now()
        self.analytics_tag = analytics_tag

    def respond(self, rh):
        for hdr in self.headers:
            rh.response.headers[hdr] = self.headers[hdr]
        rh.response.headers["X-Memcached-From"] = str(self.creation_date)
        if _ENABLE_CACHE_CONTROL_:
            rh.response.headers["Cache-Control"] = \
                "max-age=%d, public" % (_CACHE_LIFE_)
        head = False
        rh.response.out.write(self.content)
        if self.status_code != 200:
            rh.error(self.status_code)
        if self.analytics_tag:
            enqueue_log_task(rh, pagename=self.analytics_tag, 
                             from_memcache=True)
        return len(self.content)

def memcachable(warh_method):
    """Decorator to add memcaching to webapp.RequestHandler methods

    In the decorated methods, you need to return the content, ideally
    as a HeadersAndContent, but a string will do.  Otherwise there
    won't be anything to memcache.

    FYI: The original webapp1 version returned a boolean indicating
    success or failure (although I never found a scenario to return
    the latter) - however this causes webapp2.RequestHandler to blow
    up, so the return statements have been removed

    """
    def innerfunc(self, *args):
        self.responded = False
        data = memcache.get(self.request.url)
        if _USE_MEMCACHE_ and can_use_cached_copy(self) and data:
            data_len = data.respond(self)
            self.responded = True
            logging.debug("Responded with %d bytes of memcached data for %s" %
                          (data_len, self.request.url))
        else:
            method_args = [self]
            method_args.extend(args)
            retval = warh_method(*method_args)
            if can_use_cached_copy(self):
                if _USE_MEMCACHE_ and retval:
                    if isinstance(retval, HeadersAndContent):
                        if retval.content is not None:
                            memcache.set(self.request.url, 
                                         retval,
                                         time=_CACHE_LIFE_)
                        else:
                            logging.debug("Response for '%s' is not cachable" %
                                          (self.request.url))
                    else:
                        # Assume just the content; no headers,
                        # HTTP status, etc
                        memcache.set(self.request.url,
                                     HeadersAndContent(content=retval),
                                     time=_CACHE_LIFE_)
                else:
                    logging.warning("Memcache disabled and/or no value "
                                    "returned from handler for '%s'" % 
                                    (self.request.url))

    return innerfunc


class MemcachablePageHandler(LoggingHandler):
    """
    Much of this class became defunct in favour of @memcachable, but
    it's still worth using if only for the HEAD handler.

    The signatures for .head() and .get() methods have *dontcare just
    in case the 'real' handlers catch part of the URL as args via
    a regexp.  They are irrelevant here as we look at the full URL

    """
    
    def __init__(self, request, response):
        LoggingHandler.__init__(self, request, response)

    def cache_response(self, content, time=_CACHE_LIFE_):
        if content and len(content)>0 and can_use_cached_copy(self):
            logging.debug("Caching %d bytes of content for %s" % 
                          (len(content), self.request.url))
            memcache.set(self.request.url, content, time=time)
        else:
            logging.debug("NOT caching content for %s" %
                          (self.request.url))

    def head(self, *dontcare):
        """Basic handler to minimize spurious errors on dashboard"""
        if _USE_MEMCACHE_:
            data = memcache.get(self.request.url)
            if data:
                data.respond(self)
        # Don't bother serving/generating a "proper" page if
        # we don't have one cached - it's only HEAD after all

    def get(self, *dontcare):
        """
        Respond to request from memcache where available

        The inheriting class should do the following in
        its get() method:
        1. After calling this, check self.responded and
           return if it is True
        2. Call cache_response() with the rendered content.
           (NB the content would still have to be returned
           to the client)
        If you use the @memcachable decorator you get this (and
        more for free), you just need to return the content -
        ideally as a HeadersAndContent, but a string will
        be accepted.

        """
        self.responded = False
        if not can_use_cached_copy(self):
            return
        if _USE_MEMCACHE_:
            data = memcache.get(self.request.url)
            if data:
                data.respond(self)
                self.responded = True
                logging.debug("Responded with memcached page for %s" %
                              (self.request.url))
