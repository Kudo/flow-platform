# -*- coding: big5 -*-
from django.conf import settings
from google.appengine.api import mail

STR_CANCEL_CONTENT=u'''

�ܩ�p�A"%(event)s"���ʦ]�U�C��]����

--
%(reason)s
--

�J�߷P�±z�����W�A

���ݤU�@�����|�A

�P�z�@�ɬ����q�I�X���߼֡C

�Y���Ӥu�C�X���x
'''

STR_JOIN_APPROVED_CONTENT=u'''

�z���W�ѥ["%(event)s"���ʡA�w�g�q�L�f�֡C

�Y���Ӥu�C�X���x
'''

def sendEventCancelMail(objVolunteer,objEvent,strReason):
    message = mail.EmailMessage()
    message.subject=u'[�Y���Ӥu�C�X���x] ���ʨ����q��'
    message.sender = settings.ADMIN_EMAIL
    message.to = objVolunteer.volunteer_id.email()
    message.body = STR_CANCEL_CONTENT%{'event':objEvent.event_name,'reason':strReason}
    message.send()

def sendJoinEventApprovedMail(objVolunteer,objEvent):
    message = mail.EmailMessage()
    message.subject=u'[�Y���Ӥu�C�X���x] �z���W�ѥ[�����ʤw�f�ֳq�L'
    message.sender = settings.ADMIN_EMAIL
    message.to = objVolunteer.volunteer_id.email()
    message.body = STR_JOIN_APPROVED_CONTENT%{'event':objEvent.event_name}
    message.send()
    