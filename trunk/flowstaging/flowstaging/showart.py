from django.http import HttpResponse
from django.shortcuts import render_to_response

showArtPages = [ 
                {'filename'    : 'base.html', 
                 'name'        : 'Base Page', 
                 'description' : 'The base of HTML page',
                 'owner'       : 'brian_wang', 
                 'status'      : 'DONE'},
                {'filename'    : 'splashbox.html', 
                 'name'        : 'Splash Box', 
                 'description' : 'included by xxx Base Page',
                 'owner'       : 'brian_wang', 
                 'status'      : 'DONE'},
                {'filename'    : 'splashbox_search.html', 
                 'name'        : 'Splash Box - Search Version', 
                 'description' : 'included by xxx Base Page',
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                {'filename'    : 'register_base.html', 
                 'name'        : 'Register: Base Page', 
                 'description' : 'extends Base Page',
                 'owner'       : 'brian_wang', 
                 'status'      : 'DONE'},
                {'filename'    : 'register_new_account.html', 
                 'name'        : 'Register: New Account', 
                 'description' : 'new account page, extends Register Base Page',
                 'owner'       : 'brian_wang', 
                 'status'      : 'TODO'},
                {'filename'    : 'twocolumn_base.html', 
                 'name'        : 'Two Column: Base Page', 
                 'description' : 'two column layout template, extends Base Page',
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                {'filename'    : 'profile_base.html', 
                 'name'        : 'Profile: Base Page', 
                 'description' : 'extends Two Column Base Page',
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                {'filename'    : 'profile_leftcolumn.html', 
                 'name'        : 'Profile: Sidebar', 
                 'description' : 'sidebar content, included by Profile Base Page',
                 'owner'       : 'tom_chen', 
                 'status'      : 'PARTIAL'},
                {'filename'    : 'profile_content.html', 
                 'name'        : 'Profile: Sample Content',
                 'description' : 'sample content, extends Profile Base Page', 
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                ]

def showartAction(request, filename):
    if ('' == filename):
        return render_to_response('showart.html', {'showart_pages' : showArtPages})
    else:
        #try:
        response = render_to_response(filename, {})
        #except:
        #    response = HttpResponse('Page not found: '+filename)
        return response
