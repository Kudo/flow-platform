# -*- coding: big5 -*-
from django.conf import settings
from google.appengine.api import mail

STR_CANCEL_CONTENT=u'''

�ܩ�p�A%(npo)s �]�U�C��]����"%(event)s"����

--
%(reason)s
--

�J�߷P�±z�����W�A

���ݤU�@�����|�A

�P�z�@�ɬ����q�I�X���߼֡C

�Y���Ӥu�C�X���x
'''

STR_JOIN_APPROVED_CONTENT=u'''

%(npo)s �w�f�ֳq�L�z�����ʳ��W�A

�z���W�ѥ[�����ʬ� %(event)s�A

���ʶ}�l�ɶ��� %(start_time)s�A

�Y���Ӥu�C�X���x
'''

def sendEventCancelMail(objVolunteer,objEvent,strReason):
    message = mail.EmailMessage()
    message.subject=u'[�Y���Ӥu�C�X���x] ���ʨ����q��'
    message.sender = settings.ADMIN_EMAIL
    message.to = objVolunteer.volunteer_id.email()
    message.body = STR_CANCEL_CONTENT%{'event':objEvent.event_name,
                                       'reason':strReason,
                                       'npo':objEvent.npo_profile_ref.npo_name}
    message.send()

def sendJoinEventApprovedMail(objVolunteer,objEvent):
    message = mail.EmailMessage()
    message.subject=u'[�Y���Ӥu�C�X���x] �z�����W�w�g�q�L�f��'
    message.sender = settings.ADMIN_EMAIL
    message.to = objVolunteer.volunteer_id.email()
    message.body = STR_JOIN_APPROVED_CONTENT%{'event':objEvent.event_name,
                                              'npo':objEvent.npo_profile_ref.npo_name,
                                              'start_time':objEvent.start_time.strftime('%Y-%m-%d %H:%M')}
    message.send()
    