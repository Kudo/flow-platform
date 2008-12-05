#!/usr/bin/env python
# -*- coding: utf-8 -*-

# First edition: 2008/11/07, Tony Chu
# Revised: 2008/11/18, Kudo Chien

import sys
import datetime
import checker
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users

__all__ = ["counter", "Keyword", "ArchiveInfo", "EventLogging",
           "Authentication", "Npo", "Individual", "Activity", "RecruitingSpec",
           "NpoActivityIndividual", "Rating", "External", "Guestbook",
           "QuestionaireTemplate", "Questionaire"]

"""
#----------------------------------------------------------
# The DDL (Data Definition Language) of Flow Platform
#
# Each property name of a entity class (such as "authority" in class
# "Authentication") is simply named as such, without the Hugarian notation
# prefix (such as "strAuthority"). It is *PURPOSELY* designed in this way
# so that the following GQL query is possible:
#
#    result = db.GqlQuery(
#        "SELECT * FROM Authentication WHERE authority = :1", "GOOGLE")
# or:
#    result = Authentication.gql("WHERE authority = :1", "GOOGLE")
# 
#----------------------------------------------------------
"""

class FlowDdlModel(db.Model):
    """
    All DDL entity classes must inherit from this class so as to make use of
    our special version of __str__() method, which tries to generate the
    serializable XML format.
    """

    def __str__(self):
        ret = ["<", self.__class__.__name__, ' key="', str(self.key()), '"']
        children = []
        for member in dir(self):
            if not callable(getattr(self, member)) and member[0] != "_" and not member.endswith("_set"):
                ret.append(" " + member + "=")
                value = getattr(self, member)
                if member.endswith("ref"):
                    if value:
                        ret.append('"' + str(value.key()) + '"')
                        if member != "back_ref":
                            # The "back_ref" is a reference from a child node to parent.
                            # We must avoid adding it to the "children" list or else the
                            # result would be an infinite recursion.
                            children.append(str(value))
                    else:
                        ret.append('"None"')
                else:
                    ret.append('"' + str(value).replace('"', '&quot;') + '"')
        if children == []:
            ret.append(" />")
        else:
            ret.append(">\n")
            ret.append("\n".join(children) + "\n")
            ret.append("</" + self.__class__.__name__ + ">")
        return "".join(ret)
  

# end class FlowDdlModel


class Counter(FlowDdlModel):
    """
    The counter singleton class.
    This class has been revised so that each entity class can have its own
    unique counter, thanks to Kudo Chien's idea.
    """
    className = db.StringProperty(required=True)
    counter = db.IntegerProperty(required=True)

    @staticmethod
    def init(classObj):
        """
        Start a new counter singleton. User should not directly call this method.
        """
        ctr = Counter(className=classObj.__name__, counter=0)
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
    def next(classObj):
        """
        Obtain the next available counter (started from 0). Sample usage:
            Counter.next(ClassName)
        """
        acc = Counter.gql("WHERE className=:1", classObj.__name__).get()
        if acc == None:
            return db.run_in_transaction(Counter.init, classObj)
        else:
            return db.run_in_transaction(Counter.increment, acc.key())

    def __getitem__(self, classObj):
        """
        The purpose of this method is to support the following syntatical sugar:
            counter[ClassName]
        which is slightly more readable (and less typing effort) than this:
            Counter.next(ClassName)
        """
        return Counter.next(classObj)

counter = Counter(className="Counter", counter=0)

# end class Counter


class Keyword(FlowDdlModel):
    id = db.IntegerProperty(required=True)
    keyword = db.StringProperty(required=True)
    category = db.StringProperty(required=True, choices=set(["EXPERTISE","ACTIVITY","SERVICE_TARGET"]))
    reference_count = db.IntegerProperty(required=True)

    def __init__(self, parent=None, key_name=None, app=None, **kargs):
        if "reference_count" not in kargs:
            kargs["reference_count"] = 1
        FlowDdlModel.__init__(self, parent, key_name, app, **kargs)

    @staticmethod
    def UnitTest():
        try:
            writeln("*** Keyword.UnitTest")

            kw = Keyword(
                id=counter[Keyword], keyword="sample", category="EXPERTISE")
            kw.put()
            writeln("kw=", kw)

            count = db.Query(Keyword).count()
            db.delete(kw)
            if db.Query(Keyword).count() != count - 1: raise IOError
        except:
            writeln("!!! Keyword.UnitTest failed: ", sys.exc_info())
        finally:
            writeln()

