from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import TemplateDoesNotExist
from django import forms
from google.appengine.ext import db
from db import ddl



def eventAction(request):
    #print request.POST['event_id']
    return render_to_response(r'event\event-admin-cancel.html', {})
    
