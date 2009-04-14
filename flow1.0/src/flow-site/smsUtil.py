# coding=big5
import logging,datetime,re
import urllib
from db import ddl

def sendSms(strPhoneNumber,objUniContent):
    smsSettings=getSmsSettings()
    strUrl='http://api.twsms.com/send_sms.php'
    dicData={'username':smsSettings.account,
             'password':smsSettings.password,
             'type':'now',
             'encoding':'unicode',
             'mobile':strPhoneNumber,
             'message':objUniContent.encode('utf8')
             }
    strRequest=strUrl+'?'+urllib.urlencode(dicData)
    print `strRequest`
    print urllib.urlopen(strRequest,proxies={'http':'http://twproxy.trendmicro.com:8080'}).read()

def getSmsSettings():
    smsSettings = ddl.SmsSettings.all()
    if not smsSettings.count():
        smsSettings=ddl.SmsSettings(account='',password='')
        smsSettings.put()
        return smsSettings
    return smsSettings[0]

def sendSmsOnGAE(strPhoneNumber,objUniContent,npo_id='',volunteer_id='',event_id=''):
    from google.appengine.api.urlfetch import fetch
    smsSettings=getSmsSettings()
    strUrl='http://api.twsms.com/send_sms.php'
    dicData={'username':smsSettings.account,
             'password':smsSettings.password,
             'type':'now',
             'encoding':'unicode',
             'mobile':strPhoneNumber,
             'message':objUniContent.encode('utf8')
             }
    strRequest=strUrl+'?'+urllib.urlencode(dicData)
    resp=fetch(strRequest)
    logging.info(resp.content)
    objSmsLog=ddl.SmsLog(send_time=datetime.datetime.utcnow(),cellphone_no=strPhoneNumber,result=resp.content,
                         npo_id=str(npo_id),volunteer_id=str(volunteer_id),event_id=str(event_id))
    objSmsLog.put()
    objMatch=re.search('resp=([-]*[\d]*)',resp.content)
    if not objMatch:
        raise RuntimeError('Send SMS failed! Error:%s'%resp.content)
    else:
        if len(objMatch.group(1))!=8:
            raise RuntimeError('Send SMS failed! Error:%s'%objMatch.group(1))
        return objMatch.group(1)
    