# end class Keyword


class ArchiveInfo(FlowDdlModel):
    id = db.IntegerProperty(required=True)
    date_archive = db.DateProperty(required=True)
    date_begin = db.DateProperty()
    date_end = db.DateProperty(required=True)
    # 0: SINGLE INCIDENT 1: TO_DATE_INFO 2:PERIOD_INFO
    attribute = db.IntegerProperty(required=True, choices=set([0,1,2]))
    # 0: Activity, 1: IDV Service Record, 2: Consolidate Rating
    type = db.IntegerProperty(required=True, choices=set([0,1,2]))
    context = db.TextProperty(required=True)

    @staticmethod
    def UnitTest():
        try:
            writeln("*** ArchiveInfo.UnitTest")

            arc = ArchiveInfo(
                id=counter[ArchiveInfo],
                date_archive=datetime.date(2000, 1, 1),
                date_end=datetime.date(2000, 1, 1), attribute=0, type=0,
                context="whatever")
            arc.put()
            writeln("arc=", arc)

            count = db.Query(ArchiveInfo).count()
            db.delete(arc)
            if db.Query(ArchiveInfo).count() != count - 1: raise IOError
        except:
            writeln("!!! ArchiveInfo.UnitTest failed: ", sys.exc_info())
        finally:
            writeln()

# end class ArchiveInfo


class EventLogging(FlowDdlModel):
    id = db.IntegerProperty(required=True)
    # 0: OBJECT_CREATION, 1: OBJECT_DELETION, 2: SYSTEM_GENERAL_LOGGING, 3: SYSTEM_SECURITY_LOGGING, 4: SYSTEM_DEBUG_LOGGING
    type = db.IntegerProperty(required=True, choices=set([0,1,2,3,4]))
    # 0:INFORMATIONAL, 2: WARNING, 3: ERROR
    attribute = db.IntegerProperty(required=True, choices=set([0,2,3]))
    object = db.IntegerProperty(required=True)
    subject = db.IntegerProperty(required=True)
    incident = db.TextProperty(required=True)

    @staticmethod
    def UnitTest():
        try:
            writeln("*** EventLogging.UnitTest")

            log = EventLogging(
                id=counter[EventLogging],
                type=0, attribute=0, object=0, subject=0,
                incident="something's wrong")
            log.put()
            writeln("log=", log)

            count = db.Query(EventLogging).count()
            db.delete(log)
            if db.Query(EventLogging).count() != count - 1: raise IOError
        except:
            writeln("!!! EventLogging.UnitTest failed: ", sys.exc_info())
        finally:
            writeln()

# end class EventLogging


class Ratee(FlowDdlModel):
    """
    The superclass of Npo, Individual, and Activity.
    This is the interfacce class for whatever can be rated.
    """
    pass


class Rater(Ratee):
    """
    The superclass of Npo and Individual.
    This class is declared so that we can have a
        back_ref = db.ReferenceProperty(reference_class=Rater)
    definition in the Autentication entity class. This also serves as an
    interface class of the ones who can rate others.
    """
    pass


# TODO: Administrator is not yet implemented because the schema is vague about it.

