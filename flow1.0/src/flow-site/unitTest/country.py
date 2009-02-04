#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import datetime
from db.ddl import CountryCity
from google.appengine.api import users
from django.http import HttpResponse

def create(request):
    response = HttpResponse(mimetype="text/plain; charset=utf-8")
    taiwanCities = (
           ('Taipei',           u'臺北縣市'),
           ('Keelung',          u'基隆市'),
           ('Taoyuan',          u'桃園縣'),
           ('Hsinchu',          u'新竹縣市'),
           ('Miaoli',           u'苗栗縣'),
           ('Taichung',         u'台中縣市'),
           ('Changhua',         u'彰化縣'),
           ('Nantou',           u'南投縣'),
           ('Yunlin',           u'雲林縣'),
           ('Chiayi',           u'嘉義縣市'),
           ('Tainan',           u'台南縣市'),
           ('Kaohsiung',        u'高雄縣市'),
           ('Pingtung',         u'屏東縣'),
           ('Taitung',          u'台東縣'),
           ('Hualien',          u'花蓮縣'),
           ('Yilan',            u'宜蘭縣'),
           ('Penghu',           u'澎湖縣'),
    )


    try:
        for (cityEN, cityTC) in taiwanCities:
            entity = CountryCity(country_tc=u"中華民國", country_en="ROC", state_tc=u"台灣省", state_en="Taiwan", city_tc=cityTC, city_en=cityEN, zip_code="???")
            entity.put()
    except:
        response.write('新增 CountryCity 失敗 (%s)' % str(sys.exc_info()))
        return response

    response.write('新增 CountryCity 成功!!!')
    return response
