#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import datetime
from db import ddl
from django.http import HttpResponse
from google.appengine.ext import db

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

def resetModelCount(request):
    response = HttpResponse(mimetype="text/plain; charset=utf-8")
    models = ddl.__all__
    models.remove('ModelCount')
    while ddl.ModelCount.all().count() > 0:
        for entity in ddl.ModelCount.all():
            entity.delete()
    for model in models:
        count = eval('ddl.' + model + '.all()').count()
        if count > 0:
            def txn():
                shardName = model + '0'
                obj = ddl.ModelCount(key_name=shardName, className=model, count=count)
                obj.put()
            db.run_in_transaction(txn)

    response.write('resetModelCount 成功!!!')
    return response
