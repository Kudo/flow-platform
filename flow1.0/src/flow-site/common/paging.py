#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import cgi
import datetime
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from google.appengine.ext import db
from google.appengine.api import users
import flowBase
from db.ddl import VolunteerProfile, VolunteerIm, NpoProfile

displayCount = 10
displayNpoCount = 3
displayPageCount = 5
displayExpertiseCount = 5

def get(requestGET, count, displayCount=10, displayPageCount=5):
    startIndex = 0
    if 'start' in requestGET:
        startIndex = int(requestGET['start'])
        if startIndex < 0 or startIndex >= count:
            startIndex = 0
    endIndex = startIndex + displayCount - 1
    if endIndex >= count:
        endIndex = count - 1

    currentPage = startIndex / displayCount + 1
    totalPage = (count - 1) / displayCount + 1

    # Calculate the page list window
    if totalPage < 1:
        totalPage = 1
    fromPage = currentPage -  (displayPageCount / 2)
    if fromPage < 1:
        fromPage = 1
    endPage = fromPage + displayPageCount
    while endPage > totalPage + 1:
        fromPage -= 1
        endPage -= 1
    if fromPage < 1:
        fromPage = 1
    pageList = [{'index': i, 'startIndex': (i - 1) * displayCount} for i in range(fromPage, endPage)]
    del fromPage, endPage

    entryOffset = startIndex
    if count <= 0:
        startIndex = -1

    return {
        'count':                    count,
        'entryOffset':              entryOffset,
        'startIndex':               startIndex,
        'nextIndex':                startIndex + displayCount if currentPage < totalPage else None,
        'prevIndex':                startIndex - displayCount if currentPage > 1 else None,
        'endIndex':                 endIndex,
        'pageList':                 pageList,
        'currentPage':              currentPage,
    }
