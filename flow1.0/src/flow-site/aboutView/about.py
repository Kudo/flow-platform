#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response
from django.template import TemplateDoesNotExist
import flowBase

def show(request, filename):
    try:
        response = render_to_response('about/' + filename, {'base': flowBase.getBase(request)})
    except TemplateDoesNotExist:
        response = HttpResponseNotFound()
    return response