class Authentication(FlowDdlModel):
    id = db.IntegerProperty(required=True, validator=checker.Authentication.checkId)
    back_ref = db.ReferenceProperty(reference_class=Rater)
    back_id = db.IntegerProperty()
    authority = db.StringProperty(required=True, multiline=False, choices=set(["GOOGLE"]))
    context = db.UserProperty(required=True)
    # 1: Npo, 2: Individual, 999: Administrator
    role = db.IntegerProperty(required=True, choices=set([1, 2, 999]))
    validated = db.BooleanProperty(required=True)

    def __init__(self, parent=None, key_name=None, app=None, **kargs):
        if "authority" not in kargs:
            kargs["authority"] = "GOOGLE"
        if "validated" not in kargs:
            kargs["validated"] = True
        FlowDdlModel.__init__(self, parent, key_name, app, **kargs)

    def resolve(self):
        """
        A handy method to resolve myself to an Npo or Individual entity.
        Returns None if this Authentication entity has not been bound to
        any entity.
        """
        if self.role == 1:
            return Npo.gql("WHERE auth_ref=:1", self).get()
        elif self.role == 2:
            return Individual.gql("WHERE auth_ref=:1", self).get()
        else:
            # try our best to locate it
            x = Npo.gql("WHERE auth_ref=:1", self).get()
            if x != None: return x
            return Individual.gql("WHERE auth_ref=:1", self).get()

    @staticmethod
    def UnitTest():
        try:
            writeln("*** Authentication.UnitTest")

            user = users.User("dummy_account@gmail.com")
            auth = Authentication(
                id=counter[Authentication],
                context=user, role=2)
            auth.put()
            writeln("auth=", auth)

            count = db.Query(Authentication).count()
            db.delete(auth)
            if db.Query(Authentication).count() != count - 1: raise IOError
        except:
            writeln("!!! Authentication.UnitTest failed: ", sys.exc_info())
        finally:
            writeln()

# end class Authentication


class Npo(Rater):
    id = db.IntegerProperty(required=True)
    auth_ref = db.ReferenceProperty(required=True, reference_class=Authentication)
    auth_id = db.IntegerProperty(required=True)
    time_creation = db.DateTimeProperty(required=True)
    time_modification = db.DateTimeProperty(required=True)
    name = db.StringProperty(required=True, multiline=False)
    founder = db.StringProperty(required=True, multiline=False)
    objectives = db.TextProperty(required=True)
    contact = db.EmailProperty(required=True)
    website = db.LinkProperty(required=True)
    phone = db.PhoneNumberProperty(required=True)
    fax = db.PhoneNumberProperty(required=True)
    date_founding = db.DateProperty()
    authority = db.StringProperty(multiline=False)
    service_area = db.StringProperty(multiline=False)
    service_target = db.StringProperty(multiline=False)
    service_item = db.StringProperty(multiline=False)
    bank_account_number = db.StringProperty(multiline=False)
    bank_account_name = db.StringProperty(multiline=False)

    def __init__(self, user=None, parent=None, key_name=None, app=None, **kargs):
        if user == None:
            # The original way... The Authentication entity should be constructed
            # separately and keywords "auth_ref" & "auth_id" should be
            # assigned explicitly.
            Rater.__init__(self, parent, key_name, app, **kargs)
        else:
            # The new way... Only the "user=..." is needed.
            auth = Authentication(
                id=counter[Authentication],
                context=user, role=1)
            try:
                kargs["auth_ref"] = auth.put()
                kargs["auth_id"] = auth.id
                Rater.__init__(self, parent, key_name, app, **kargs)
            except Exception, e:
                auth.delete()
                raise Exception, e

    def put(self):
        """
        This method is here because we need to also update the Authentication
        entity associated with this Npo.
        """
        # Authentication entity back references to me
        k = Rater.put(self)
        self.auth_ref.back_ref = k
        self.auth_ref.back_id = self.id
        # make sure Authentication entity has the correct role
        if self.auth_ref.role != 1:
            self.auth_ref.role = 1
        # update the Authentication entity
        self.auth_ref.put()
        # return the key where put() generally should do
        return k

    @staticmethod
    def UnitTest():
        try:
            writeln("*** Npo.UnitTest")

            user = user=users.User("green_peace@gmail.com")
            now = datetime.datetime.utcnow()
            npo = Npo(
                id=counter[Npo],
                user=user, time_creation=now, time_modification=now,
                name="Green Peace", founder="Jim Bohlen",
                objectives="environment protection",
                contact=user.email(), website="http://www.greenpeace.org/",
                phone="12345678", fax="12345678")
            npo.put()

            writeln("npo=", npo)
            return npo
        except:
            writeln("!!! Npo.UnitTest failed: ", sys.exc_info())
        finally:
            writeln()

    @staticmethod
    def RollBack(npo):
        try:
            contact = npo.contact
            auth = npo.auth_ref
            user = auth.context
            db.delete(npo)
            for x in Npo.gql("WHERE contact=:1", contact):
                writeln("Npo.contact=", x.contact, " is not deleted")
                raise IOError
            db.delete(auth)
            for x in Authentication.gql("WHERE context=:1", user):
                writeln("Authentication.context=", x.context, " is not deleted")
                raise IOError
        except:
            writeln("!!! Npo.RollBack failed: ", sys.exc_info())

