from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import TemplateDoesNotExist
#from flowstaging.data.proflist import getProfessionList
from proflist import getProfessionList

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
                {'filename'    : 'twocolumn_base.html', 
                 'name'        : 'Two Column: Base Page', 
                 'description' : 'two column layout template, extends Base Page',
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                {'filename'    : 'volunteer/base.html', 
                 'name'        : 'Profile: Base Page', 
                 'description' : 'extends Two Column Base Page',
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                {'filename'    : 'volunteer/profile_leftcolumn.html', 
                 'name'        : 'Profile: Sidebar', 
                 'description' : 'sidebar content, included by Profile Base Page',
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                {'filename'    : 'volunteer/volunteer_list.html', 
                 'name'        : 'Profile: Volunteer List', 
                 'description' : 'Volunteer List, extends Volunteer Profile Base Page', 
                 'owner'       : 'kudo_chien', 
                 'status'      : 'DONE'},
#                {'filename'    : 'volunteer/profile_content.html', 
#                 'name'        : 'Profile: Sample Content',
#                 'description' : 'sample content, extends Profile Base Page', 
#                 'owner'       : 'tom_chen', 
#                 'status'      : 'DONE'},
                {'filename'    : 'volunteer/profile_home.html', 
                 'name'        : 'Profile: volunteer Homepage',
                 'description' : 'volunteer homepage, extends Profile Base Page', 
                 'owner'       : 'brian_wang',
                 'status'      : 'DONE'},
                {'filename'    : 'volunteer/profile_info.html', 
                 'name'        : 'Profile: volunteer Info',
                 'description' : 'volunteer information, extends Profile Base Page', 
                 'owner'       : 'brian_wang',
                 'status'      : 'DONE'},
                {'filename'    : 'volunteer/volunteer_npo.html', 
                 'name'        : 'Profile: Joined NPOs',
                 'description' : 'volunteer\'s joined npos, extends Profile Base Page', 
                 'owner'       : 'brian_wang',
                 'status'      : 'DONE'},
#                {'filename'    : 'volunteer/profile_friends.html', 
#                 'name'        : 'Profile: Friends',
#                 'description' : 'volunteer\'s friends, extends Profile Base Page', 
#                 'owner'       : 'brian_wang',
#                 'status'      : 'DONE'},
#                {'filename'    : 'volunteer/profile_portofolio.html', 
#                 'name'        : 'Profile: volunteer Portofolio',
#                 'description' : 'volunteer portofolio, extends Profile Base Page', 
#                 'owner'       : 'brian_wang',
#                 'status'      : 'DONE'},
                {'filename'    : 'volunteer/profile_space.html', 
                 'name'        : 'Profile: volunteer Space',
                 'description' : 'volunteer personal space, extends Profile Base Page', 
                 'owner'       : 'brian_wang',
                 'status'      : 'DONE'},
                {'filename'    : 'volunteer/profile_edit.html', 
                 'name'        : 'Profile: Edit volunteer Profile',
                 'description' : 'extends Profile Base Page', 
                 'owner'       : 'brian_wang',
                 'status'      : 'DONE'},
                {'filename'    : 'npo/base.html', 
                 'name'        : 'NPO Profile: Base Page', 
                 'description' : 'extends Two Column Base Page',
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                {'filename'    : 'npo/profile_leftcolumn.html', 
                 'name'        : 'NPO Profile: Sidebar', 
                 'description' : 'sidebar content, included by NPO Profile Base Page',
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
#                {'filename'    : 'npo/profile_content.html', 
#                 'name'        : 'NPO Profile: Sample Content',
#                 'description' : 'sample content, extends NPO Profile Base Page', 
#                 'owner'       : 'tom_chen', 
#                 'status'      : 'DONE'},
                {'filename'    : 'npo/npo_list.html', 
                 'name'        : 'NPO List',
                 'description' : 'NPO List, extends NPO Profile Base Page', 
                 'owner'       : 'brian_wang', 
                 'status'      : 'DONE'},
                {'filename'    : 'npo/npo_home.html', 
                 'name'        : 'NPO Profile: NPO Homepage',
                 'description' : 'NPO Homepage, extends NPO Profile Base Page', 
                 'owner'       : 'brian_wang', 
                 'status'      : 'DONE'},
                {'filename'    : 'npo/npo_info.html', 
                 'name'        : 'NPO Profile: NPO Info',
                 'description' : 'extends NPO Profile Base Page', 
                 'owner'       : 'brian_wang', 
                 'status'      : 'DONE'},
                {'filename'    : 'npo/npo_volunteers.html', 
                 'name'        : 'NPO Profile: Volunteers List',
                 'description' : 'extends NPO Profile Base Page', 
                 'owner'       : 'brian_wang', 
                 'status'      : 'DONE'},
                {'filename'    : 'npo/npo_portofolio.html', 
                 'name'        : 'NPO Profile: NPO Portofolio',
                 'description' : 'extends NPO Profile Base Page', 
                 'owner'       : 'brian_wang', 
                 'status'      : 'DONE'},
                {'filename'    : 'npo/npo_space.html', 
                 'name'        : 'NPO Profile: NPO Space',
                 'description' : 'extends NPO Space Base Page', 
                 'owner'       : 'brian_wang', 
                 'status'      : 'DONE'},
                 {'filename'    : 'npo/add_pictures.html', 
                 'name'        : 'NPO Profile: Add Pictures',
                 'description' : 'extends NPO Space Base Page', 
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                 {'filename'    : 'npo/add_videos.html', 
                 'name'        : 'NPO Profile: Add Videos',
                 'description' : 'extends NPO Space Base Page', 
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                 {'filename'    : 'npo/add_articles.html', 
                 'name'        : 'NPO Profile: Add Articles',
                 'description' : 'extends NPO Space Base Page', 
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                {'filename'    : 'npo/manage_edit_info.html', 
                 'name'        : 'NPO Management: edit info',
                 'description' : 'extends NPO Profile Base Page', 
                 'owner'       : 'feynman_huang', 
                 'status'      : 'DONE'},
                {'filename'    : 'npo/manage_managers.html', 
                 'name'        : 'NPO Management: edit managers',
                 'description' : 'extends NPO Profile Base Page', 
                 'owner'       : 'feynman_huang', 
                 'status'      : 'DONE'},
                {'filename'    : 'npo/manage_news.html', 
                 'name'        : 'NPO Management: edit news',
                 'description' : 'extends NPO Profile Base Page', 
                 'owner'       : 'feynman_huang', 
                 'status'      : 'DONE'},
                {'filename'    : 'registration/base.html', 
                 'name'        : 'Registration: Base Page',
                 'description' : 'extends Base Page', 
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                {'filename'    : 'registration/volunteer_step1.html', 
                 'name'        : 'Registration: volunteer Registration Step 1 Page',
                 'description' : 'extends Registration Base Page', 
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                {'filename'    : 'registration/volunteer_step2.html', 
                 'name'        : 'Registration: volunteer Registration Step 2 Page',
                 'description' : 'extends Registration Base Page', 
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                {'filename'    : 'registration/volunteer_step3.html', 
                 'name'        : 'Registration: volunteer Registration Step 3 Page',
                 'description' : 'extends Registration Base Page', 
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                {'filename'    : 'registration/npo_step1.html', 
                 'name'        : 'Registration: NPO Registration Step 1 Page',
                 'description' : 'extends Registration Base Page', 
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                {'filename'    : 'registration/npo_step2.html', 
                 'name'        : 'Registration: NPO Registration Step 2 Page',
                 'description' : 'extends Registration Base Page', 
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                {'filename'    : 'registration/npo_step3.html', 
                 'name'        : 'Registration: NPO Registration Step 3 Page',
                 'description' : 'extends Registration Base Page', 
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                {'filename'    : 'event/event-list.html', 
                 'name'        : 'event: event List',
                 'description' : 'extends event Base Page', 
                 'owner'       : 'brian_wang', 
                 'status'      : 'DONE'},
                {'filename'    : 'event/event-info.html', 
                 'name'        : 'event: event Info',
                 'description' : 'extends event Base Page', 
                 'owner'       : 'brian_wang', 
                 'status'      : 'DONE'},
                {'filename'    : 'event/event-info-header.html', 
                 'name'        : 'event: event Info Header',
                 'description' : 'included by event Info & Apply page', 
                 'owner'       : 'brian_wang', 
                 'status'      : 'DONE'},
                {'filename'    : 'event/event-info-basic.html', 
                 'name'        : 'event: event Basic Info',
                 'description' : 'included by event Info & Apply page', 
                 'owner'       : 'brian_wang', 
                 'status'      : 'DONE'},
                {'filename'    : 'event/event-apply.html', 
                 'name'        : 'event: event Application',
                 'description' : 'extends event Base Page', 
                 'owner'       : 'brian_wang', 
                 'status'      : 'DONE'},
                {'filename'    : 'event/event-admin-list.html', 
                 'name'        : 'event: Admin event List',
                 'description' : 'extends event Base Page', 
                 'owner'       : 'feynman_huang', 
                 'status'      : 'DONE'},
                {'filename'    : 'event/event-admin-add.html', 
                 'name'        : 'event: Admin Add event',
                 'description' : 'extends event Base Page', 
                 'owner'       : 'feynman_huang', 
                 'status'      : 'DONE'},
                {'filename'    : 'event/event-admin-edit.html', 
                 'name'        : 'event: Admin Edit event',
                 'description' : 'extends event Base Page', 
                 'owner'       : 'feynman_huang', 
                 'status'      : 'DONE'},
                {'filename'    : 'event/event-admin-cancel.html', 
                 'name'        : 'event: Admin Cancel event',
                 'description' : 'extends event Base Page', 
                 'owner'       : 'camgelo', 
                 'status'      : 'DONE'},
                {'filename'    : 'event/event-admin-validate.html', 
                 'name'        : 'event: Admin Validate event Volunteers',
                 'description' : 'extends event Base Page', 
                 'owner'       : 'HTML:tom_chen/SCRIPT:brian_wang', 
                 'status'      : 'DONE'},
                ]

def showartAction(request, filename):
    from django.conf import settings
    old_template = settings.TEMPLATE_DIRS
    settings.TEMPLATE_DIR = (settings.ROOT_PATH + '/showart/templates',)
    if ('' == filename):
        return render_to_response('showart.html', {'showart_pages' : showArtPages})
    else:
        try:
            # process proflist to 5 per row
            proflist = getProfessionList()
            viewproflist = []
            num_profession_per_row = 3
            for i in range(0, len(proflist)):
                if (i % num_profession_per_row == 0):
                    viewproflist.append([])
                viewproflist[i/num_profession_per_row].append(proflist[i])
            
            from django.conf import settings
            settings.TEMPLATE_DIRS = (settings.ROOT_PATH + '/showart/templates',)
            response = render_to_response(filename, {'proflist': viewproflist})
        except TemplateDoesNotExist:
            response = HttpResponse('Page not found or included / extended template not found: '+filename)
        
        settings.TEMPLATE_DIRS = old_template
        return response
