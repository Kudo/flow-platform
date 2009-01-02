from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import TemplateDoesNotExist

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
                {'filename'    : 'user/base.html', 
                 'name'        : 'Profile: Base Page', 
                 'description' : 'extends Two Column Base Page',
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                {'filename'    : 'user/profile_leftcolumn.html', 
                 'name'        : 'Profile: Sidebar', 
                 'description' : 'sidebar content, included by Profile Base Page',
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
#                {'filename'    : 'user/profile_content.html', 
#                 'name'        : 'Profile: Sample Content',
#                 'description' : 'sample content, extends Profile Base Page', 
#                 'owner'       : 'tom_chen', 
#                 'status'      : 'DONE'},
                {'filename'    : 'user/profile_home.html', 
                 'name'        : 'Profile: User Homepage',
                 'description' : 'user homepage, extends Profile Base Page', 
                 'owner'       : 'brian_wang',
                 'status'      : 'DONE'},
                {'filename'    : 'user/profile_info.html', 
                 'name'        : 'Profile: User Info',
                 'description' : 'user information, extends Profile Base Page', 
                 'owner'       : 'brian_wang',
                 'status'      : 'DONE'},
                {'filename'    : 'user/user_npo.html', 
                 'name'        : 'Profile: Joined NPOs',
                 'description' : 'user\'s joined npos, extends Profile Base Page', 
                 'owner'       : 'brian_wang',
                 'status'      : 'DONE'},
                {'filename'    : 'user/profile_friends.html', 
                 'name'        : 'Profile: Friends',
                 'description' : 'user\'s friends, extends Profile Base Page', 
                 'owner'       : 'brian_wang',
                 'status'      : 'DONE'},
                {'filename'    : 'user/profile_portofolio.html', 
                 'name'        : 'Profile: User Portofolio',
                 'description' : 'user portofolio, extends Profile Base Page', 
                 'owner'       : 'brian_wang',
                 'status'      : 'DONE'},
                {'filename'    : 'user/profile_space.html', 
                 'name'        : 'Profile: User Space',
                 'description' : 'user personal space, extends Profile Base Page', 
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
                {'filename'    : 'registration/user_step1.html', 
                 'name'        : 'Registration: User Registration Step 1 Page',
                 'description' : 'extends Registration Base Page', 
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                {'filename'    : 'registration/user_step2.html', 
                 'name'        : 'Registration: User Registration Step 2 Page',
                 'description' : 'extends Registration Base Page', 
                 'owner'       : 'tom_chen', 
                 'status'      : 'DONE'},
                {'filename'    : 'registration/user_step3.html', 
                 'name'        : 'Registration: User Registration Step 3 Page',
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
                {'filename'    : 'activity/activity-list.html', 
                 'name'        : 'Activity: Activity List',
                 'description' : 'extends Activity Base Page', 
                 'owner'       : 'brian_wang', 
                 'status'      : 'DONE'},
                {'filename'    : 'activity/activity-info.html', 
                 'name'        : 'Activity: Activity Info',
                 'description' : 'extends Activity Base Page', 
                 'owner'       : 'brian_wang', 
                 'status'      : 'DONE'},
                {'filename'    : 'activity/activity-info-header.html', 
                 'name'        : 'Activity: Activity Info Header',
                 'description' : 'included by Activity Info & Apply page', 
                 'owner'       : 'brian_wang', 
                 'status'      : 'DONE'},
                {'filename'    : 'activity/activity-info-basic.html', 
                 'name'        : 'Activity: Activity Basic Info',
                 'description' : 'included by Activity Info & Apply page', 
                 'owner'       : 'brian_wang', 
                 'status'      : 'DONE'},
                {'filename'    : 'activity/activity-apply.html', 
                 'name'        : 'Activity: Activity Application',
                 'description' : 'extends Activity Base Page', 
                 'owner'       : 'brian_wang', 
                 'status'      : 'DONE'},
                {'filename'    : 'activity/activity-admin-list.html', 
                 'name'        : 'Activity: Admin Activity List',
                 'description' : 'extends Activity Base Page', 
                 'owner'       : 'feynman_huang', 
                 'status'      : 'DONE'},
                {'filename'    : 'activity/activity-admin-add.html', 
                 'name'        : 'Activity: Admin Add Activity',
                 'description' : 'extends Activity Base Page', 
                 'owner'       : 'feynman_huang', 
                 'status'      : 'DONE'},
                {'filename'    : 'activity/activity-admin-edit.html', 
                 'name'        : 'Activity: Admin Edit Activity',
                 'description' : 'extends Activity Base Page', 
                 'owner'       : 'feynman_huang', 
                 'status'      : 'DONE'},
                {'filename'    : 'activity/activity-admin-cancel.html', 
                 'name'        : 'Activity: Admin Cancel Activity',
                 'description' : 'extends Activity Base Page', 
                 'owner'       : 'camgelo', 
                 'status'      : 'DONE'},
                {'filename'    : 'activity/activity-admin-validate.html', 
                 'name'        : 'Activity: Admin Validate Activity Volunteers',
                 'description' : 'extends Activity Base Page', 
                 'owner'       : 'HTML:tom_chen/SCRIPT:brian_wang', 
                 'status'      : 'DONE'},
                ]

def showartAction(request, filename):
    if ('' == filename):
        return render_to_response('showart.html', {'showart_pages' : showArtPages})
    else:
        try:
            response = render_to_response(filename, {})
        except TemplateDoesNotExist:
            response = HttpResponse('Page not found or included / extended template not found: '+filename)
        return response
