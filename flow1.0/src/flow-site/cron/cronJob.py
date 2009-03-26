import logging
from django.http import HttpResponse

def every5minutes(request):
    logging.info('every5minutes cron test')
    return HttpResponse('ok')

def hourly(request):
    logging.info('hourly cron test')
    return HttpResponse('ok')