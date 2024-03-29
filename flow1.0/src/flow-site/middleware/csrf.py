"""
Cross Site Request Forgery Middleware.

This module provides a middleware that implements protection
against request forgeries from other sites. 

"""
from django.conf import settings
from django.http import HttpResponseForbidden
import re
import itertools
from google.appengine.api import users, memcache
import flowBase

_ERROR_MSG = '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"><body><h1>403 Forbidden</h1><p>Cross Site Request Forgery detected. Request aborted.</p></body></html>'

_POST_FORM_RE = memcache.get('Misc/FormRE') 
if not _POST_FORM_RE:
    _POST_FORM_RE = re.compile(r'(<form\W[^>]*\bmethod=(\'|"|)POST(\'|"|)\b[^>]*>)', re.IGNORECASE)
    memcache.add('Misc/FormRE', _POST_FORM_RE)
    
_HTML_TYPES = ('text/html', 'application/xhtml+xml')    

class CsrfMemcacheMiddleware(object):
    """Django middleware that adds protection against Cross Site
    Request Forgeries by adding hidden form fields to POST forms and 
    checking requests for the correct value.  
    
    In the list of middlewares, SessionMiddleware is required, and must come 
    after this middleware.  CsrfMiddleWare must come after compression 
    middleware.
   
    If a session ID cookie is present, it is hashed with the SECRET_KEY 
    setting to create an authentication token.  This token is added to all 
    outgoing POST forms and is expected on all incoming POST requests that 
    have a session ID cookie.
    
    If you are setting cookies directly, instead of using Django's session 
    framework, this middleware will not work.
    """
    
    def process_request(self, request):
        if request.POST:
            volunteer = flowBase.getVolunteer(users.get_current_user())
            if not volunteer:
                return None

            csrf_token = flowBase.makeToken(request, volunteer.volunteer_id)
            # check incoming token
            try:
                request_csrf_token = request.POST['xToken']
            except KeyError:
                return HttpResponseForbidden(_ERROR_MSG)
            
            if request_csrf_token != csrf_token:
                return HttpResponseForbidden(_ERROR_MSG)
                
        return None

    def process_response(self, request, response):
        volunteer = flowBase.getVolunteer(users.get_current_user())
        if not volunteer:
            return response
        csrf_token = flowBase.makeToken(request, volunteer.volunteer_id)
            
        if csrf_token is not None and \
                response['Content-Type'].split(';')[0] in _HTML_TYPES:
            
            # ensure we don't add the 'id' attribute twice (HTML validity)
            idattributes = itertools.chain(("id='xToken'",), 
                                            itertools.repeat(''))
            def add_csrf_field(match):
                """Returns the matched <form> tag plus the added <input> element"""
                return match.group() + "<div style='display:none;'>" + \
                "<input type='hidden' " + idattributes.next() + \
                " name='xToken' value='" + csrf_token + \
                "' /></div>"

            # Modify any POST forms
            response.content = _POST_FORM_RE.sub(add_csrf_field, response.content)
        return response
