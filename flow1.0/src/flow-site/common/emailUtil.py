# -*- coding: big5 -*-
from django.conf import settings
from google.appengine.api import mail

STR_CANCEL_CONTENT=u'''

很抱歉，%(npo)s 因下列原因取消"%(event)s"活動

--
%(reason)s
--

衷心感謝您的報名，

期待下一次機會，

與您共享為公益付出的喜樂。

若水志工媒合平台
'''

STR_JOIN_APPROVED_CONTENT=u'''

%(npo)s 已審核通過您的活動報名，

您報名參加的活動為 %(event)s，

活動開始時間為 %(start_time)s，

若水志工媒合平台
'''

def sendEventCancelMail(objVolunteer,objEvent,strReason):
    message = mail.EmailMessage()
    message.subject=u'[若水志工媒合平台] 活動取消通知'
    message.sender = settings.ADMIN_EMAIL
    message.to = objVolunteer.volunteer_id.email()
    message.body = STR_CANCEL_CONTENT%{'event':objEvent.event_name,
                                       'reason':strReason,
                                       'npo':objEvent.npo_profile_ref.npo_name}
    message.send()

def sendJoinEventApprovedMail(objVolunteer,objEvent):
    message = mail.EmailMessage()
    message.subject=u'[若水志工媒合平台] 您的報名已經通過審核'
    message.sender = settings.ADMIN_EMAIL
    message.to = objVolunteer.volunteer_id.email()
    message.body = STR_JOIN_APPROVED_CONTENT%{'event':objEvent.event_name,
                                              'npo':objEvent.npo_profile_ref.npo_name,
                                              'start_time':objEvent.start_time.strftime('%Y-%m-%d %H:%M')}
    message.send()
    