# end class Npo


class Individual(Rater):
    id = db.IntegerProperty(required=True)
    auth_ref = db.ReferenceProperty(required=True, reference_class=Authentication)
    auth_id = db.IntegerProperty(required=True)
    time_creation = db.DateTimeProperty(required=True)
    time_modification = db.DateTimeProperty(required=True)
    name = db.StringProperty(required=True, multiline=False)
    date_birth = db.DateProperty(required=True, validator=checker.Individual.checkBirth)
    # 1: FEMALE, 2: MALE
    gender = db.IntegerProperty(required=True, choices=set([1, 2]))
    resident_city = db.PostalAddressProperty()
    organization = db.TextProperty()
    email = db.EmailProperty(required=True, validator=checker.Individual.checkEmail)
    instant_message = db.IMProperty()
    cell_phone = db.PhoneNumberProperty(validator=checker.Individual.checkPhone)
    blog = db.LinkProperty()
    expertise = db.CategoryProperty(required=True)
    total_service_hour = db.IntegerProperty()
    total_service_count = db.IntegerProperty()
    total_service_presence_count = db.IntegerProperty()
    medal = db.IntegerProperty()
    concerned_issue = db.TextProperty()
    personal_quote = db.TextProperty()
    # 1 ... 10
    user_rating = db.IntegerProperty(required=True, choices=set(range(1, 11)))

    def __init__(self, user=None, parent=None, key_name=None, app=None, **kargs):
        if user == None:
            # The original way... The Authentication entity should be constructed
            # separately and keywords "auth_ref" & "auth_id" should be
            # assigned explicitly.
            Rater.__init__(self, parent, key_name, app, **kargs)
        else:
            # The new way... Only the "user=..." is needed.
            auth = Authentication(
                id=counter[Authentication],
                context=user, role=2)
            try:
                kargs["auth_ref"] = auth.put()
                kargs["auth_id"] = auth.id
                Rater.__init__(self, parent, key_name, app, **kargs)
            except Exception, e:
                auth.delete()
                raise Exception, e

    def put(self):
        """
        This method is here because we need to also update the Authentication
        entity associated with this Individual.
        """
        # Authentication entity back references to me
        k = Rater.put(self)
        self.auth_ref.back_ref = k
        self.auth_ref.back_id = self.id
        # make sure Authentication entity has the correct role
        if self.auth_ref.role != 2:
            self.auth_ref.role = 2
        # update the Authentication entity
        self.auth_ref.put()
        # return the key where put() generally should do
        return k

    @staticmethod
    def UnitTest():
        try:
            writeln("*** Individual.UnitTest")

            user = users.User("john_doe@gmail.com")
            now = datetime.datetime.utcnow()
            ind = Individual(
                id=counter[Individual],
                user=user, time_creation=now, time_modification=now,
                name="John Doe", date_birth=datetime.date(1980, 1, 1),
                gender=2, email=user.email(), expertise="computer",
                user_rating=1)
            ind.put()

            writeln("ind=", ind)
            return ind
        except:
            writeln("!!! Individual.UnitTest failed: ", sys.exc_info())
        finally:
            writeln()

    @staticmethod
    def RollBack(ind):
        try:
            email = ind.email
            auth = ind.auth_ref
            user = auth.context
            db.delete(ind)
            for x in Individual.gql("WHERE email=:1", email):
                writeln("Individual.email=", x.email, " is not deleted")
                raise IOError
            db.delete(auth)
            for x in Authentication.gql("WHERE context=:1", user):
                writeln("Authentication.context=", x.context, " is not deleted")
                raise IOError
        except:
            writeln("!!! Individual.RollBack failed: ", sys.exc_info())

