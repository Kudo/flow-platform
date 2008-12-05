from django.http import HttpResponse
from django.shortcuts import render_to_response

showArtPages = [ 
                {'filename'    : 'register.html', 
                 'name'        : 'Register', 
                 'description' : 'Register page',
                 'owner'       : 'brian_wang', 
                 'status'      : 'TODO'},
                {'filename'    : 'profile.html', 
                 'name'        : 'Profile',
                 'description' : 'Profile page', 
                 'owner'       : 'tom_chen', 
                 'status'      : 'TODO'},
                ]

def showartAction(request, filename):
    if ('' == filename):
        return render_to_response('showart.html', {'showart_pages' : showArtPages})
    else:
        try:
            response = render_to_response(filename, {})
        except:
            response = HttpResponse('Page not found: '+filename)
        return response
