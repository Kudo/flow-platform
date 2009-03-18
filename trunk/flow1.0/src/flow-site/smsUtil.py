# coding=big5
import logging
import urllib

def sendSms(strPhoneNumber,objUniContent):
    strUrl='http://api.twsms.com/send_sms.php'
    dicData={'username':'flowadmin',
             'password':'anho1133',
             'type':'now',
             'encoding':'unicode',
             'mobile':strPhoneNumber,
             'message':objUniContent.encode('utf8')
             }
    strRequest=strUrl+'?'+urllib.urlencode(dicData)
    print `strRequest`
    print urllib.urlopen(strRequest,proxies={'http':'http://twproxy.trendmicro.com:8080'}).read()

def sendSmsOnGAE(strPhoneNumber,objUniContent):
    from google.appengine.api.urlfetch import fetch
    strUrl='http://api.twsms.com/send_sms.php'
    dicData={'username':'flowadmin',
             'password':'anho1133',
             'type':'now',
             'encoding':'unicode',
             'mobile':strPhoneNumber,
             'message':objUniContent.encode('utf8')
             }
    strRequest=strUrl+'?'+urllib.urlencode(dicData)
    resp=fetch(strRequest)
    logging.info(resp.content)
    return resp.content
