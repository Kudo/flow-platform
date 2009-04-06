#!/usr/bin/env python
# -*- coding: utf-8 -*-

_cityList = [
   u'基隆市',
   u'台北市',
   u'台北縣',
   u'桃園縣',
   u'新竹市',
   u'新竹縣',
   u'苗栗縣',
   u'台中市',
   u'台中縣',
   u'彰化縣',
   u'南投縣',
   u'雲林縣',
   u'嘉義市',
   u'嘉義縣',
   u'台南市',
   u'台南縣',
   u'高雄市',
   u'高雄縣',
   u'屏東縣',
   u'台東縣',
   u'花蓮縣',
   u'宜蘭縣',
   u'澎湖縣',
   u'金門縣',
   u'連江縣',
   u'其他地區',
]

_regionList = [
    u'全省',
    u'北區',
    u'中區',
    u'南區',
]

def getResidentList():
	return _cityList

def getRegionList():
    return _regionList
