# -*- coding: big5 -*-
from django.conf import settings
from google.appengine.api import mail

STR_CANCEL_CONTENT=u'''

很抱歉，"%(event)s"活動因下列原因取消

--
%(reason)s
--

衷心感謝您的報名，

期待下一次機會，

與您共享為公益付出的喜樂。

若水志工媒合平台
'''

STR_JOIN_APPROVED_CONTENT=u'''

您報名參加"%(event)s"活動，已經通過審核。

若水志工媒合平台
'''

def sendEventCancelMail(objVolunteer,objEvent,strReason):
    message = mail.EmailMessage()
    message.subject=u'[若水志工媒合平台] 活動取消通知'
    message.sender = settings.ADMIN_EMAIL
    message.to = objVolunteer.volunteer_id.email()
    message.body = STR_CANCEL_CONTENT%{'event':objEvent.event_name,'reason':strReason}
    message.send()

def sendJoinEventApprovedMail(objVolunteer,objEvent):
    message = mail.EmailMessage()
    message.subject=u'[若水志工媒合平台] 您報名參加的活動已審核通過'
    message.sender = settings.ADMIN_EMAIL
    message.to = objVolunteer.volunteer_id.email()
    message.body = STR_JOIN_APPROVED_CONTENT%{'event':objEvent.event_name}
    message.send()
    