# end class Individual


class Activity(Ratee):
    id = db.IntegerProperty(required=True)
    owner_ref = db.ReferenceProperty(required=True, reference_class=Npo)
    owner_id = db.IntegerProperty(required=True)
    time_creation = db.DateTimeProperty(required=True)
    time_modification = db.DateTimeProperty(required=True)
    originator = db.StringProperty(required=True, multiline=False)
    name = db.StringProperty(required=True, multiline=False)
    category = db.StringProperty(required=True, multiline=False)
    time_begin = db.DateTimeProperty(required=True)
    time_end = db.DateTimeProperty(required=True)
    location = db.PostalAddressProperty(required=True)
    # service_hour > 0
    service_hour = db.IntegerProperty(required=True)
    service_target = db.StringProperty(required=True, multiline=False)
    tag = db.CategoryProperty(required=True)
    objectives = db.StringProperty(required=True)
    summary = db.TextProperty(required=True)
    expense = db.IntegerProperty()
    sign_up_fee = db.IntegerProperty()
    status = db.StringProperty(required=True, choices=set(["EDITING","RECRUITING","CLOSED","CANCELED"]))
    sticker = db.StringProperty(required=True)
    latest_information = db.StringProperty(required=True)
    urls_video = db.StringListProperty()
    urls_pictures = db.StringListProperty()
    faq = db.TextProperty()
    urls_attachment = db.StringListProperty()
    # 1 ... 10
    rating = db.IntegerProperty(required=True, choices=set(range(1, 11)))

    def __init__(self, parent=None, key_name=None, app=None, **kargs):
        if kargs["service_hour"] <= 0:
            raise db.BadValueError("service_hour=%s" % kargs["service_hour"])
        Ratee.__init__(self, parent, key_name, app, **kargs)

    @staticmethod
    def UnitTest():
        try:
            writeln("*** Activity.UnitTest")

            now = datetime.datetime.utcnow()
            # use any Npo entity
            npo = db.Query(Npo).get()

            act = Activity(
                id=counter[Activity],
                owner_ref=npo, owner_id=npo.id,
                time_creation=now, time_modification=now,
                originator="someone", name="save the world",
                category="voluntary", time_begin=now, time_end=now,
                location="Taipei", service_hour=1, service_target="netizens",
                tag="internet", objectives="fight against crimes",
                summary="to be discussed", status="EDITING", sticker="stuck",
                latest_information="this just in", rating=1)
            act.put()

            writeln("act=", act)
            return act
        except:
            writeln("!!! Activity.UnitTest failed: ", sys.exc_info())
        finally:
            writeln()

    @staticmethod
    def RollBack(act):
        try:
            count = db.Query(Activity).count()
            db.delete(act)
            if db.Query(Activity).count() != count - 1: raise IOError
        except:
            writeln("!!! Activity.RollBack failed: ", sys.exc_info())

# end class Activity


