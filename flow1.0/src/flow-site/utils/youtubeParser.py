#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from django.utils import simplejson
from django.http import HttpResponse
import atom.url
import gdata.alt.appengine
import gdata.youtube, gdata.youtube.service

def get(request):
    youtubeUri = request.POST.get('uri', None)
    if not youtubeUri:
        return HttpResponse(simplejson.dumps({'statusCode': 404, 'reason': 'Unknown action'}), mimetype='application/json')
    matchObj = re.match(r'http://\w+\.youtube\.com(\.tw)?/.*[&?]v=(.+?)(&.*)*$', youtubeUri)
    if not matchObj:
        return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': 'Fail to parse uri'}), mimetype='application/json')
    vid = matchObj.group(2)
    service = gdata.youtube.service.YouTubeService()
    gdata.alt.appengine.run_on_appengine(service)
    try:
        video = service.GetYouTubeVideoEntry(video_id=vid)
    except:
        return HttpResponse(simplejson.dumps({'statusCode': 500, 'reason': 'Fail to parse uri'}), mimetype='application/json')

    return HttpResponse(simplejson.dumps({'statusCode': 200, 'reason': 'success', 'title': video.title.text.decode('UTF-8'), 'uri': video.media.content[0].url}), mimetype='application/json')
