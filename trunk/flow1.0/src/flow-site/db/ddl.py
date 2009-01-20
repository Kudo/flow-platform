#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
#----------------------------------------------------------
# The DDL (Data Definition Layer) of Flow Platform
#
# Copyright 2008-2009 Trend Micro and Flow Internal. All rights reserved.
#
# THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE OF TREND MICRO.
# The copyright notice above does not evidence any
# actual or intended publication of such source code.
#
#
# *** NAMING CONVENTION ***
# Each attribute name of a entity class (such as "founder" in class
# "NpoProfile") is simply named as such, without the Hugarian notation
# prefix (such as "strFounder"). It is *PURPOSELY* designed in this way
# so that the following GQL query is possible:
#
#    result = db.GqlQuery(
#        "SELECT * FROM NpoProfile WHERE founder = :1", "John Doe")
# or:
#    result = NpoProfile.gql("WHERE founder = :1", "John Doe")
#
#
# *** PLATFORM ***
# The code in this file needs GAE 1.1.7 or above.
#
#
# *** REVISION HISTORY ***
# 2008/11/07, Tony Chu:              first edition, based on the schema from Stanley Hsiao
# 2008/11/18, Kudo Chien:            add validators and counter-per-class
# 2008/12/08, Kudo Chien:            adopt the use of _from_entity (from GAE 1.1.7) to simplify invocation of constructor
# 2008/12/19, Alex Chiu:             revised schema to "FlowPlatform_DataSchema_v0.4.xls"
# 2008/12/19, Tony Chu:              revise code based on Alex's schema "FlowPlatform_DataSchema_v0.4.xls"
# 2008/12/30, Kudo Chien:            add SearchableStringProperty for Chinese full text search
# 2009/01/13, Tony Chu & Kudo Chien: bug fix: un-initialized data fields were used to construct other fields, now they are
#                                    constructed in the correct order
# 2009/01/19, Kudo Chien:            improve search() performance for SearchableStringProperty by chaining query filter
# 2009/01/20, Tony Chu:              update code based on schema "FlowPlatform_DataSchema_v0.5.xls";
#                                    simplify require-constraint by removing redundant ones
#
#
# *** REMARKS ***
# The constraints of each attribute in an entity group are normally shown as keyword arguments of the property function.
# For instance, db.StringProperty(required=True). However, sometimes it is not possible to do that and must be enforced
# by the constructor, validator or caller's program logic. In this case, the constraints are shown in the comments.
# Many attributes are commented as "# the constraint must be enforced by program logic", which is a reminder that you
# should LOOK CLOSER INTO THE SCHEMA about the proper use of these attributes. It is possible to enforce the related
# constraints described by the schema in this DDL code, but it would be a terrible performance hindrance.
#
# Note that although in the schema it is normally shown with a simple name, for instance "EVENT_PROFILE", for referencing
# an entity to another group, we have adopted a different coding convention:
#     1. Create an attribute which is the actual reference to the other entity, the naming convention is "X_ref",
#        for instance "event_profile_ref".
#     2. Create an integer attribut to keep the ID number of the referenced entity, the naming convention is "X_id",
#        for instance "event_profile_id".
# The reference is for the places where the object-oriented way of data look-up is needed, which is very convenient.
# The ID number is used when you want to show it to the user, and later the user can type it and the program can
# query for the related entity, explained in "USAGE" section.
#
#
# *** UNIT-TEST ***
# 1. Prepare an "app.yaml", the script line should be "script: ddl.py", and save the file where this ddl.py is located.
# 2. Start the GAE SDK local server emulator: dev_appserver.py --clear_datastore {the-path-where-app.yaml-is-saved}
# 3. Open your browser, type the address: http://localhost:8080/
# 4. The output should be a bunch of XML codes, and no <UnitTestFailure> is shown. If it does show up, you are fortunate
#    enough to be eligible to debug it. ;p
#
#
# *** USAGE ***
# 1. All tables in the schema are implemented as entity-group classes and exported by the __all__ built-in variable.
# 2. An entity instance (record) is created by calling the related constructor. The attributes (columns) are filled
#    with the proper keyword parameters. Don't forget to SAVE IT with the .put() command. This is a memory-to-DB route.
# 3. To retrieve the data (DB-to-memory), use the .get() command. For multiple instances of data, use .fetch().
# 4. To discard a entity (record), use the .delete() command.
# 5. As explained in the above REMARKS section, you should use references as often as you can for performance efficiency.
#    However, there are times when you need to provide the ID numbers for the user, you can use the following query to
#    obtain the entity: (using NpoProfile as an example)
#          entity = NpoProfile.gql("WHERE id = :1", id).get()
#    The result would be None if the id is bogus.
#
#
# *** USAGE: SearchableStringProperty ***
# Limitation: In current GAE implementation, StringProperty is the only allowed property.
# To use this full-text search function, bear in mind that you are costing much more CPU / memory resource.
# If, however, you do need a full-text search feature, follow the steps:
#   1. Add an attribute with 'SearchableStringProperty' to the entity group, presuming it's called EntityGroup.
#   2. Initiate the entity group class as usual.
#   3. The calling convention is as follow, the result is a list of matched entries:
#       matchList = EntityGroup.all().search(EntityGroup.attribute, "The keywords you want to search for")
#   4. If you want to get the origional input text in SearchableStringProperty, it is stored in the first element.
#       e.g. matchList[i].attribute[0]
#----------------------------------------------------------
"""

import sys
import datetime
import cgi
import re
import string
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

"""
#----------------------------------------------------------
# Classes exported from this module.
#----------------------------------------------------------
"""

__all__ = ["NpoProfile", "NpoEmail", "NpoContact", "NpoPhone", "NpoAdmin", "VolunteerProfile", "QuestionnaireTemplate",
           "EventProfile", "VolunteerEvent", "VolunteerIm", "VolunteerLog", "EventNews", "EventQuestion", "EventAnswer",
           "EventQuestionnaire", "ReportTemplate", "EventReport", "ImproperReport", "CountryCity", "Target", "Field"]

"""
#----------------------------------------------------------
# Validators /constraints.
#----------------------------------------------------------
"""

def vaNonnegative(value):
    if value < 0:
        raise db.BadValueError("Non-negative value expected.")
    return value

def vaEventId(id):
    if len(id) != 10:
        raise db.BadValueError("Event-ID length error.")
    if not re.compile("^[0-9]+$").match(id):
        raise db.BadValueError("Event-ID should be 10 digits.")
    return id

def vaIP(ip):
    if not re.compile("^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$").match(ip):
        raise db.BadValueError("Invalid IP address.")
    return ip

def vaEmail(email):
    if email is None:
        return email
    if not re.compile("^[^@]+@[^@]+$").match(email):
        raise db.BadValueError("Invalid E-mail address.")
    return email

def vaBirthDate(date):
    if date is None:
        return date
    age = (datetime.date.today() - date).days / 365
    if (age < 4) or (age > 120):
        raise db.BadValueError("Invalid birth date.")
    return date

def require(kargs, *properties):
    for prop in properties:
        if prop not in kargs:
            raise db.BadValueError("Property " + prop + " is required")


"""
#----------------------------------------------------------
# Private classes.
#----------------------------------------------------------
"""

class Counter(db.Model):
    """
    The counter singleton class.
    This class has been revised so that each entity class can have its own
    unique counter, thanks to Kudo Chien's idea.
    """
    className = db.StringProperty(required=True)
    counter   = db.IntegerProperty(required=True)

    @staticmethod
    def init(obj):
        """
        Start a new counter singleton. User should not directly call this method.
        """
        ctr = Counter(className=obj.__class__.__name__, counter=0)
        ctr.put()
        return ctr.counter

    @staticmethod
    def increment(key):
        """
        Increment the singleton by 1. User should not directly call this method.
        """
        ctr = db.get(key)
        ctr.counter += 1
        ctr.put()
        return ctr.counter

    @staticmethod
    def next(obj):
        """
        Obtain the next available counter (started from 0). Sample usages:
            Counter.next(obj) # the formal way
            counter[obj]      # the syntatical-sugar way
        """
        acc = Counter.gql("WHERE className=:1", obj.__class__.__name__).get()
        if acc == None:
            return db.run_in_transaction(Counter.init, obj)
        else:
            return db.run_in_transaction(Counter.increment, acc.key())

    def __getitem__(self, obj):
        """
        The purpose of this method is to support the following syntatical sugar:
            counter[obj]
        which is slightly more readable (and less typing effort) than this:
            Counter.next(obj)
        """
        return Counter.next(obj)

counter = Counter(className="Counter", counter=0)

# end class Counter


def Ngram(text=None, n=2, encFrom="UTF-8", lowerCase=True):
    """
    The Ngram function will do N-gram for given text and n.

    Args:
        text:       text to do Ngram
        n:          the N of Ngram
        encFrom:    the encoding of text, if it is None, it was said that is unicode type.
        lowerCase:  if it is True, convert all the result grams to lowercase string.

    Returns:
        The list of grams
    """
    if not text:
        return []
    if isinstance(text, str) and encFrom:
        text = unicode(text, encFrom)
    if len(text) < n:
        return [text]

    grams = set()
    # split English and non-English
    text = re.sub("([^a-zA-Z0-9]*?)([a-zA-Z0-9]+)([^a-zA-Z0-9]*?)", "\\1 \\2 \\3", text)

    # split terms by delimiters
    delimits = string.whitespace + string.punctuation + u"，。、！：；‧〝〞‘’“”『』「」〈〉《》【】﹝﹞？"
    textList = re.split("["+delimits+"]", text)

    # do ngram
    alnumRe = re.compile("^[a-zA-Z0-9]+$")
    for segment in textList:
        if not segment:
            continue
        if alnumRe.match(segment):
            if lowerCase:
                segment = segment.lower()
            grams.add(segment)
        else:
            lenSegment = len(segment)
            if lenSegment < n:
                # Note: If you want to get the grams which length are less than n, unmark the line below
                #grams.add(segment)
                continue
            for i in range(lenSegment - n + 1):
                grams.add(segment[i:i+n])
    return list(grams)

# end Ngram()


class SearchableStringProperty(db.StringListProperty):
    """
    This property supports Chinese full text search by storing n-gram into Datastore.
    """
    def __init__(self, encFrom="UTF-8", **kargs):
        self._encFrom = encFrom
        super(SearchableStringProperty, self).__init__(**kargs)

    def __set__(self, model_instance, value):
        if value and type(value) is not list: # Avoid to do Ngram again while called from from_entity()
            grams = set()
            for n in range(1, 3):
                for gram in Ngram(text=value, n=n, encFrom=self._encFrom):
                    grams.add(gram)
            if isinstance(value, str) and self._encFrom:
                value = unicode(value, self._encFrom)
            value = [value] + list(grams)
        super(SearchableStringProperty, self).__set__(model_instance, value)

# end class SearchableStringProperty


class FlowDdlModel(db.Model):
    """
    All DDL entity classes must inherit from this class so as to make use of
    our special version of __str__() method, which tries to generate the
    serializable XML format.
    This superclass also provides an integer attribute "id" which is unique within the class.
    """
    id = db.IntegerProperty() # auto-generated

    def __init__(self, parent=None, key_name=None, app=None, _from_entity=False, **kargs):
        if not _from_entity and "id" not in kargs:
            kargs["id"] = counter[self]
        db.Model.__init__(self, parent, key_name, app, _from_entity, **kargs)

    def __str__(self):
        ret = ["<", self.__class__.__name__, ' key="', str(self.key()), '"']
        children = []
        for member in dir(self):
            if not callable(getattr(self, member)) and member[0] != "_" and not member.endswith("_set"):
                ret.append(" " + member + "=")
                value = getattr(self, member)
                if member.endswith("ref"):
                    if value:
                        ret.append('"' + cgi.escape(str(value.key())) + '"')
                        if member != "back_ref":
                            # The "back_ref" is a reference from a child node to parent.
                            # We must avoid adding it to the "children" list or else the
                            # result would be an infinite recursion.
                            children.append(str(value))
                    else:
                        ret.append('"None"')
                else:
                    ret.append('"' + cgi.escape(str(value)) + '"')
        if children == []:
            ret.append(" />")
        else:
            ret.append(">\n")
            ret.append("\n".join(children) + "\n")
            ret.append("</" + self.__class__.__name__ + ">")
        return "".join(ret)

    @classmethod
    def all(cls):
        return FlowDdlModel.Query(cls)

    class Query(db.Query):
        def search(self, property, query, encFrom="UTF-8"):
            if not isinstance(property, SearchableStringProperty):
                raise db.BadPropertyError("Currently, search() is only for SearchableStringProperty.")
            if not query:
                return []
            if isinstance(query, str) and encFrom:
                query = unicode(query, encFrom)

            queryList = re.sub("([^a-zA-Z0-9]{2})", "\\1 ", query).split()
            queryObj = self
            for query in queryList:
                query = query.lower()
                queryObj = queryObj.filter(property.name + " = ", query)
            entryList = []
            queryList = query.split()
            for entry in queryObj:
                isMatch = True
                for query in queryList:
                    if query not in getattr(entry, property.name)[0]:
                        isMatch = False
                if isMatch:
                    entryList.append(entry)
            return entryList

# end class FlowDdlModel


"""
#----------------------------------------------------------
# Public classes, as declared by __all__.
#----------------------------------------------------------
"""

class NpoProfile(FlowDdlModel):
    """
    NPO_PROFILE
    """
    npo_id                 = db.StringProperty()                         # auto-generated as npo_category:id
    npo_category           = db.CategoryProperty(choices=set(["NPO", "ENT", "EDU", "SEF"])) # default to "NPO"
    npo_name               = db.StringProperty(required=True)
    founder                = db.StringProperty(required=True)
    google_acct            = db.UserProperty(required=True)
    valid_google_acct      = db.BooleanProperty()                        # default to True
    brief_intro            = db.TextProperty()
    logo                   = db.LinkProperty()
    website                = db.LinkProperty()
    blog                   = db.LinkProperty()
    photo_link             = db.StringListProperty(db.Link)
    video_link             = db.StringListProperty(db.Link)
    article_link           = db.StringListProperty(db.Link)
    country                = db.StringProperty(required=True)            # the constraint must be enforced by program logic
    postal                 = db.StringProperty(required=True)
    state                  = db.StringProperty(required=True)            # the constraint must be enforced by program logic
    city                   = db.StringProperty(required=True)            # the constraint must be enforced by program logic
    district               = db.StringProperty(required=True)            # the constraint must be enforced by program logic
    street1                = db.StringProperty(multiline=True)
    street2                = db.StringProperty(multiline=True)
    founding_date          = db.DateProperty(required=True)
    authority              = db.StringProperty(required=True)
    service_region         = db.StringListProperty()
    service_target         = db.StringListProperty()
    service_field          = db.StringListProperty()
    bank_acct_no           = db.StringProperty()
    bank_acct_name         = db.StringProperty()
    tag                    = db.StringListProperty()                     # required
    status                 = db.StringProperty(required=True, choices=set(["new application", "approving", "approved", "approval failed", "authenticating",
                                                                           "authenticated", "authenticatin failed", "normal", "revoked", "abusive usage",
                                                                           "terminated"]))
    docs_link              = db.StringListProperty()                     # required
    total_events           = db.IntegerProperty(validator=vaNonnegative) # default to 0
    total_event_volunteers = db.IntegerProperty(validator=vaNonnegative) # default to 0
    total_event_hours      = db.IntegerProperty(validator=vaNonnegative) # default to 0
    npo_rating             = db.RatingProperty(required=True)            # range=[0..100]
    news_list              = db.ListProperty(db.Text)
    create_time            = db.DateTimeProperty(required=True)
    update_time            = db.DateTimeProperty(required=True)
    members                = db.ListProperty(db.Key)                     # the constraint must be enforced by program logic

    def __init__(self, parent=None, key_name=None, app=None, _from_entity=False, **kargs):
        if not _from_entity:
            require(kargs, "tag", "docs_link")
            if "npo_category" not in kargs:
                kargs["npo_category"] = "NPO"
            if "valid_google_acct" not in kargs:
                kargs["valid_google_acct"] = True
            if "total_events" not in kargs:
                kargs["total_events"] = 0
            if "total_event_volunteers" not in kargs:
                kargs["total_event_volunteers"] = 0
            if "total_event_hours" not in kargs:
                kargs["total_event_hours"] = 0

        FlowDdlModel.__init__(self, parent, key_name, app, _from_entity, **kargs)

        if not _from_entity:
            self.npo_id = self.npo_category + ":" + str(self.id)

    @classmethod
    def unitTest(cls):
        startUnitTest("NpoProfile.unitTest")

        user = users.User("john_doe@gmail.com")
        now  = datetime.datetime.utcnow()
        npo  = NpoProfile(npo_name="Save the Orcas", founder="John Doe", google_acct=user, country="ROC", postal="104", state="Taiwan", city="Taipei",
                          district="Nangang", founding_date=datetime.date(1980, 1, 1), authority="GOV", tag=["wild lives", "marines"],
                          status="new application", docs_link=["Timbuck2"], npo_rating=1, create_time=now, update_time=now)

        npo.put()
        writeln(npo)
        return npo

# end class NpoProfile


class NpoNews(FlowDdlModel):
    """
    NPO_NEWS
    """
    npo_profile_ref = db.ReferenceProperty(required=True, reference_class=NpoProfile, collection_name="news2npo")
    npo_profile_id  = db.IntegerProperty() # auto-generated from npo_profile_ref.id
    news_no         = db.IntegerProperty(required=True)
    create_date     = db.DateTimeProperty(required=True)
    news            = db.TextProperty(required=True)

    def __init__(self, parent=None, key_name=None, app=None, _from_entity=False, **kargs):
        FlowDdlModel.__init__(self, parent, key_name, app, _from_entity, **kargs)

        if not _from_entity:
            self.npo_profile_id = self.npo_profile_ref.id

    @classmethod
    def unitTest(cls, npo):
        startUnitTest("NpoNews.unitTest")

        now  = datetime.datetime.utcnow()
        news = NpoNews(npo_profile_ref=npo, news_no=99101, create_date=now, news="time to go")

        news.put()
        writeln(news)
        rollBack(news)

# end class NpoNews


class NpoEmail(FlowDdlModel):
    """
    NPO_EMAIL
    """
    npo_profile_ref = db.ReferenceProperty(required=True, reference_class=NpoProfile, collection_name="emails2npo")
    npo_profile_id  = db.IntegerProperty() # auto-generated from npo_profile_ref.id
    email_type      = db.StringProperty(required=True, choices=set(["Default", "Group", "GMail", "Others"]))
    email_addr      = db.EmailProperty(required=True, validator=vaEmail)
    hide            = db.BooleanProperty() # default to False

    def __init__(self, parent=None, key_name=None, app=None, _from_entity=False, **kargs):
        if not _from_entity and "hide" not in kargs:
            kargs["hide"] = False

        FlowDdlModel.__init__(self, parent, key_name, app, _from_entity, **kargs)

        if not _from_entity:
            self.npo_profile_id = self.npo_profile_ref.id

    @classmethod
    def unitTest(cls, npo):
        startUnitTest("NpoEmail.unitTest")

        email = NpoEmail(npo_profile_ref=npo, email_type="GMail", email_addr="foobar@gmail.com")

        email.put()
        writeln(email)
        rollBack(email)

# end class NpoEmail


class NpoContact(FlowDdlModel):
    """
    NPO_CONTACT
    """
    npo_profile_ref = db.ReferenceProperty(required=True, reference_class=NpoProfile, collection_name="contacts2npo")
    npo_profile_id  = db.IntegerProperty() # auto-generated from npo_profile_ref.id
    contact_type    = db.StringProperty(required=True, choices=set(["Major", "Manager", "Chair", "Director", "Supervisor", "PR", "Lead", "Other"]))
    contact_name    = db.StringProperty(required=True)
    contact_email   = db.EmailProperty(required=True, validator=vaEmail)
    contact_phone   = db.PhoneNumberProperty()
    volunteer_id    = db.UserProperty(required=True)

    def __init__(self, parent=None, key_name=None, app=None, _from_entity=False, **kargs):
        FlowDdlModel.__init__(self, parent, key_name, app, _from_entity, **kargs)

        if not _from_entity:
            self.npo_profile_id = self.npo_profile_ref.id

    @classmethod
    def unitTest(cls, npo):
        startUnitTest("NpoContact.unitTest")

        email   = "john_doe@gmail.com"
        user    = users.User(email)
        contact = NpoContact(npo_profile_ref=npo, contact_type="Other", contact_name="John Doe", contact_email=email,
                             volunteer_id=user)

        contact.put()
        writeln(contact)
        rollBack(contact)

# end class NpoContact


class NpoPhone(FlowDdlModel):
    """
    NPO_PHONE
    """
    npo_profile_ref = db.ReferenceProperty(required=True, reference_class=NpoProfile, collection_name="phones2npo")
    npo_profile_id  = db.IntegerProperty() # auto-generated from npo_profile_ref.id
    phone_type      = db.StringProperty(required=True, choices=set(["Fixed", "Mobile", "Fax"]))
    phone_no        = db.PhoneNumberProperty(required=True)
    hide            = db.BooleanProperty() # default to False

    def __init__(self, parent=None, key_name=None, app=None, _from_entity=False, **kargs):
        if not _from_entity and "hide" not in kargs:
            kargs["hide"] = False

        FlowDdlModel.__init__(self, parent, key_name, app, _from_entity, **kargs)

        if not _from_entity:
            self.npo_profile_id = self.npo_profile_ref.id

    @classmethod
    def unitTest(cls, npo):
        startUnitTest("NpoPhone.unitTest")

        phone = NpoPhone(npo_profile_ref=npo, phone_type="Mobile", phone_no="0910-000000")

        phone.put()
        writeln(phone)
        rollBack(phone)

# end class NpoPhone


class NpoAdmin(FlowDdlModel):
    """
    NPO_ADMIN
    """
    npo_profile_ref = db.ReferenceProperty(required=True, reference_class=NpoProfile, collection_name="admins2npo")
    npo_profile_id  = db.IntegerProperty() # auto-generated from npo_profile_ref.id
    admin_role      = db.StringProperty(required=True, choices=set(["Main", "Event", "Security", "Checker", "News"]))
    volunteer_id    = db.UserProperty(required=True)

    def __init__(self, parent=None, key_name=None, app=None, _from_entity=False, **kargs):
        FlowDdlModel.__init__(self, parent, key_name, app, _from_entity, **kargs)

        if not _from_entity:
            self.npo_profile_id = self.npo_profile_ref.id

    @classmethod
    def unitTest(cls, npo):
        startUnitTest("NpoAdmin.unitTest")

        user  = users.User("john_doe@gmail.com")
        admin = NpoAdmin(npo_profile_ref=npo, admin_role="Event", volunteer_id=user)

        admin.put()
        writeln(admin)
        rollBack(admin)

# end class NpoAdmin


class VolunteerProfile(FlowDdlModel):
    """
    VOLUNTEER_PROFILE
    """
    volunteer_id         = db.UserProperty(required=True)   # the constraint (UNIQUE) must be enforced by program logic
    id_no                = db.StringProperty(required=True)
    valid_google_acct    = db.BooleanProperty()             # default to True
    volunteer_last_name  = db.StringProperty(required=True)
    volunteer_first_name = db.StringProperty(required=True)
    gmail                = db.EmailProperty(required=True, validator=vaEmail)
    alternate_email      = db.EmailProperty(validator=vaEmail)
    date_birth           = db.DateProperty(required=True, validator=vaBirthDate)
    expertise            = db.StringListProperty()          # required
    sex                  = db.CategoryProperty(required=True, choices=set(["Male", "Female"]))
    phone_no             = db.PhoneNumberProperty(required=True)
    cellphone_no         = db.PhoneNumberProperty()
    hide_cellphone       = db.BooleanProperty()             # default to False
    resident_country     = db.StringProperty(required=True) # the constraint must be enforced by program logic
    resident_postal      = db.StringProperty(required=True)
    resident_state       = db.StringProperty(required=True) # the constraint must be enforced by program logic
    resident_city        = db.StringProperty(required=True) # the constraint must be enforced by program logic
    resident_district    = db.StringProperty(required=True) # the constraint must be enforced by program logic
    tag                  = db.StringListProperty()
    school               = db.StringProperty()
    organization         = db.StringProperty()
    title                = db.StringProperty()
    blog                 = db.LinkProperty()
    brief_intro          = db.TextProperty()
    logo                 = db.LinkProperty()
    photo_link           = db.StringListProperty(db.Link)
    video_link           = db.StringListProperty(db.Link)
    article_link         = db.StringListProperty(db.Link)
    prefer_region        = db.StringListProperty()          # required
    prefer_zip           = db.StringListProperty()          # required
    prefer_target        = db.StringListProperty()          # required
    prefer_field         = db.StringListProperty()          # required
    prefer_group         = db.StringListProperty()          # required
    create_time          = db.DateTimeProperty(required=True)
    update_time          = db.DateTimeProperty(required=True)
    total_serv_hours     = db.IntegerProperty()             # default to 0
    total_reg_events     = db.IntegerProperty()             # default to 0
    total_serv_events    = db.IntegerProperty()             # default to 0
    total_sharing        = db.IntegerProperty()             # default to 0
    volunteer_rating     = db.RatingProperty(required=True) # range=[0..100]
    medal                = db.StringListProperty()
    status               = db.StringProperty(required=True, choices=set(["new application", "authenticating", "authenticated", "authenticatin failed",
                                                                         "normal", "revoked", "abusive usage", "terminated"]))
    friends              = db.ListProperty(db.Key)          # the constraint must be enforced by program logic
    volunteer_profile    = db.ListProperty(db.Key)          # the constraint must be enforced by program logic
    npo_profile_ref      = db.ListProperty(db.Key)          # the constraint must be enforced by program logic
    search_text          = SearchableStringProperty()

    def __init__(self, parent=None, key_name=None, app=None, _from_entity=False, **kargs):
        if not _from_entity:
            require(kargs, "expertise", "prefer_region", "prefer_zip", "prefer_target", "prefer_field", "prefer_group")
            if "valid_google_acct" not in kargs:
                kargs["valid_google_acct"] = True
            if "hide_cellphone" not in kargs:
                kargs["hide_cellphone"] = False
            if "total_serv_hours" not in kargs:
                kargs["total_serv_hours"] = 0
            if "total_reg_events" not in kargs:
                kargs["total_reg_events"] = 0
            if "total_serv_events" not in kargs:
                kargs["total_serv_events"] = 0
            if "total_sharing" not in kargs:
                kargs["total_sharing"] = 0

        FlowDdlModel.__init__(self, parent, key_name, app, _from_entity, **kargs)

    @classmethod
    def unitTest(cls):
        startUnitTest("VolunteerProfile.unitTest")

        user      = users.User("jane_doe@gmail.com")
        now       = datetime.datetime.utcnow()
        volunteer = VolunteerProfile(volunteer_id=user, id_no="A123456789", volunteer_last_name="Doe", volunteer_first_name="Jane", gmail=user.email(),
                                     date_birth=datetime.date(1970, 2, 1), expertise=["PR"], sex="Female", phone_no="02-1234-5678", resident_country="ROC",
                                     resident_postal="104", resident_state="Taiwan", resident_city="Taipei", resident_district="Shilin",
                                     prefer_region=[], prefer_zip=[], prefer_target=[], prefer_field=[], prefer_group=[],
                                     create_time=now, update_time=now, volunteer_rating=80, status="normal" , search_text=u"測試中文字 test. ngram 屋啦啦 中英文English")

        volunteer.put()
        writeln(volunteer)
        return volunteer

    @classmethod
    def unitTestSearch(cls):
        startUnitTest("VolunteerProfile.unitTestSearch")
        matchList = VolunteerProfile.all().search(VolunteerProfile.search_text, u"測試中文字 屋啦")
        if len(matchList) > 0:
            writeln(matchList[0].search_text[0].encode("UTF-8"))

# end class VolunteerProfile


class QuestionnaireTemplate(FlowDdlModel):
    """
    QUESTIONNAIRE_TEMPLATE
    """
    # Note that although in the schema we have "QUESTIONNAIRE_ID", it is actually implemented as "id" in this class (inherited from FlowDdlModel).
    questions_xml = db.TextProperty(required=True)
    create_time   = db.DateTimeProperty(required=True)
    status        = db.StringProperty(required=True, choices=set(["Draft", "Normal", "Archive", "Cancelled"]))

    @classmethod
    def unitTest(cls):
        startUnitTest("QuestionnaireTemplate.unitTest")

        now      = datetime.datetime.utcnow()
        template = QuestionnaireTemplate(questions_xml="<Question>Howdy</Question>", create_time=now, status="Normal")

        template.put()
        writeln(template)
        return template

# end class QuestionnaireTemplate


class EventProfile(FlowDdlModel):
    """
    EVENT_PROFILE
    """
    event_id                   = db.StringProperty(required=True, validator=vaEventId) # the constraint (UNIQUE) must be enforced by program logic
    event_name                 = db.StringProperty(required=True)
    description                = db.TextProperty(required=True)
    npo_profile_ref            = db.ReferenceProperty(required=True, reference_class=NpoProfile, collection_name="event2npo")
    npo_profile_id             = db.IntegerProperty()         # auto-generated from npo_profile_ref.id
    npo_id                     = db.StringProperty()          # auto-generated from npo_profile_ref.npo_id
    volunteer_profile_ref      = db.ReferenceProperty(required=True, reference_class=VolunteerProfile, collection_name="originator2volunteer")
    volunteer_profile_id       = db.IntegerProperty()         # auto-generated from volunteer_profile_ref.id
    originator                 = db.UserProperty()            # auto-generated from volunteer_profile_ref.volunteer_id
    event_region               = db.StringListProperty()      # required
    event_zip                  = db.StringListProperty()      # required
    event_hours                = db.IntegerProperty()         # default to 0
    event_target               = db.StringListProperty()      # required
    event_field                = db.StringListProperty()      # required
    category                   = db.CategoryProperty(required=True)
    start_time                 = db.DateTimeProperty(required=True)
    end_time                   = db.DateTimeProperty(required=True)
    reg_start_time             = db.DateTimeProperty(required=True)
    reg_end_time               = db.DateTimeProperty(required=True)
    objective                  = db.StringProperty(required=True, multiline=True)
    summary                    = db.StringProperty(multiline=True)
    expense                    = db.IntegerProperty()         # default to 0
    registration_fee           = db.IntegerProperty()         # default to 0
    registered_volunteer       = db.ListProperty(users.User)  # required, must be enforced by program logic
    registered_count           = db.IntegerProperty()         # auto-generated from len(registered_volunteer)
    approved_volunteer         = db.ListProperty(users.User)  # required, must be enforced by program logic
    approved_count             = db.IntegerProperty()         # auto-generated from len(approved_volunteer)
    status                     = db.StringProperty(required=True, choices=set(["new application", "approved", "announced", "authenticating", "authenticated",
                                                                               "registrating", "recruiting", "registration closed", "on-going",
                                                                               "filling polls", "activity closed", "case-closed reporting", "cancelled",
                                                                               "abusive usage"]))
    approved                   = db.BooleanProperty()         # default to False
    approved_time              = db.DateTimeProperty()        # required if approvode is True
    attachment_links           = db.ListProperty(db.Link)
    tag                        = db.StringListProperty()
    max_age                    = db.IntegerProperty(required=True, validator=vaNonnegative) # max_age >= min_age
    min_age                    = db.IntegerProperty(required=True, validator=vaNonnegative) # ditto
    sex                        = db.CategoryProperty(choices=set(["Male", "Female", "Both", "None"])) # default to Both
    female_req                 = db.IntegerProperty()         # default to 0
    male_req                   = db.IntegerProperty()         # default to 0
    volunteer_req              = db.IntegerProperty()         # default to 0
    expertise_req              = db.StringListProperty()
    join_flow_plan             = db.BooleanProperty()         # default to True
    # Note that in the schema we have "QUESTIONNAIRE_ID", but it is more efficient to implement in the following way:
    questionnaire_template_ref = db.ReferenceProperty(required=True, reference_class=QuestionnaireTemplate)
    questionnaire_template_id  = db.IntegerProperty()         # auto-generated from questionnaire_template_ref.id
    sentiments                 = db.StringProperty(multiline=True)
    event_rating               = db.RatingProperty(required=True)
    npo_event_rating           = db.RatingProperty(required=True)
    event_album_link           = db.LinkProperty()
    event_video_link           = db.LinkProperty()
    event_blog_link            = db.LinkProperty()
    create_time                = db.DateTimeProperty(required=True)
    update_time                = db.DateTimeProperty(required=True)

    def __init__(self, parent=None, key_name=None, app=None, _from_entity=False, **kargs):
        if not _from_entity:
            require(kargs, "event_region", "event_zip", "event_target", "event_field", "max_age", "min_age")
            if "approved" not in kargs:
                kargs["approved"] = False
            if kargs["approved"] and ("approved_time" not in kargs):
                raise db.BadValueError("Property approved_time is required if property approved is True")
            if kargs["max_age"] < kargs["min_age"]:
                raise db.BadValueError("Properties max_age and min_age are in wrong order")
            if "event_hours" not in kargs:
                kargs["event_hours"] = 0
            if "expense" not in kargs:
                kargs["expense"] = 0
            if "registration_fee" not in kargs:
                kargs["registration_fee"] = 0
            if "registered_volunteer" in kargs:
                kargs["registered_count"] = len(kargs["registered_volunteer"])
            else:
                kargs["registered_count"] = 0
            if "approved_volunteer" in kargs:
                kargs["approved_count"] = len(kargs["approved_volunteer"])
            else:
                kargs["approved_count"] = 0
            if "sex" not in kargs:
                kargs["sex"] = "Both"
            if "female_req" not in kargs:
                kargs["female_req"] = 0
            if "male_req" not in kargs:
                kargs["male_req"] = 0
            if "volunteer_req" not in kargs:
                kargs["volunteer_req"] = 0
            if "join_flow_plan" not in kargs:
                kargs["join_flow_plan"] = True

        FlowDdlModel.__init__(self, parent, key_name, app, _from_entity, **kargs)

        if not _from_entity:
            self.npo_profile_id            = self.npo_profile_ref.id
            self.npo_id                    = self.npo_profile_ref.npo_id
            self.volunteer_profile_id      = self.volunteer_profile_ref.id
            self.originator                = self.volunteer_profile_ref.volunteer_id
            self.questionnaire_template_id = self.questionnaire_template_ref.id

    @classmethod
    def unitTest(cls, npo, volunteer, template):
        startUnitTest("EventProfile.unitTest")

        now   = datetime.datetime.utcnow()
        event = EventProfile(event_id="2009010199", event_name="Operation Save-Orcas", description="Beach watch?", npo_profile_ref=npo,
                             volunteer_profile_ref=volunteer, event_region=["Taipei"], event_zip=["104"],
                             event_target=["social worker"], event_field=[], category="socializing",
                             start_time=now, end_time=now, reg_start_time=now, reg_end_time=now, objective="Killing time with orcas",
                             status="new application", max_age=99, min_age=9, questionnaire_template_ref=template, event_rating=75, npo_event_rating=80,
                             create_time=now, update_time=now)

        event.put()
        writeln(event)
        return event

# end class EventProfile


class VolunteerEvent(FlowDdlModel):
    """
    VOLUNTEER_EVENT
    """
    volunteer_profile_ref  = db.ReferenceProperty(required=True, reference_class=VolunteerProfile, collection_name="ve2volunteer")
    volunteer_profile_id   = db.IntegerProperty()             # auto-generated from volunteer_profile_ref.id
    event_profile_ref      = db.ReferenceProperty(required=True, reference_class=EventProfile, collection_name="ve2event")
    event_profile_id       = db.IntegerProperty()             # auto-generated from event_profile_ref.id
    volunteer_id           = db.UserProperty()                # auto-generated from volunteer_profile_ref.volunteer_id
    event_id               = db.StringProperty()              # auto-generated from event_profile_ref.event_id
    registered_time        = db.DateTimeProperty(required=True)
    approved_time          = db.DateTimeProperty(required=True)
    sentiments             = db.StringProperty(multiline=True)
    status                 = db.StringProperty(required=True, choices=set(["new registration", "approving", "approved", "approval failed", "involving",
                                                                           "partial involve", "closed", "cancelled", "abusive usage"]))
    event_pic_link         = db.LinkProperty()
    event_video_link       = db.LinkProperty()
    event_blog_link        = db.LinkProperty()
    finished_event_hours   = db.IntegerProperty(required=True, validator=vaNonnegative)
    volunteer_event_rating = db.RatingProperty(required=True) # range=[0..100]
    event_rating           = db.RatingProperty(required=True) # range=[0..100]
    npo_event_rating       = db.RatingProperty(required=True) # range=[0..100]
    cancelled              = db.BooleanProperty()             # default to False
    cancel_date            = db.DateProperty()                # required if cancelled is True
    cancel_reason          = db.StringProperty(multiline=True)

    def __init__(self, parent=None, key_name=None, app=None, _from_entity=False, **kargs):
        if not _from_entity:
            if "cancelled" not in kargs:
                kargs["cancelled"] = False
            if kargs["cancelled"] and "cancel_date" not in kargs:
                raise db.BadValueError("Property cancel_date is required if property cancelled is True")

        FlowDdlModel.__init__(self, parent, key_name, app, _from_entity, **kargs)

        if not _from_entity:
            self.volunteer_profile_id = self.volunteer_profile_ref.id
            self.volunteer_id         = self.volunteer_profile_ref.volunteer_id
            self.event_profile_id     = self.event_profile_ref.id
            self.event_id             = self.event_profile_ref.event_id

    @classmethod
    def unitTest(cls, volunteer, event):
        startUnitTest("VolunteerEvent.unitTest")

        now            = datetime.datetime.utcnow()
        volunteerEvent = VolunteerEvent(volunteer_profile_ref=volunteer, event_profile_ref=event, registered_time=now, approved_time=now,
                                        status="new registration", finished_event_hours=50, volunteer_event_rating=75, event_rating=80,
                                        npo_event_rating=85)

        volunteerEvent.put()
        writeln(volunteerEvent)
        rollBack(volunteerEvent)

# end class VolunteerEvent


class VolunteerEmailBook(FlowDdlModel):
    """
    VOLUNTEER_EMAIL_BOOK
    """
    volunteer_profile_ref = db.ReferenceProperty(required=True, reference_class=VolunteerProfile, collection_name="email_book2volunteer")
    volunteer_profile_id  = db.IntegerProperty() # auto-generated from volunteer_profile_ref.id
    email_group           = db.StringProperty()
    email                 = db.EmailProperty(validator=vaEmail)

    def __init__(self, parent=None, key_name=None, app=None, _from_entity=False, **kargs):
        FlowDdlModel.__init__(self, parent, key_name, app, _from_entity, **kargs)

        if not _from_entity:
            self.volunteer_profile_id = self.volunteer_profile_ref.id

    @classmethod
    def unitTest(cls, volunteer):
        startUnitTest("VolunteerEmailBook.unitTest")

        veb = VolunteerEmailBook(volunteer_profile_ref=volunteer, im_type="MSN", email_group="board", email="johndoe@gmail.com")

        veb.put()
        writeln(veb)
        rollBack(veb)

#end class VolunteerEmailBook


class VolunteerIm(FlowDdlModel):
    """
    VOLUNTEER_IM
    """
    volunteer_profile_ref = db.ReferenceProperty(required=True, reference_class=VolunteerProfile, collection_name="im2volunteer")
    volunteer_profile_id  = db.IntegerProperty() # auto-generated from volunteer_profile_ref.id
    im_type               = db.StringProperty(choices=set(["MSN", "Yahoo Messenger", "Skype", "ICQ", "Other"]))
    im_account            = db.IMProperty()

    def __init__(self, parent=None, key_name=None, app=None, _from_entity=False, **kargs):
        FlowDdlModel.__init__(self, parent, key_name, app, _from_entity, **kargs)

        if not _from_entity:
            self.volunteer_profile_id = self.volunteer_profile_ref.id

    @classmethod
    def unitTest(cls, volunteer):
        startUnitTest("VolunteerIm.unitTest")

        im = VolunteerIm(volunteer_profile_ref=volunteer, im_type="MSN", im_account="http://msn.com/ ahorsewithnoname@yahoo.com")

        im.put()
        writeln(im)
        rollBack(im)

# end class VolunteerIm


class VolunteerLog(FlowDdlModel):
    """
    VOLUNTEER_LOG
    """
    volunteer_profile_ref = db.ReferenceProperty(required=True, reference_class=VolunteerProfile, collection_name="logs2volunteer")
    volunteer_profile_id  = db.IntegerProperty() # auto-generated from volunteer_profile_ref.id
    volunteer_id          = db.UserProperty()    # auto-generated from volunteer_profile_ref.volunteer_id
    signin_datetime       = db.DateTimeProperty(required=True)
    signin_ip             = db.StringProperty(required=True, validator=vaIP)
    signoff_datetime      = db.DateTimeProperty(required=True)

    def __init__(self, parent=None, key_name=None, app=None, _from_entity=False, **kargs):
        FlowDdlModel.__init__(self, parent, key_name, app, _from_entity, **kargs)

        if not _from_entity:
            self.volunteer_profile_id = self.volunteer_profile_ref.id
            self.volunteer_id         = self.volunteer_profile_ref.volunteer_id

    @classmethod
    def unitTest(cls, volunteer):
        startUnitTest("VolunteerLog.unitTest")

        now = datetime.datetime.utcnow()
        log = VolunteerLog(volunteer_profile_ref=volunteer, signin_datetime=now, signin_ip="127.0.0.1", signoff_datetime=now)

        log.put()
        writeln(log)
        rollBack(log)

# end class VolunteerLog


class EventNews(FlowDdlModel):
    """
    EVENT_NEWS
    """
    event_profile_ref = db.ReferenceProperty(required=True, reference_class=EventProfile, collection_name="news2event")
    event_profile_id  = db.IntegerProperty() # auto-generated from event_profile_ref.id
    event_id          = db.StringProperty()  # auto-generated from event_profile_ref.event_id
    create_date       = db.DateTimeProperty(required=True)
    news              = db.TextProperty(required=True)

    def __init__(self, parent=None, key_name=None, app=None, _from_entity=False, **kargs):
        FlowDdlModel.__init__(self, parent, key_name, app, _from_entity, **kargs)

        if not _from_entity:
            self.event_profile_id = self.event_profile_ref.id
            self.event_id         = self.event_profile_ref.event_id

    @classmethod
    def unitTest(cls, event):
        startUnitTest("EventNews.unitTest")

        now  = datetime.datetime.utcnow()
        news = EventNews(event_profile_ref=event, create_date=now, news="This just in!")

        news.put()
        writeln(news)
        rollBack(news)

# end class EventNews


class EventQuestion(FlowDdlModel):
    """
    EVENT_QUESTION
    """
    event_profile_ref     = db.ReferenceProperty(required=True, reference_class=EventProfile, collection_name="q_a2event")
    event_profile_id      = db.IntegerProperty() # auto-generated from event_profile_ref.id
    event_id              = db.StringProperty()  # auto-generated from event_profile_ref.event_id
    volunteer_profile_ref = db.ReferenceProperty(required=True, reference_class=VolunteerProfile, collection_name="questioners2volunteer")
    volunteer_profile_id  = db.IntegerProperty() # auto-generated from volunteer_profile_ref.id
    questioner            = db.UserProperty()    # auto-generated from volunteer_profile_ref.volunteer_id
    title                 = db.StringProperty(required=True)
    content               = db.StringProperty(required=True, multiline=True)
    create_time           = db.DateTimeProperty(required=True)
    update_time           = db.DateTimeProperty(required=True)
    ip                    = db.StringProperty(required=True, validator=vaIP)

    def __init__(self, parent=None, key_name=None, app=None, _from_entity=False, **kargs):
        FlowDdlModel.__init__(self, parent, key_name, app, _from_entity, **kargs)

        if not _from_entity:
            self.event_profile_id     = self.event_profile_ref.id
            self.event_id             = self.event_profile_ref.event_id
            self.volunteer_profile_id = self.volunteer_profile_ref.id
            self.questioner           = self.volunteer_profile_ref.volunteer_id

    @classmethod
    def unitTest(cls, volunteer, event):
        startUnitTest("EventQuestion.unitTest")

        now      = datetime.datetime.utcnow()
        question = EventQuestion(event_profile_ref=event, volunteer_profile_ref=volunteer, title="Smalltalk", content="How's your life?", create_time=now,
                                 update_time=now, ip="127.0.0.1")

        question.put()
        writeln(question)
        return question

# end class EventQuestion


class EventAnswer(FlowDdlModel):
    """
    EVENT_ANSWER
    """
    event_question_ref    = db.ReferenceProperty(required=True, reference_class=EventQuestion, collection_name="answers2eventquestion")
    event_question_id     = db.IntegerProperty() # auto-generated from event_question_ref.id
    volunteer_profile_ref = db.ReferenceProperty(required=True, reference_class=VolunteerProfile, collection_name="answerers2volunteer")
    volunteer_profile_id  = db.IntegerProperty() # auto-generated from volunteer_profile_ref.id
    volunteer_id          = db.UserProperty()    # auto-generated from volunteer_profile_ref.volunteer_id
    title                 = db.StringProperty(required=True)
    content               = db.StringProperty(required=True, multiline=True)
    create_time           = db.DateTimeProperty(required=True)
    update_time           = db.DateTimeProperty(required=True)
    ip                    = db.StringProperty(validator=vaIP)

    def __init__(self, parent=None, key_name=None, app=None, _from_entity=False, **kargs):
        FlowDdlModel.__init__(self, parent, key_name, app, _from_entity, **kargs)

        if not _from_entity:
            self.event_question_id    = self.event_question_ref.id
            self.volunteer_profile_id = self.volunteer_profile_ref.id
            self.volunteer_id         = self.volunteer_profile_ref.volunteer_id

    @classmethod
    def unitTest(cls, volunteer, question):
        startUnitTest("EventAnswer.unitTest")

        now    = datetime.datetime.utcnow()
        answer = EventAnswer(event_question_ref=question, volunteer_profile_ref=volunteer, title="My Answer", content="dunno", create_time=now,
                             update_time=now, ip="127.0.0.1")

        answer.put()
        writeln(answer)
        rollBack(answer)

# end class EventAnswer


class EventQuestionnaire(FlowDdlModel):
    """
    EVENT_QUESTIONNAIRE
    """
    event_profile_ref          = db.ReferenceProperty(required=True, reference_class=EventProfile, collection_name="questionnaires2event")
    event_profile_id           = db.IntegerProperty() # auto-generated from event_profile_ref.id
    event_id                   = db.StringProperty()  # auto-generated from event_profile_ref.event_id
    questionnaire_template_ref = db.ReferenceProperty(required=True, reference_class=QuestionnaireTemplate, collection_name="answers2qtemplate")
    questionnaire_template_id  = db.IntegerProperty() # auto-generated from questionnaire_template_ref.id
    volunteer_profile_ref      = db.ReferenceProperty(required=True, reference_class=VolunteerProfile, collection_name="respondents2volunteer")
    volunteer_profile_id       = db.IntegerProperty() # auto-generated from volunteer_profile_ref.id
    respondent                 = db.UserProperty()    # auto-generated from volunteer_profile_ref.volunteer_id
    answers_xml                = db.TextProperty(required=True)
    create_time                = db.DateTimeProperty(required=True)
    ip                         = db.StringProperty(required=True, validator=vaIP)

    def __init__(self, parent=None, key_name=None, app=None, _from_entity=False, **kargs):
        FlowDdlModel.__init__(self, parent, key_name, app, _from_entity, **kargs)

        if not _from_entity:
            self.event_profile_id          = self.event_profile_ref.id
            self.event_id                  = self.event_profile_ref.event_id
            self.questionnaire_template_id = self.questionnaire_template_ref.id
            self.volunteer_profile_id      = self.volunteer_profile_ref.id
            self.respondent                = self.volunteer_profile_ref.volunteer_id

    @classmethod
    def unitTest(cls, volunteer, event, template):
        startUnitTest("EventQuestionnaire.unitTest")

        now           = datetime.datetime.utcnow()
        questionnaire = EventQuestionnaire(event_profile_ref=event, questionnaire_template_ref=template, volunteer_profile_ref=volunteer,
                                           answers_xml="<Answer>Like it!</Answer>", create_time=now, ip="127.0.0.1")
        questionnaire.put()
        writeln(questionnaire)
        rollBack(questionnaire)

# end class EventQuestionnaire


class ReportTemplate(FlowDdlModel):
    """
    REPORT_TEMPLATE
    """
    # Note that although we have "REPORT_ID" in the schema, it is actually implemented as "id" whcih is inherited from FlowDdlModel.
    questions_xml = db.TextProperty(required=True)
    create_time   = db.DateTimeProperty(required=True)
    status        = db.StringProperty(required=True, choices=set(["Draft", "Normal", "Archive", "Cancelled"]))

    @classmethod
    def unitTest(cls):
        startUnitTest("ReportTemplate.unitTest")

        now      = datetime.datetime.utcnow()
        template = ReportTemplate(questions_xml="<FooBar>Baracuda</FooBar>", create_time=now, status="Normal")

        template.put()
        writeln(template)
        return template

# end class ReportTemplate


class EventReport(FlowDdlModel):
    """
    EVENT_REPORT
    """
    event_profile_ref     = db.ReferenceProperty(required=True, reference_class=EventProfile, collection_name="reports2event")
    event_profile_id      = db.IntegerProperty() # auto-generated from event_profile_ref.id
    event_id              = db.StringProperty()  # auto-generated from event_profile_ref.event_id
    report_template_ref   = db.ReferenceProperty(required=True, reference_class=ReportTemplate, collection_name="answers2reporttemplate")
    # Note that although we have "REPORT_ID" in the schema, it is actually implemented as "report_template_id" here to follow our coding convention.
    report_template_id    = db.IntegerProperty() # auto-generated from report_template_ref.id
    volunteer_profile_ref = db.ReferenceProperty(required=True, reference_class=VolunteerProfile, collection_name="reporters2volunteer")
    volunteer_profile_id  = db.IntegerProperty() # auto-generated from volunteer_profile_ref.id
    reporter              = db.UserProperty()    # auto-generated from volunteer_profile_ref.volunteer_id
    answers_xml           = db.TextProperty(required=True)
    create_time           = db.DateTimeProperty(required=True)
    ip                    = db.StringProperty(required=True, validator=vaIP)

    def __init__(self, parent=None, key_name=None, app=None, _from_entity=False, **kargs):
        FlowDdlModel.__init__(self, parent, key_name, app, _from_entity, **kargs)

        if not _from_entity:
            self.event_profile_id     = self.event_profile_ref.id
            self.event_id             = self.event_profile_ref.event_id
            self.report_template_id   = self.report_template_ref.id
            self.volunteer_profile_id = self.volunteer_profile_ref.id
            self.reporter             = self.volunteer_profile_ref.volunteer_id

    @classmethod
    def unitTest(cls, volunteer, event, template):
        startUnitTest("EventReport.unitTest")

        now    = datetime.datetime.utcnow()
        report = EventReport(event_profile_ref=event, report_template_ref=template, volunteer_profile_ref=volunteer, answers_xml="<Answer>Dunno!</Answer>",
                             create_time=now, ip="127.0.0.1")

        report.put()
        writeln(report)
        rollBack(report)

# end class EventReport


class ImproperReport(FlowDdlModel):
    """
    IMPROPER_REPORT
    """
    report_time = db.DateTimeProperty(required=True)
    reporter    = db.UserProperty(required=True)
    webpage     = db.LinkProperty(required=True)
    field       = db.StringProperty(required=True)
    content     = db.StringProperty(required=True, multiline=True)
    comments    = db.StringProperty(multiline=True)
    report_type = db.CategoryProperty(required=True)
    status      = db.StringProperty(required=True, choices=set(["New Report", "Processing", "Closed"]))
    ip          = db.StringProperty(required=True, validator=vaIP)

    @classmethod
    def unitTest(cls, user):
        startUnitTest("ImproperReport.unitTest")

        now    = datetime.datetime.utcnow()
        report = ImproperReport(report_time=now, reporter=user, webpage="http://www.HotSexyBabe.com/", field="porno", content="porno",
                                report_type="abusive", status="New Report", ip="127.0.0.1")

        report.put()
        writeln(report)
        rollBack(report)

# end class ImproperReport


class CountryCity(FlowDdlModel):
    """
    COUNTRY_CITY
    """
    country_tc = db.StringProperty(required=True)
    country_en = db.StringProperty(required=True)
    state_tc   = db.StringProperty(required=True)
    state_en   = db.StringProperty(required=True)
    city_tc    = db.StringProperty(required=True)
    city_en    = db.StringProperty(required=True)
    zip_code   = db.StringProperty(required=True)

    @classmethod
    def unitTest(cls):
        startUnitTest("CountryCity.unitTest")

        countryCity = CountryCity(country_tc="??", country_en="ROC", state_tc="??", state_en="Taiwan", city_tc="??", city_en="Taipei", zip_code="104")

        countryCity.put()
        writeln(countryCity)
        rollBack(countryCity)

# end class CountryCity


class Target(FlowDdlModel):
    """
    TARGET
    """
    name = db.StringProperty(required=True)

    @classmethod
    def unitTest(cls):
        startUnitTest("Target.unitTest")

        target=Target(name="John Doe")

        target.put()
        writeln(target)
        rollBack(target)

# end class Target


class Field(FlowDdlModel):
    """
    FIELD
    """
    name = db.StringProperty(required=True)

    @classmethod
    def unitTest(cls):
        startUnitTest("Field.unitTest")

        field=Field(name="Social works")

        field.put()
        writeln(field)
        rollBack(field)

# end class Field


"""
#----------------------------------------------------------
# Unit-test Section.
#----------------------------------------------------------
"""

# tester[0]: The output handle.
# tester[1]: Each unit-test routine should assign its name to this so that error report can show it.
tester = []

def startUnitTest(name):
    tester[1] = name
    writeln()
    writeln('<UnitTestClass name="', name, '" />')

def rollBack(data):
    count = db.Query(data.__class__).count()
    db.delete(data)
    if db.Query(data.__class__).count() != count - 1:
        raise IOError

def rollBackFor(data, testName):
    tester[1] = testName
    rollBack(data)

def writeln(*args):
    for arg in args:
        if arg.__class__ == tuple:
            separator = ""
            for item in arg:
                tester[0].response.out.write(separator + str(item))
                separator = "; "
        else:
            tester[0].response.out.write(str(arg))
    tester[0].response.out.write("\n")

class DDL_UnitTest(webapp.RequestHandler):
    def get(self):
        self.response.headers["Content-Type"] = "text/xml"
        tester.append(self)
        tester.append("")

        try:
            writeln('<?xml version="1.0"?>')
            writeln("<UnitTest>")

            npo            = NpoProfile.unitTest()
            volunteer      = VolunteerProfile.unitTest()
            template       = QuestionnaireTemplate.unitTest()
            event          = EventProfile.unitTest(npo, volunteer, template)
            question       = EventQuestion.unitTest(volunteer, event)
            reportTemplate = ReportTemplate.unitTest()
            NpoNews.unitTest(npo)
            NpoEmail.unitTest(npo)
            NpoContact.unitTest(npo)
            NpoPhone.unitTest(npo)
            NpoAdmin.unitTest(npo)
            VolunteerEvent.unitTest(volunteer, event)
            VolunteerEmailBook.unitTest(volunteer)
            VolunteerIm.unitTest(volunteer)
            VolunteerLog.unitTest(volunteer)
            EventNews.unitTest(event)
            EventAnswer.unitTest(volunteer, question)
            EventQuestionnaire.unitTest(volunteer, event, template)
            EventReport.unitTest(volunteer, event, reportTemplate)
            ImproperReport.unitTest(volunteer.volunteer_id)
            CountryCity.unitTest()
            Target.unitTest()
            Field.unitTest()
            VolunteerProfile.unitTestSearch()

            rollBackFor(reportTemplate, "ReportTemplate.unitTest")
            rollBackFor(question, "EventQuestion.unitTest")
            rollBackFor(event, "EventProfile.unitTest")
            rollBackFor(template, "QuestionnaireTemplate.unitTest")
            rollBackFor(volunteer, "VolunteerProfile.unitTest")
            rollBackFor(npo, "NpoProfile.unitTest")
        except:
            writeln("<UnitTestFailure>!!! ", cgi.escape(tester[1]), ": ", cgi.escape(str(sys.exc_info())), "</UnitTestFailure>")
        finally:
            writeln()
            writeln("</UnitTest>")

# Show the unit-test page. This is executed only when we test the module alone.
if __name__ == "__main__":
    run_wsgi_app(webapp.WSGIApplication([("/", DDL_UnitTest)], debug=True))

