from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin, FileColumn, ImageColumn
from sqlalchemy import Column, Integer, String, ForeignKey, Enum 
from sqlalchemy.orm import relationship

from flask_appbuilder.security.sqla.models import User
import enum
"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""

class StatusEnum(enum.Enum):
    open = 1
    close_true = 2
    close_false = 3

class TypeEnum(enum.Enum):
    high_risk_country = 1
    high_volume_value = 2
    profiling = 3
    flow_through = 4

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

    def __repr__(self):
        return self.account_key + " "+ self.country_name
        