class RecruitingSpec(FlowDdlModel):
    id = db.IntegerProperty(required=True)
    activity_ref = db.ReferenceProperty(required=True, reference_class=Activity)
    activity_id = db.IntegerProperty(required=True)
    # age_min <= age_max AND age_max >= 0
    age_max = db.IntegerProperty(required=True)
    # age_min <= age_max AND age_min >= 0
    age_min = db.IntegerProperty(required=True)
    # 0: not specified, 1: FEMALE, 2: MALE
    gender = db.IntegerProperty(required=True, choices=([0, 1, 2]))
    # head_count_required > 0
    head_count_required = db.IntegerProperty(required=True)
    expertise_required = db.CategoryProperty(required=True)

    def __init__(self, parent=None, key_name=None, app=None, **kargs):
        if kargs["age_max"] < 0:
            raise db.BadValueError("age_max=%s" % kargs["age_max"])
        if kargs["age_min"] < 0:
            raise db.BadValueError("age_min=%s" % kargs["age_min"])
        if kargs["age_min"] > kargs["age_max"]:
            raise db.BadValueError("age_min=%s, age_max=%s" % (kargs["age_min"], kargs["age_max"]))
        if kargs["head_count_required"] <= 0:
            raise db.BadValueError("head_count_required=%s" % kargs["head_count_required"])
        FlowDdlModel.__init__(self, parent, key_name, app, **kargs)

    @staticmethod
    def UnitTest():
        try:
            writeln("*** RecruitingSpec.UnitTest")

            # use any Activity entity
            act = db.Query(Activity).get()

            rec = RecruitingSpec(
                id=counter[RecruitingSpec],
                activity_ref=act, activity_id=act.id,
                age_max=99, age_min=9, gender=0,
                head_count_required=1, expertise_required="computer")
            rec.put()

            writeln("rec=", rec)
            return rec
        except:
            writeln("!!! RecruitingSpec.UnitTest failed: ", sys.exc_info())
        finally:
            writeln()

    @staticmethod
    def RollBack(rec):
        try:
            count = db.Query(RecruitingSpec).count()
            db.delete(rec)
            if db.Query(RecruitingSpec).count() != count - 1: raise IOError
        except:
            writeln("!!! RecruitingSpec.RollBack failed: ", sys.exc_info())

# end class RecruitingSpec


class NpoActivityIndividual(FlowDdlModel):
    id = db.IntegerProperty(required=True)
    npo_ref = db.ReferenceProperty(required=True, reference_class=Npo)
    npo_id = db.IntegerProperty(required=True)
    activity_ref = db.ReferenceProperty(required=True, reference_class=Activity)
    activity_id = db.IntegerProperty(required=True)
    individual_ref = db.ReferenceProperty(required=True, reference_class=Individual)
    individual_id = db.IntegerProperty(required=True)
    attribute = db.StringProperty(required=True, choices=set([
        "IDV_SIGNUP","IDV_REJECT","IDV_TENTATIVE","IDV_FAVORITE","NPO_FAVORITE",
        "NPO_REJECT","SYSTEM_SUGGEST"]))

    @staticmethod
    def UnitTest():
        try:
            writeln("*** NpoActivityIndividual.UnitTest")

            # use any Npo entity
            npo = db.Query(Npo).get()
            # use any Activity entity
            act = db.Query(Activity).get()
            # use any Individual entity
            ind = db.Query(Individual).get()

            nai = NpoActivityIndividual(
                id=counter[NpoActivityIndividual],
                npo_ref=npo, npo_id=npo.id,
                activity_ref=act, activity_id=act.id,
                individual_ref=ind, individual_id=ind.id,
                attribute="IDV_SIGNUP")
            nai.put()

            writeln("nai=", nai.npo_ref.name, nai)
            return nai
        except:
            writeln("!!! NpoActivityIndividual.UnitTest failed: ", sys.exc_info())
        finally:
            writeln()

    @staticmethod
    def RollBack(nai):
        try:
            count = db.Query(NpoActivityIndividual).count()
            db.delete(nai)
            if db.Query(NpoActivityIndividual).count() != count - 1: raise IOError
        except:
            writeln("!!! NpoActivityIndividual.RollBack failed: ", sys.exc_info())

# end class NpoActivityIndividual


class Rating(FlowDdlModel):
    id = db.IntegerProperty(required=True)
    rater_ref = db.ReferenceProperty(required=True, reference_class=Rater)
    rater_id = db.IntegerProperty(required=True)
    ratee_ref = db.ReferenceProperty(required=True, reference_class=Ratee)
    ratee_id = db.IntegerProperty(required=True)
    time_creation = db.DateTimeProperty(required=True)
    time_modification = db.DateTimeProperty(required=True)
    # 1 ... 10
    rating = db.IntegerProperty(required=True, choices=set(range(1, 11)))
    comment = db.TextProperty(required=True)

    @staticmethod
    def UnitTest():
        try:
            writeln("*** Rating.UnitTest")

            now = datetime.datetime.utcnow()
            # use any Activity entity
            act = db.Query(Activity).get()
            # use any Individual entity
            ind = db.Query(Individual).get()

            rat = Rating(
                id=counter[Rating],
                rater_ref=ind, rater_id=ind.id,
                ratee_ref=act, ratee_id=act.id,
                time_creation=now, time_modification=now, rating=1,
                comment="no comment")
            rat.put()

            writeln("rat=", rat)
            return rat
        except:
            writeln("!!! Rating.UnitTest failed: ", sys.exc_info())
        finally:
            writeln()

    @staticmethod
    def RollBack(rat):
        try:
            count = db.Query(Rating).count()
            db.delete(rat)
            if db.Query(Rating).count() != count - 1: raise IOError
        except:
            writeln("!!! Rating.RollBack failed: ", sys.exc_info())

