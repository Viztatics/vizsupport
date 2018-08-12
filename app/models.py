from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin, FileColumn, ImageColumn
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime 
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from flask_appbuilder.security.sqla.models import User
import enum
import datetime
"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""

class StatusEnum(enum.Enum):
    Open = 1
    Close_True = 2
    Close_False = 3

class TypeEnum(enum.Enum):
    High_Risk_Country = 1
    High_Volume_Value = 2
    Profiling = 3
    Flow_Through = 4

class ProcessEnum(enum.Enum):
    Alert_Created = 1
    Manager_Assign = 2
    Analyst_Process = 3

class Company(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name

class VizUser(User):
    company_id = Column(Integer, ForeignKey('company.id'), nullable=True)
    company = relationship("Company")

class VizRules(AuditMixin,Model):
    id = Column(Integer, primary_key=True)
    rule = Column(String(50), unique = True, nullable=False)
    file = Column(String(100), unique = True, nullable=False)

class VizAlerts(AuditMixin,Model):
    id = Column(Integer, primary_key=True)
    account_key = Column(String(100), nullable=False)
    trans_month = Column(String(6), nullable=False)
    country_abbr = Column(String(100))
    country_name = Column(String(100))
    amount = Column(Integer,nullable=False)
    cnt = Column(Integer,nullable=True)
    rule_type = Column(Enum(TypeEnum))
    rule_status = Column(Enum(StatusEnum))
    operated_on = Column(DateTime, default=datetime.datetime.now, nullable=True)
    finished_on = Column(DateTime, nullable=True)

    @declared_attr
    def operated_by_fk(cls):
        return Column(Integer, ForeignKey('ab_user.id'), nullable=True)

    @declared_attr
    def operated_by(cls):
        return relationship("VizUser", primaryjoin='%s.operated_by_fk == VizUser.id' % cls.__name__, enable_typechecks=False)

    def __repr__(self):
        return self.account_key + " "+ self.trans_month

class AlertProcess(AuditMixin,Model):
    id = Column(Integer, primary_key=True)
    alert_id = Column(Integer, ForeignKey('viz_alerts.id'), nullable=True)
    alert = relationship("VizAlerts")
    process_type = Column(Enum(ProcessEnum))
    assigned_on = Column(DateTime, default=datetime.datetime.now, nullable=True)
    syslog = Column(String(500))

    @declared_attr
    def assigned_to_fk(cls):
        return Column(Integer, ForeignKey('ab_user.id'), nullable=True)

    @declared_attr
    def assgined_by(cls):
        return relationship("VizUser", primaryjoin='%s.assigned_to_fk == VizUser.id' % cls.__name__, enable_typechecks=False)

    def __repr__(self):
        return self.syslog

class AlertProcessComments(AuditMixin,Model):
    id = Column(Integer, primary_key=True)
    process_id = Column(Integer, ForeignKey('alert_process.id'), nullable=True)
    process = relationship("AlertProcess")
    comment = Column(String(500))
    attachment = Column(String(100))

    def __repr__(self):
        return self.process+" add comment: " +  self.comment       
