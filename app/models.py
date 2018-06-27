from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin, FileColumn, ImageColumn
from sqlalchemy import Column, Integer, String, ForeignKey 
from sqlalchemy.orm import relationship
"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""

class VizRules(AuditMixin,Model):
    id = Column(Integer, primary_key=True)
    rule = Column(String(50), unique = True, nullable=False)
    file = Column(String(100), unique = True, nullable=False)

    def __repr__(self):
        return self.name
        