# end class Rating


class External(FlowDdlModel):
    id = db.IntegerProperty(required=True)
    owner_ref = db.ReferenceProperty(required=True, reference_class=Authentication)
    owner_id = db.IntegerProperty(required=True)
    cateory = db.StringProperty(required=True, choices=set([
        "RSS","ATOM","PICASA","YOUTUBE","GOOGLE_DOC","GOOGLE_SPREADSHEET","URL"]))
    context = db.LinkProperty(required=True)

    @staticmethod
    def UnitTest():
        try:
            writeln("*** External.UnitTest")

            # use any Individual entity
            ind = db.Query(Individual).get()

            ext = External(
                id=counter[External],
                owner_ref=ind.auth_ref, owner_id=ind.id,
                cateory="URL", context="http://www.google.com/")
            ext.put()

            writeln("ext=", ext)
            return ext
        except:
            writeln("!!! External.UnitTest failed: ", sys.exc_info())
        finally:
            writeln()

    @staticmethod
    def RollBack(ext):
        try:
            count = db.Query(External).count()
            db.delete(ext)
            if db.Query(External).count() != count - 1: raise IOError
        except:
            writeln("!!! External.RollBack failed: ", sys.exc_info())

# end class External


class Guestbook(FlowDdlModel):
    id = db.IntegerProperty(required=True)
    owner_ref = db.ReferenceProperty(required=True, reference_class=Authentication)
    owner_id = db.IntegerProperty(required=True)
    creater_ref = db.ReferenceProperty(required=True, reference_class=Individual)
    creater_id = db.IntegerProperty(required=True)
    time_creation = db.DateTimeProperty(required=True)
    time_reply = db.DateTimeProperty(required=True)
    creator_name = db.StringProperty(required=True, multiline=False)
    title = db.StringProperty(required=True, multiline=False)
    context = db.TextProperty(required=True)
    reply = db.TextProperty(required=True)
    # 1: IGNORE_TO_USER, 2: IGNORE_TO_READER
    attribute = db.IntegerProperty(required=True, choices=set([1,2]))

    @staticmethod
    def UnitTest():
        try:
            writeln("*** Guestbook.UnitTest")

            now = datetime.datetime.utcnow()
            # use any Npo entity
            npo = db.Query(Npo).get()
            # use any Individual entity
            ind = db.Query(Individual).get()

            gbk = Guestbook(
                id=counter[Guestbook],
                owner_ref=npo.auth_ref, owner_id=npo.id,
                creater_ref=ind, creater_id=ind.id,
                time_creation=now, time_reply=now, creator_name="Stalker Joe",
                title="FYI", context="listen up!", reply="not interested",
                attribute=1)
            gbk.put()

            writeln("gbk=", gbk)
            return gbk
        except:
            writeln("!!! Guestbook.UnitTest failed: ", sys.exc_info())
        finally:
            writeln()

    @staticmethod
    def RollBack(gbk):
        try:
            count = db.Query(Guestbook).count()
            db.delete(gbk)
            if db.Query(Guestbook).count() != count - 1: raise IOError
        except:
            writeln("!!! Guestbook.RollBack failed: ", sys.exc_info())

# end class Guestbook


