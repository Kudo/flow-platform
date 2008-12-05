#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re
import datetime
import ddl
from google.appengine.ext import db

"""
#----------------------------------------------------------
# The DDL checker module of Flow Platform
#
# The module is for Databases field checking
# For both db checking and application checking, the moudle
# is seperated to external module.
#
#----------------------------------------------------------
"""

class Authentication(object):
    #
    # List of check methods
    @staticmethod
    def checkId(value):
        if value is None:
            return value

        if ddl.Authentication.gql("WHERE id=:1", value).count() > 1:
            raise db.BadValueError('Authentication ID must be unique')
        return value

    def __init__(self, authObj):
        self.authObj = authObj

        Authentication.checkId(self.authObj.id)

class Individual(object):
    @staticmethod
    def checkEmail(value):
        if value is None:
            return value

        find = re.search('@',value)
        if(find == None):
            raise db.BadValueError('!!! E-mail %s is incorrect (checkEmail)'%value ) 
        return value

    #check lenghth of cell's number is 10
    @staticmethod
    def checkPhone(value):
        if value is None:
            return value

        if(len(value)!=10):
            raise db.BadValueError('!!! Phone %s is incorrect (checkPhone)'%value)
        return value

    #Age whould between 4 and 120
    @staticmethod
    def checkBirth(value):
        if value is None:
            return value

        age = (datetime.date.today() - value).days / 365
        if age < 4 or age > 120:
            raise db.BadValueError('!!! Birth %s is incorrect (checkBirth)' %value)
        return value
