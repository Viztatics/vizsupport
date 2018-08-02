from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin, FileColumn, ImageColumn
from sqlalchemy import Column, Integer, String, ForeignKey 
from sqlalchemy.orm import relationship

from flask_appbuilder.security.sqla.models import User
"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""


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

    def __repr__(self):
        return self.name

class VizAlerts(AuditMixin,Model):
    id = Column(Integer, primary_key=True)
    rule = Column(String(50), unique = True, nullable=False)
    account_key = Column(String(100), unique = True, nullable=False)
    Amount = Column(Integer,nullable=False)

    def __repr__(self):
        return self.name
        