class QuestionaireTemplate(FlowDdlModel):
    id = db.IntegerProperty(required=True)
    owner_ref = db.ReferenceProperty(required=True, reference_class=Individual)
    owner_id = db.IntegerProperty(required=True)
    time_creation = db.DateTimeProperty(required=True)
    time_modification = db.DateTimeProperty(required=True)
    question_answer_xml = db.TextProperty(required=True)
    # 1: SYSTEM DEFAULT, 2: USER GENERATED
    attribute = db.IntegerProperty(required=True, choices=set([1,2]))

    @staticmethod
    def UnitTest():
        try:
            writeln("*** QuestionaireTemplate.UnitTest")

            now = datetime.datetime.utcnow()
            # use any Individual entity
            ind = db.Query(Individual).get()

            qnt = QuestionaireTemplate(
                id=counter[QuestionaireTemplate],
                owner_ref=ind, owner_id=ind.id,
                time_creation=now, time_modification=now,
                question_answer_xml="how are you doing?", attribute=1)
            qnt.put()

            writeln("qnt=", qnt)
            return qnt
        except:
            writeln("!!! QuestionaireTemplate.UnitTest failed: ", sys.exc_info())
        finally:
            writeln()

    @staticmethod
    def RollBack(qnt):
        try:
            count = db.Query(QuestionaireTemplate).count()
            db.delete(qnt)
            if db.Query(QuestionaireTemplate).count() != count - 1: raise IOError
        except:
            writeln("!!! QuestionaireTemplate.RollBack failed: ", sys.exc_info())

# end class QuestionaireTemplate


class Questionaire(FlowDdlModel):
    id = db.IntegerProperty(required=True)
    activity_ref = db.ReferenceProperty(required=True, reference_class=Activity)
    activity_id = db.IntegerProperty(required=True)
    responder_ref = db.ReferenceProperty(required=True, reference_class=Individual)
    responder_id = db.IntegerProperty(required=True)
    template_ref = db.ReferenceProperty(required=True, reference_class=QuestionaireTemplate)
    template_id = db.IntegerProperty(required=True)
    response_xml = db.TextProperty(required=True)

    @staticmethod
    def UnitTest():
        try:
            writeln("*** Questionaire.UnitTest")

            # use any Activity entity
            act = db.Query(Activity).get()
            # use any Individual entity
            ind = db.Query(Individual).get()
            # use any QuestionaireTemplate entity
            qnt = db.Query(QuestionaireTemplate).get()

            que = Questionaire(
                id=counter[Questionaire],
                activity_ref=act, activity_id=act.id,
                responder_ref=ind, responder_id=ind.id,
                template_ref=qnt, template_id=qnt.id,
                response_xml="I dunno")
            que.put()

            writeln("que=", que)
            return que
        except:
            writeln("!!! Questionaire.UnitTest failed: ", sys.exc_info())
        finally:
            writeln()

    @staticmethod
    def RollBack(que):
        try:
            count = db.Query(Questionaire).count()
            db.delete(que)
            if db.Query(Questionaire).count() != count - 1: raise IOError
        except:
            writeln("!!! Questionaire.RollBack failed: ", sys.exc_info())

# end class Questionaire


#------------------
# unit-test section
#------------------

tester = []

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
        self.response.headers["Content-Type"] = "text/plain"
        tester.append(self)

        Keyword.UnitTest()
        ArchiveInfo.UnitTest()
        EventLogging.UnitTest()
        Authentication.UnitTest()

        npo = Npo.UnitTest()
        ind = Individual.UnitTest()
        act = Activity.UnitTest()
        rec = RecruitingSpec.UnitTest()
        nai = NpoActivityIndividual.UnitTest()
        rat = Rating.UnitTest()
        ext = External.UnitTest()
        gbk = Guestbook.UnitTest()
        qnt = QuestionaireTemplate.UnitTest()
        que = Questionaire.UnitTest()

        Questionaire.RollBack(que)
        QuestionaireTemplate.RollBack(qnt)
        Guestbook.RollBack(gbk)
        External.RollBack(ext)
        Rating.RollBack(rat)
        NpoActivityIndividual.RollBack(nai)
        RecruitingSpec.RollBack(rec)
        Activity.RollBack(act)
        Npo.RollBack(npo)
        Individual.RollBack(ind)

# show the unit-test page
if __name__ == "__main__":
    run_wsgi_app(webapp.WSGIApplication([("/", DDL_UnitTest)], debug=True))
