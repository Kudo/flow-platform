#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import datetime
from db import ddl
from google.appengine.api import users
from django.http import HttpResponse

def cleanModel(modelName):
    model = eval('ddl.' + modelName + '.all()')
    while model.count() > 0:
        for entity in model:
            entity.delete()

def cleanAll(request):
    response = HttpResponse(mimetype="text/plain; charset=utf-8")
    models = ddl.__all__
    models.append('Counter')
    for model in models:
        cleanModel(model)

    response.write('cleanAll 成功!!!')
    return response
