# -*- coding: big5 -*-
from django.conf import settings
from google.appengine.api import mail

STR_CANCEL_CONTENT='''

�ܩ�p�A"%(event)s"���ʦ]�U�C��]����

--
%(reason)s
--

�J�߷P�±z�����W�A

���ݤU�@�����|�A

�P�z�@�ɬ����q�I�X���߼֡C

�Y���Ӥu�C�X���x
'''

def sendEventCancelMail(objVolunteer,objEvent,strReason):
    message = mail.EmailMessage()
    message.subject=u'[�Y���Ӥu�C�X���x] ���ʨ����q��'
    message.sender = settings.ADMIN_EMAIL
    message.to = objVolunteer.volunteer_id.email()
    message.body = STR_CANCEL_CONTENT%{'event':objEvent.event_name,'reason':strReason}
    message.send()
