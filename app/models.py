from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin, FileColumn, ImageColumn
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from flask_appbuilder.security.sqla.models import User
from flask import Markup, url_for
import enum
import datetime
"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""

class StatusEnum(enum.Enum):
    Open = "Open"
    Close_True = "Close_True"
    Close_False = "Close_False"

class TypeEnum(enum.Enum):
    High_Risk_Country = "High_Risk_Country"
    High_Volume_Value = "High_Volume_Value"
    Profiling = "Profiling"
    Flow_Through = "Flow_Through"

class ProcessEnum(enum.Enum):
    Alert_Created = "Alert_Created"
    Manager_Assign = "Manager_Assign"
    Analyst_Process = "Analyst_Process"
    No_Issue = "No_Issue"

class RuleEnum(enum.Enum):
    High_Risk_Country_Wire_Activity = "High_Risk_Country_Wire_Activity"
    High_Risk_Country_ACH_Activity = "High_Risk_Country_ACH_Activity"
    Cash_Activity_Limit = "Cash_Activity_Limit"
    Check_Activity_Limit = "Check_Activity_Limit"
    Remote_Deposit_Activity_Limit = "Remote_Deposit_Activity_Limit"
    Wire_Transfer_Activity_Limit = "Wire_Transfer_Activity_Limit"
    ACH_Transfer_Activity_Limit = "ACH_Transfer_Activity_Limit"
    Cash_Activity_Profiling = "Cash_Activity_Profiling"
    Check_Activity_Profiling = "Check_Activity_Profiling"
    Remote_Deposit_Activity_Profiling = "Remote_Deposit_Activity_Profiling"
    Wire_Transfer_Activity_Profiling = "Wire_Transfer_Activity_Profiling"
    ACH_Transfer_Activity_Profiling = "ACH_Transfer_Activity_Profiling"
    FLow_Through_Activity_Pattern = "FLow_Through_Activity_Pattern"

class Company(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name

class VizUser(User):
    title = Column(String(50))
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
    trigger_rule = Column(Enum(RuleEnum))
    current_step = Column(Enum(ProcessEnum))
    score = Column(Integer, default=0)
    operated_on = Column(DateTime, default=datetime.datetime.now, nullable=True)
    finished_on = Column(DateTime, nullable=True)

    @declared_attr
    def operated_by_fk(cls):
        return Column(Integer, ForeignKey('ab_user.id'), nullable=True)

    @declared_attr
    def operated_by(cls):
        return relationship("VizUser", primaryjoin='%s.operated_by_fk == VizUser.id' % cls.__name__, enable_typechecks=False)

    def alert_id(self):
        if self.id:
            return Markup('<a class="idlink" href="javascript:void(0)" data-aid="' + str(self.id)+'">'+str(self.id))

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

class Rules(AuditMixin,Model):
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer)
    rule_code = Column(String(100))
    rule_group = Column(String(100))
    product_type = Column(String(100))
    viz_template = Column(String(100))
    rule_description = Column(String(200))
    rule_type = Column(String(100))
    susp_type = Column(String(100))
    schedule = Column(String(100))
    viz_schedule = Column(String(100))
    pre_post_EOD = Column(String(100))
    cust_acct = Column(String(100))
    template_rule = Column(String(100))
    time_horizon = Column(String(100))
    customer_type = Column(String(100))
    customer_risk_level = Column(String(100))
    customer_risk_class = Column(String(100))
    min_trans_no = Column(Integer)
    min_ind_trans_amt = Column(Integer)
    max_ind_trans_amt = Column(Integer)
    min_agg_trans_amt = Column(Integer)
    max_agg_trans_amt = Column(Integer)
    additional = Column(String(100))
    cash_ind = Column(String(100)) 
    trans_code = Column(String(100)) 
    trans_code_group = Column(String(100)) 
    in_cash_ind = Column(String(100))
    in_trans_code = Column(String(100)) 
    in_trans_code_group = Column(String(100)) 
    out_cash_ind = Column(String(100)) 
    out_trans_code = Column(String(100)) 
    out_trans_code_group = Column(String(100))
    in_out_ratio_min = Column(Numeric(10,2))
    in_out_ratio_max = Column(Numeric(10,2))
    is_seleced = Column(Integer, default=0)  

    def __repr__(self):
        return self.company_id

