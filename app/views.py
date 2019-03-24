from flask import render_template, request, Response, jsonify, make_response,g
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.models.sqla.filters import FilterEqual,FilterEqualFunction
from flask_appbuilder.security.sqla.models import User
from flask_appbuilder import AppBuilder, BaseView, ModelView, expose, has_access
from flask_login import current_user
from sqlalchemy import func,inspect,text,distinct
from sqlalchemy.sql.expression import case,literal_column,bindparam
from sqlalchemy.orm import aliased
from werkzeug import secure_filename
from app import appbuilder, db
from config import *
from .fileUtils import *
from .models import *
from datetime import datetime
import decimal

import numpy as np
import pandas as pd
import json
from pathlib import Path,PurePath
import shutil

import boto3

"""
    Create your Views::


    class MyModelView(ModelView):
        datamodel = SQLAInterface(MyModel)


    Next, register your Views::


    appbuilder.add_view(MyModelView, "My View", icon="fa-folder-open-o", category="My Category", category_icon='fa-envelope')
"""

"""
    Application wide 404 error handler
"""
def jsonconverter(o):
    if isinstance(o, datetime):
        return o.__str__()
    if isinstance(o, decimal.Decimal):
        return str(o)

def getCompany():
    return g.user.company_id

def isManager():

    is_analysis_manager = False
    for role in current_user.roles:
        if role.name=='AnalysisManager':
            is_analysis_manager = True
    return is_analysis_manager

def getCompanyName():

    company_name = db.session.query(Company.name).filter(Company.id==current_user.company_id)
    company_name = [r for r in company_name]

    return company_name[0][0]

def isAdmin():

    is_admin = False
    for role in current_user.roles:
        if role.name=='Admin':
            is_admin = True
    return is_admin

def transTitle(transCode):

    if transCode=='Wire' or transCode=='ACH' :
        return transCode + ' Transfer'
    elif transCode=='Remote' :
        return transCode + ' Deposit'
    return transCode

def transDesc(transCode):

    return 'WIRE TRANSFER' if transCode=='Wire' else transCode.upper()

def row2dict(row):
    return {c.key: getattr(row, c.key) for c in inspect(row).all_orm_descriptors}

class CompanyModelView(ModelView):
    datamodel = SQLAInterface(Company)

class TransView(BaseView):
    
    route_base = '/trans'

    @expose('/category')
    @has_access
    def category(self):

        rule_groups = []

        rules = []

        result = dict()

        rule_num = db.session.query(func.count(Rules.id).label('count')).filter(Rules.company_id==current_user.company_id)

        rule_num = [r._asdict() for r in rule_num]

        print(rule_num)

        if rule_num[0]['count'] == 0: 

            rule_data = pd.read_csv(RULE_DEFAULT_FOLDER+'/initRule.csv')

            for index, row in rule_data.iterrows():
                rule = Rules(company_id=current_user.company_id, rule_code=row['RuleCode'], rule_group=row['RuleGroup'], product_type=row['ProductType'], viz_template=row['VizTemplate'], rule_description_short=row['RuleDescShort'], rule_description=('' if pd.isna(row['RuleDescription']) else row['RuleDescription']), rule_type=('' if pd.isna(row['Type']) else row['Type'])
                    , susp_type=('' if pd.isna(row['SuspType']) else row['SuspType']), schedule=('' if pd.isna(row['Schedule']) else row['Schedule']), viz_schedule=('' if pd.isna(row['VizSchedule']) else row['VizSchedule']), pre_post_EOD=('' if pd.isna(row['PrePostEOD']) else row['PrePostEOD']), cust_acct=('' if pd.isna(row['CustAcct']) else row['CustAcct']), template_rule=('' if pd.isna(row['TemplateRule']) else row['TemplateRule'])
                    , time_horizon=('' if pd.isna(row['TimeHorizon']) else row['TimeHorizon']), customer_type=('' if pd.isna(row['CustomerType']) else row['CustomerType']), customer_risk_level=('' if pd.isna(row['CustomerRiskLevel']) else row['CustomerRiskLevel']), customer_risk_class=('' if pd.isna(row['CustomerRiskClass']) else row['CustomerRiskClass']), min_trans_no=(-1 if pd.isna(row['Min_Trans_No']) else row['Min_Trans_No']), min_ind_trans_amt=(-1 if pd.isna(row['Min_Ind_Trans_Amt']) else row['Min_Ind_Trans_Amt'])
                    , max_ind_trans_amt=(-1 if pd.isna(row['Max_Ind_Trans_Amt']) else row['Max_Ind_Trans_Amt']), min_agg_trans_amt=(-1 if pd.isna(row['Min_Agg_Trans_Amt']) else row['Min_Agg_Trans_Amt']), max_agg_trans_amt=(-1 if pd.isna(row['Max_Agg_Trans_Amt']) else row['Max_Agg_Trans_Amt']), additional=('' if pd.isna(row['Additional']) else row['Additional']), cash_ind=(-1 if pd.isna(row['Cash_Ind']) else row['Cash_Ind']), trans_code=('' if pd.isna(row['Trans_Code']) else row['Trans_Code'])
                    , trans_code_group=('' if pd.isna(row['Trans_Code_Group']) else row['Trans_Code_Group']), in_cash_ind=(-1 if pd.isna(row['In_Cash_Ind']) else row['In_Cash_Ind']), in_trans_code=('' if pd.isna(row['In_Trans_Code']) else row['In_Trans_Code']), in_trans_code_group=('' if pd.isna(row['In_Trans_Code_Group']) else row['In_Trans_Code_Group']), out_cash_ind=(-1 if pd.isna(row['Out_Cash_Ind']) else row['Out_Cash_Ind']), out_trans_code=('' if pd.isna(row['Out_Trans_Code']) else row['Out_Trans_Code'])
                    , out_trans_code_group=('' if pd.isna(row['Out_Trans_Code_Group']) else row['Out_Trans_Code_Group']), in_out_ratio_min=(-1 if pd.isna(row['In_Out_Ratio_Min']) else row['In_Out_Ratio_Min']*100.00), in_out_ratio_max=(-1 if pd.isna(row['In_Out_Ratio_Max']) else row['In_Out_Ratio_Max']*100.00))
                self.appbuilder.get_session.add(rule)
            self.appbuilder.get_session.commit()

        rule_groups = db.session.query(Rules.rule_group).distinct().filter(Rules.company_id==current_user.company_id,Rules.rule_group!='Profiling').order_by(Rules.rule_group)

        rule_groups = [r._asdict() for r in rule_groups]

        rules = db.session.query(Rules.id,Rules.company_id,Rules.rule_code,Rules.rule_group,Rules.product_type,Rules.viz_template,Rules.rule_description_short,Rules.rule_description,Rules.susp_type,Rules.schedule,Rules.viz_schedule,
            Rules.pre_post_EOD,Rules.cust_acct,Rules.template_rule,Rules.time_horizon,Rules.customer_type,Rules.customer_risk_level,Rules.customer_risk_class,Rules.min_trans_no,Rules.min_ind_trans_amt,
            Rules.max_ind_trans_amt,Rules.min_agg_trans_amt,Rules.max_agg_trans_amt,Rules.additional,Rules.cash_ind,Rules.trans_code,Rules.trans_code_group,Rules.in_cash_ind,Rules.in_trans_code,
            Rules.in_trans_code_group,Rules.out_cash_ind,Rules.out_trans_code,Rules.out_trans_code_group,Rules.in_out_ratio_min,Rules.in_out_ratio_max,Rules.is_seleced).filter(Rules.company_id==current_user.company_id,Rules.rule_group!='Profiling').order_by(Rules.rule_group,Rules.id)

        rules = [r._asdict() for r in rules]

        for group in rule_groups:
            result[group['rule_group']]=[]
            for rule in rules:
                if group['rule_group'] == rule['rule_group']:
                    result[group['rule_group']].append(rule)
                if rule["rule_code"]=='blvelshwir':
                    print(rule)

        return self.render_template('trans/monitoring_category.html',rules=result)


class RuleView(BaseView):
    
    route_base = '/rules'
    HIGH_RISK_COUNTRY_FOLDER_PREFIX = 'highRiskCountry'
    HIGH_VALUE_VOLUMN_FOLDER_PREFIX = 'highValueVolume'
    ACTIVITY_PROFILING_FOLDER_PREFIX = 'activityProfiling'
    ACTIVITY_FLOW_THROUGH_FOLDER_PREFIX = 'activityPattern'
    """
    s3 = boto3.resource(
        's3',
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY,
    )
    """
    #s3 = boto3.resource('s3')
    #bucket_name='vizrules'

    ALLOWED_RND_EXTENSIONS = set(['csv'])

    def allowed_file(self,filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.ALLOWED_RND_EXTENSIONS

    """
    Rule1: High Risk Countries Wire
    """        

    @expose('/highRiskCountry/<rule_code>/<transCode>')
    @has_access
    def highRiskCountry(self,rule_code,transCode):

        keyname = ''
        highRiskCountryFolder = self.HIGH_RISK_COUNTRY_FOLDER_PREFIX+transCode
        src_file = RULE_DEFAULT_FOLDER+highRiskCountryFolder+"/highRiskCountry.csv"
        dst_path = RULE_UPLOAD_FOLDER+highRiskCountryFolder+"/"+str(current_user.id)
        if request.method == 'GET':

            if not os.path.exists(dst_path):   
                os.makedirs(dst_path)
            if not os.listdir(dst_path):
                shutil.copy(src_file, dst_path)
            p = Path(dst_path)
            for child in p.iterdir():
                keyname = PurePath(child).name
            rules = db.session.query(Rules.id,Rules.company_id,Rules.rule_code,Rules.rule_group,Rules.product_type,Rules.viz_template,Rules.rule_description_short,Rules.rule_description,Rules.susp_type,Rules.schedule,Rules.viz_schedule,
                    Rules.pre_post_EOD,Rules.cust_acct,Rules.template_rule,Rules.time_horizon,Rules.customer_type,Rules.customer_risk_level,Rules.customer_risk_class,Rules.min_trans_no,Rules.min_ind_trans_amt,
                    Rules.max_ind_trans_amt,Rules.min_agg_trans_amt,Rules.max_agg_trans_amt,Rules.additional,Rules.cash_ind,Rules.trans_code,Rules.trans_code_group,Rules.in_cash_ind,Rules.in_trans_code,
                    Rules.in_trans_code_group,Rules.out_cash_ind,Rules.out_trans_code,Rules.out_trans_code_group,Rules.in_out_ratio_min,Rules.in_out_ratio_max,Rules.is_seleced).filter(Rules.company_id==current_user.company_id,Rules.rule_code==rule_code)

            rules = [r._asdict() for r in rules]
        return self.render_template('rules/rule_high_risk_country.html',keyname=keyname,rulename=rules[0]["rule_description_short"],customertype=rules[0]["customer_type"],customerrisklevel=rules[0]["customer_risk_level"],transCode=transTitle(transCode))

    @expose('/highRiskCountry/statisticsdata/<transCode>',methods=['POST'])
    def getHighRiskCountryStatisticsData(self,transCode):

    	highRiskCountryFolder = self.HIGH_RISK_COUNTRY_FOLDER_PREFIX+transCode

    	dst_path = RULE_UPLOAD_FOLDER+highRiskCountryFolder+"/"+str(current_user.id)

    	dst_file = request.get_json()["filename"]

    	#transCodeType = request.get_json()["transCodeType"]

    	#crDb = request.get_json()["crDb"]

    	outlier = request.get_json()["outlier"]

    	table_data = pd.read_csv(dst_path+"/"+dst_file,usecols=['ACCOUNT_KEY', 'Month of Trans Date','Trans_Amt','outlier','Trans_Code_Type'])

    	table_data = table_data[table_data['Trans_Code_Type']==transDesc(transCode)]

    	#table_data = table_data.groupby(['ACCOUNT_KEY', 'Month of Trans Date'],as_index=False).sum()

    	#table_data = table_data[(table_data['Trans Code Type']==transCodeType)&(table_data['Cr_Db']==crDb)]

    	if outlier!='1':
    		table_data = table_data[table_data['outlier'].isnull()]

    	min_data = table_data['Trans_Amt'].min()

    	max_data = table_data['Trans_Amt'].max()
    	
    	median_data = table_data['Trans_Amt'].median()

    	mean_data = table_data['Trans_Amt'].mean()

    	return Response(pd.io.json.dumps([{'min_data':min_data,'max_data':max_data,'median_data':median_data,'mean_data':mean_data}]), mimetype='application/json')
    
    @expose('/highRiskCountry/percentiledata/<transCode>',methods=['POST'])
    def getHighRiskCountryPercentileData(self,transCode):

    	highRiskCountryFolder = self.HIGH_RISK_COUNTRY_FOLDER_PREFIX+transCode

    	dst_path = RULE_UPLOAD_FOLDER+highRiskCountryFolder+"/"+str(current_user.id)

    	dst_file = request.get_json()["filename"]

    	outlier = request.get_json()["outlier"]

    	table_data = pd.read_csv(dst_path+"/"+dst_file,usecols=['ACCOUNT_KEY', 'Month of Trans Date','Trans_Amt','outlier','Trans_Code_Type'])

    	table_data = table_data[table_data['Trans_Code_Type']==transDesc(transCode)]

    	#table_data = table_data.groupby(['ACCOUNT_KEY', 'Month of Trans Date'],as_index=False).sum()

    	#table_data = table_data[(table_data['Trans Code Type']==transCodeType)&(table_data['Cr_Db']==crDb)]

    	if outlier!='1':
    		table_data = table_data[table_data['outlier'].isnull()]    	

    	percentile_data = table_data['Trans_Amt'].quantile([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])

    	return Response(percentile_data.to_json(orient='records'), mimetype='application/json')

    @expose('/highRiskCountry/paretodata/<transCode>',methods=['POST'])
    def getHighRiskCountryParetoData(self,transCode):

    	highRiskCountryFolder = self.HIGH_RISK_COUNTRY_FOLDER_PREFIX+transCode

    	dst_path = RULE_UPLOAD_FOLDER+highRiskCountryFolder+"/"+str(current_user.id)

    	dst_file = request.get_json()["filename"]

    	outlier = request.get_json()["outlier"]

    	table_data = pd.read_csv(dst_path+"/"+dst_file,usecols=['ACCOUNT_KEY', 'Trans_Amt','outlier','Trans_Code_Type'])

    	table_data = table_data[table_data['Trans_Code_Type']==transDesc(transCode)]

    	table_data = table_data.groupby(['ACCOUNT_KEY'],as_index=False).sum()

    	#table_data = table_data[(table_data['Trans Code Type']==transCodeType)&(table_data['Cr_Db']==crDb)]

    	if outlier!='1':
    		table_data = table_data[table_data['outlier']==0]   

    	bar_data = table_data.sort_values(by='Trans_Amt', ascending=False)

    	line_data = bar_data['Trans_Amt'].cumsum()/bar_data['Trans_Amt'].sum()*100.00

    	line_data = pd.Series(line_data, name='percentage')

    	pareto_data = pd.concat([bar_data, line_data], axis=1, sort=False)

    	return Response(pareto_data.to_json(orient='records'), mimetype='application/json')

    @expose('/highRiskCountry/heatmap/<transCode>',methods=['POST'])
    @has_access
    def getHighRiskCountryHeatMapData(self,transCode):

        highRiskCountryFolder = self.HIGH_RISK_COUNTRY_FOLDER_PREFIX+transCode

        dst_path = RULE_UPLOAD_FOLDER+highRiskCountryFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

        threshold = request.get_json()["threshNum"]

        def_data_county = dst_path+"/"+dst_file

        heat_map_data = pd.read_csv(def_data_county,usecols=['Month of Trans Date','OPP_CNTRY','Trans_Amt','Trans_Code_Type'])

        heat_map_data = heat_map_data[(heat_map_data['Trans_Code_Type']==transDesc(transCode))&(heat_map_data['OPP_CNTRY'].notnull())&((heat_map_data['OPP_CNTRY'])!='US')]

        #min_month = heat_map_data['Month of Trans Date'].min()
        #heat_map_result = heat_map_data.loc[heat_map_data['Month of Trans Date'] == min_month]
        heat_map_result = heat_map_data.groupby(['Month of Trans Date','OPP_CNTRY']).sum().reset_index()
        #print(heat_map_result.to_json(orient='records'))
        heat_map_result = heat_map_result[(heat_map_result['Trans_Amt']>=int(threshold))]

        return Response(heat_map_result.to_json(orient='records'), mimetype='application/json')

    @expose('/highRiskCountry/scatterplot/<transCode>',methods=['POST'])
    @has_access
    def getHighRiskCountryScatterPlotData(self,transCode):

    	highRiskCountryFolder = self.HIGH_RISK_COUNTRY_FOLDER_PREFIX+transCode

    	dst_path = RULE_UPLOAD_FOLDER+highRiskCountryFolder+"/"+str(current_user.id)

    	dst_file = request.get_json()["filename"]

    	def_data_no_county = dst_path+"/"+dst_file

    	plot_data = pd.read_csv(def_data_no_county,usecols=['Trans_Count','Trans_Amt','ACCOUNT_KEY','Month of Trans Date','outlier','Trans_Code_Type'])
    	#plot_data = plot_data.groupby(['ACCOUNT_KEY','Month of Trans Date'],as_index=False).sum()
    	plot_data = plot_data[['Trans_Count','Trans_Amt','ACCOUNT_KEY','Month of Trans Date','outlier','Trans_Code_Type']]

    	plot_data = plot_data[plot_data['Trans_Code_Type']==transDesc(transCode)]
    	plot_data = plot_data[(plot_data['Trans_Amt']>=100)]

    	return Response(plot_data.to_json(orient='split'), mimetype='application/json')

    @expose('/highRiskCountry/scatterstatistics/<transCode>',methods=['POST'])
    @has_access
    def getHighRiskCountryScatterStatisticsData(self,transCode):

        highRiskCountryFolder = self.HIGH_RISK_COUNTRY_FOLDER_PREFIX+transCode

        dst_path = RULE_UPLOAD_FOLDER+highRiskCountryFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

        threshold_below = request.get_json()["threshNum"]

        threshold_above = request.get_json()["threshNum2"]

        def_data_no_county = dst_path+"/"+dst_file

        plot_data = pd.read_csv(def_data_no_county,usecols=['Trans_Count','Trans_Amt','ACCOUNT_KEY','Month of Trans Date','outlier','Trans_Code_Type'])
        #plot_data = plot_data.groupby(['ACCOUNT_KEY','Month of Trans Date'],as_index=False).sum()
        plot_data = plot_data[plot_data['Trans_Code_Type']==transDesc(transCode)]
        amount = np.round(plot_data['Trans_Amt'].sum(),decimals=2)
        count = plot_data['Trans_Count'].sum()

        plot_below = plot_data[(plot_data['Trans_Amt']>=int(threshold_below))]
        above_amount_below = np.round(plot_below['Trans_Amt'].sum(),decimals=2)
        above_count_below = plot_below['Trans_Count'].sum()
        below_amount_below = np.round(amount - above_amount_below,decimals=2)
        below_count_below = count - above_count_below
        percent_amount_below = np.round(above_amount_below*100/amount,decimals=2)
        percent_acount_below = np.round(above_count_below*100/count,decimals=2)

        plot_above = plot_data[(plot_data['Trans_Amt']>=int(threshold_above))]
        above_amount_above = np.round(plot_above['Trans_Amt'].sum(),decimals=2)
        above_count_above = plot_above['Trans_Count'].sum()
        below_amount_above = np.round(amount - above_amount_above,decimals=2)
        below_count_above = count - above_count_above
        percent_amount_above = np.round(above_amount_above*100/amount,decimals=2)
        percent_acount_above = np.round(above_count_above*100/count,decimals=2)

        return Response(pd.io.json.dumps({'amount':amount,'count':count,'above_amount_below':above_amount_below,'above_count_below':above_count_below,'below_amount_below':below_amount_below,'below_count_below':below_count_below,'percent_amount_below':percent_amount_below,'percent_acount_below':percent_acount_below,'above_amount_above':above_amount_above,'above_count_above':above_count_above,'below_amount_above':below_amount_above,'below_count_above':below_count_above,'percent_amount_above':percent_amount_above,'percent_acount_above':percent_acount_above}), mimetype='application/json')

    @expose('/highRiskCountry/tabledata/<transCode>',methods=['POST'])
    @has_access
    def getHighRiskCountryTableData(self,transCode):

        highRiskCountryFolder = self.HIGH_RISK_COUNTRY_FOLDER_PREFIX+transCode

        dst_path = RULE_UPLOAD_FOLDER+highRiskCountryFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

        threshold = request.get_json()["threshNum"]

        threshold2 = request.get_json()["threshNum2"]

        def_data_no_county = dst_path+"/"+dst_file

        table_data = pd.read_csv(def_data_no_county,usecols=['ACCOUNT_KEY','Month of Trans Date','OPP_CNTRY','Country Name','Trans_Amt','Trans_Code_Type'])

        #table_data = table_data.groupby(['ACCOUNT_KEY', 'Month of Trans Date'],as_index=False).sum()

        table_data = table_data[(table_data['Trans_Amt']>=int(threshold))&(table_data['Trans_Code_Type']==transDesc(transCode))&(table_data['OPP_CNTRY'].notnull())&((table_data['OPP_CNTRY'])!='US')]

        table_data['run2'] = np.where(table_data['Trans_Amt']>=int(threshold2), '1', '0')

        db_result = db.session.query(func.count(VizAlerts.account_key).label('count'),VizAlerts.account_key).join(User, VizAlerts.created_by_fk == User.id).group_by(VizAlerts.account_key).filter(VizUser.company_id==current_user.company_id)

        db_frame = pd.DataFrame(db_result.all(),columns=[column['name'] for column in db_result.column_descriptions])

        db_frame = db_frame.rename(str.upper, axis='columns')

        table_data = pd.merge(table_data,db_frame,how='left',on='ACCOUNT_KEY')

        table_data['ID'] = table_data.index

        return Response(table_data.to_json(orient='records'), mimetype='application/json')

    @expose('/highRiskCountry/tablestatistics/<transCode>',methods=['POST'])
    @has_access
    def getHighRiskCountryTableStatistics(self,transCode):

        highRiskCountryFolder = self.HIGH_RISK_COUNTRY_FOLDER_PREFIX+transCode

        dst_path = RULE_UPLOAD_FOLDER+highRiskCountryFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

        threshold = request.get_json()["threshNum"]

        threshold2 = request.get_json()["threshNum2"]

        def_data_no_county = dst_path+"/"+dst_file

        table_data = pd.read_csv(def_data_no_county,usecols=['ACCOUNT_KEY','Month of Trans Date','OPP_CNTRY','Country Name','Trans_Amt','Trans_Code_Type'])

        table_data = table_data[(table_data['Trans_Amt']>=int(threshold))&(table_data['Trans_Code_Type']==transDesc(transCode))&(table_data['OPP_CNTRY'].notnull())&((table_data['OPP_CNTRY'])!='US')]

        table_data['run2'] = np.where(table_data['Trans_Amt']>=int(threshold2), '1', '0')

        db_result = db.session.query(func.count(Customer.id).label('count')).filter(Customer.company_id==current_user.company_id)

        db_result = [r._asdict() for r in db_result]

        total = db_result[0]["count"]

        run1_customer = table_data['ACCOUNT_KEY'].nunique()

        run1_customer_not = int(total)-int(run1_customer)

        run1_customer_percent = np.round(int(run1_customer)*100/total,decimals=2)

        run1_customer_percent_not = np.round(run1_customer_not*100/total,decimals=2)

        table_data2 = table_data[table_data['run2']=='1']

        run2_customer = table_data2['ACCOUNT_KEY'].nunique()

        run2_customer_not = int(total)-int(run2_customer)

        run2_customer_percent = np.round(int(run2_customer)*100/total,decimals=2)

        run2_customer_percent_not = np.round(run2_customer_not*100/total,decimals=2)

        return Response(pd.io.json.dumps({'total':total,'run1_customer':run1_customer,'run1_customer_percent':run1_customer_percent,'run2_customer':run2_customer,'run2_customer_percent':run2_customer_percent,'run1_customer_not':run1_customer_not,'run1_customer_percent_not':run1_customer_percent_not,'run2_customer_not':run2_customer_not,'run2_customer_percent_not':run2_customer_percent_not}), mimetype='application/json')


    @expose('/highRiskCountry/runDiff/<transCode>',methods=['POST'])
    @has_access
    def getHighRiskCountryRunDiff(self,transCode):

        highRiskCountryFolder = self.HIGH_RISK_COUNTRY_FOLDER_PREFIX+transCode

        dst_path = RULE_UPLOAD_FOLDER+highRiskCountryFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

        threshold = request.get_json()["threshNum"]

        threshold2 = request.get_json()["threshNum2"]

        def_data_no_county = dst_path+"/"+dst_file

        table_data = pd.read_csv(def_data_no_county,usecols=['ACCOUNT_KEY','Month of Trans Date','OPP_CNTRY','Country Name','Trans_Amt','Trans_Code_Type'])

        table_data = table_data[(table_data['Trans_Amt']>=int(threshold))&(table_data['Trans_Code_Type']==transDesc(transCode))&(table_data['OPP_CNTRY'].notnull())&((table_data['OPP_CNTRY'])!='US')]

        table_data['run2'] = np.where(table_data['Trans_Amt']>=int(threshold2), '1', '0')

        table_data_1 = table_data[table_data['run2']=='0']

        table_data_2 = table_data[table_data['run2']=='1']

        df_common = table_data_1.merge(table_data_2,on=['ACCOUNT_KEY'])

        table_data_3 = table_data_1[~table_data_1['ACCOUNT_KEY'].isin(df_common['ACCOUNT_KEY'])]

        rundiff = table_data_3.groupby(['ACCOUNT_KEY']).size().to_frame('size').reset_index()

        return Response(rundiff.to_json(orient='records'), mimetype='application/json')

    @expose('/highRiskCountry/alertdata/<transCode>',methods=['POST'])
    @has_access
    def createHighRiskCountryAlertData(self,transCode):

        items = request.get_json()["items"]
        dataId = request.get_json()["dataId"]
        custType = request.get_json()["custType"]
        custRLel = request.get_json()["custRLel"]
        threshNum = request.get_json()["threshNum"]
        threshNum2 = request.get_json()["threshNum2"]
        circleName = request.get_json()["circleName"]
        runName = request.get_json()["runName"]

        if transCode == 'Wire' :
            rule_name = RuleEnum.High_Risk_Country_Wire_Activity
        else:
            rule_name = RuleEnum.High_Risk_Country_ACH_Activity

        circle = db.session.query(Circle.id).filter(Circle.name==circleName)

        if circle.count() == 0 :
            new_circle = Circle(name=circleName,company_id=current_user.company_id)
            self.appbuilder.get_session.add(new_circle)
            self.appbuilder.get_session.flush()
            circle_id = new_circle.id
        else :
            circle = [r._asdict() for r in circle]
            circle_id = circle[0]["id"]

        run = db.session.query(Run.id).filter(Run.circle_id==circle_id,Run.name==runName,Run.rule_group=='High Risk Country',Run.product_type==transCode,Run.customer_type==custType,Run.customer_risk_level==custRLel,Run.current_threshold==threshNum,Run.testing_threshold==threshNum2,Run.current_cnt_threshold==0,Run.testing_cnt_threshold==0,Run.data_id==dataId)

        if run.count() == 0 :
            new_run = Run(circle_id=circle_id,name=runName,rule_group='High Risk Country',product_type=transCode,customer_type=custType,customer_risk_level=custRLel,current_threshold=threshNum,testing_threshold=threshNum2,current_cnt_threshold=0,testing_cnt_threshold=0,data_id=dataId)
            self.appbuilder.get_session.add(new_run)
            self.appbuilder.get_session.flush()
            run_id = new_run.id
        else :
            run = [r._asdict() for r in run]
            run_id = run[0]["id"]

        for item in items:

            alertdata = VizAlerts(run_id=run_id,company_id=current_user.company_id,account_key=item['ACCOUNT_KEY'], trans_month=item['Month of Trans Date'], country_abbr=item['OPP_CNTRY'], country_name = item['Country Name'], amount=item['Trans_Amt'],rule_type=TypeEnum.High_Risk_Country,rule_status=StatusEnum.Open,trigger_rule=rule_name,current_step=ProcessEnum.Manager_Assign,operated_by_fk=current_user.id)
            self.appbuilder.get_session.add(alertdata)
            self.appbuilder.get_session.flush()
            alertproc = AlertProcess(alert_id=alertdata.id,process_type=ProcessEnum.Alert_Created,assigned_to_fk=current_user.id,syslog=Alert_Created.format(current_user.username,datetime.now(),rule_name.name,TypeEnum.High_Risk_Country.name,StatusEnum.Open.name))
            self.appbuilder.get_session.add(alertproc)

        self.appbuilder.get_session.commit()
        return  json.dumps({})


    @expose('/highRiskCountry/upload/<transCode>',methods=['POST','DELETE'])
    @has_access
    def getHighRiskCountryFileData(self,transCode):

        highRiskCountryFolder = self.HIGH_RISK_COUNTRY_FOLDER_PREFIX+transCode

        dst_path = RULE_UPLOAD_FOLDER+highRiskCountryFolder+"/"+str(current_user.id)

        if request.method == 'POST':
            files = request.files['file']

            if files:
                filename = secure_filename(files.filename)

                mime_type = files.content_type

                if not self.allowed_file(files.filename):
                    result = uploadfile(name=filename, type=mime_type, size=0, not_allowed_msg="File type not allowed")

                else:
                    if not os.path.exists(dst_path):
                        os.makedirs(dst_path)
                    files.save(os.path.join((dst_path), filename))
                    """
                    self.s3.Object('vizrules', 'highRiskCountry/'+filename).put(Body=files)
                    """

        if request.method == 'DELETE':
            keyname = request.get_json()["keyname"]
            os.remove(dst_path+"/"+keyname)
            """
            bucket = self.s3.Bucket(self.bucket_name)
            for key in bucket.objects.all():
                 
                 words = key.key.split('/')
                 if len(words)==2 and words[0]=='highRiskCountry' and words[1]==keyname:
                     key.delete()
            """    

        return  json.dumps({})


    """
    Rule2: High Risk Volume
    """        

    @expose('/highRiskVolume/<rule_code>/<transCode>')
    @has_access
    def highRiskVolume(self,rule_code,transCode):

        keyname = ''
        highRiskVolumnFolder = self.HIGH_VALUE_VOLUMN_FOLDER_PREFIX+transCode
        src_file = RULE_DEFAULT_FOLDER+highRiskVolumnFolder+"/highValueVolume.csv"
        dst_path = RULE_UPLOAD_FOLDER+highRiskVolumnFolder+"/"+str(current_user.id)
        if request.method == 'GET':
            """
            for bucket in self.s3.buckets.all():
                for key in bucket.objects.all():
                    words = key.key.split('/')
                    if len(words)==2 and words[0]=='highRiskVolume' and words[1]!='':
                        keyname=words[1]
            """
            if not os.path.exists(dst_path):   
                os.makedirs(dst_path)
            if not os.listdir(dst_path):
                shutil.copy(src_file, dst_path)
            p = Path(dst_path)
            for child in p.iterdir():
                keyname = PurePath(child).name
                #self.s3.Object('vizrules', 'highRiskCountry/highRiskCountry.csv').put(Body=open('app/static/csv/rules/highRiskCountry.csv', 'rb'))

            rules = db.session.query(Rules.id,Rules.company_id,Rules.rule_code,Rules.rule_group,Rules.product_type,Rules.viz_template,Rules.rule_description_short,Rules.rule_description,Rules.susp_type,Rules.schedule,Rules.viz_schedule,
                Rules.pre_post_EOD,Rules.cust_acct,Rules.template_rule,Rules.time_horizon,Rules.customer_type,Rules.customer_risk_level,Rules.customer_risk_class,Rules.min_trans_no,Rules.min_ind_trans_amt,
                Rules.max_ind_trans_amt,Rules.min_agg_trans_amt,Rules.max_agg_trans_amt,Rules.additional,Rules.cash_ind,Rules.trans_code,Rules.trans_code_group,Rules.in_cash_ind,Rules.in_trans_code,
                Rules.in_trans_code_group,Rules.out_cash_ind,Rules.out_trans_code,Rules.out_trans_code_group,Rules.in_out_ratio_min,Rules.in_out_ratio_max,Rules.is_seleced).filter(Rules.company_id==current_user.company_id,Rules.rule_code==rule_code)

            rules = [r._asdict() for r in rules]

            return self.render_template('rules/rule_high_risk_volume.html',keyname=keyname,rulename=rules[0]["rule_description_short"],customertype=rules[0]["customer_type"],customerrisklevel=rules[0]["customer_risk_level"],transCode=transTitle(transCode))

    @expose('/highRiskVolume/statisticsdata/<transCode>',methods=['POST'])
    @has_access
    def getHighRiskVolumeStatisticsData(self,transCode):

    	highRiskVolumnFolder = self.HIGH_VALUE_VOLUMN_FOLDER_PREFIX+transCode

    	dst_path = RULE_UPLOAD_FOLDER+highRiskVolumnFolder+"/"+str(current_user.id)

    	dst_file = request.get_json()["filename"]

    	crDb = request.get_json()["crDb"]

    	outlier = request.get_json()["outlier"]

    	table_data = pd.read_csv(dst_path+"/"+dst_file)

    	table_data = table_data[(table_data['Trans Code Type']==transDesc(transCode))&(table_data['Cr_Db']==crDb)]

    	if outlier!='1':
    		table_data = table_data[table_data['outlier']!=1]

    	amt_min_data = table_data['TRANS_AMT'].min()

    	amt_max_data = table_data['TRANS_AMT'].max()
    	
    	amt_median_data = table_data['TRANS_AMT'].median()

    	amt_mean_data = table_data['TRANS_AMT'].mean()

    	cnt_min_data = table_data['TRANS_CNT'].min()

    	cnt_max_data = table_data['TRANS_CNT'].max()
    	
    	cnt_median_data = table_data['TRANS_CNT'].median()

    	cnt_mean_data = table_data['TRANS_CNT'].mean()

    	return Response(pd.io.json.dumps([{'amt_min_data':amt_min_data,'amt_max_data':amt_max_data,'amt_median_data':amt_median_data,'amt_mean_data':amt_mean_data
    		,'cnt_min_data':cnt_min_data,'cnt_max_data':cnt_max_data,'cnt_median_data':cnt_median_data,'cnt_mean_data':cnt_mean_data}]), mimetype='application/json')

    @expose('/highRiskVolume/percentiledata/<amount>/<transCode>',methods=['POST'])
    def getHighRiskVolumnPercentileData(self,amount,transCode):

    	highRiskVolumnFolder = self.HIGH_VALUE_VOLUMN_FOLDER_PREFIX+transCode

    	dst_path = RULE_UPLOAD_FOLDER+highRiskVolumnFolder+"/"+str(current_user.id)

    	dst_file = request.get_json()["filename"]

    	crDb = request.get_json()["crDb"]

    	outlier = request.get_json()["outlier"]

    	table_data = pd.read_csv(dst_path+"/"+dst_file,usecols=['TRANS_AMT','TRANS_CNT','Cr_Db','outlier','Trans Code Type'])

    	table_data = table_data[(table_data['Trans Code Type']==transDesc(transCode))&(table_data['Cr_Db']==crDb)]

    	#table_data = table_data.groupby(['ACCOUNT_KEY', 'Month of Trans Date'],as_index=False).sum()

    	#table_data = table_data[(table_data['Trans Code Type']==transCodeType)&(table_data['Cr_Db']==crDb)]

    	if outlier!='1':
    		table_data = table_data[table_data['outlier'].isnull()]

    	if amount=='amt':
    	 	percentile_data = table_data['TRANS_AMT'].quantile([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])
    	else:
    		percentile_data = table_data['TRANS_CNT'].quantile([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])

    	return Response(percentile_data.to_json(orient='records'), mimetype='application/json')

    @expose('/highRiskVolume/paretodata/<amount>/<transCode>',methods=['POST'])
    def getHighRiskVolumnParetoData(self,amount,transCode):

    	highRiskVolumnFolder = self.HIGH_VALUE_VOLUMN_FOLDER_PREFIX+transCode

    	dst_path = RULE_UPLOAD_FOLDER+highRiskVolumnFolder+"/"+str(current_user.id)

    	dst_file = request.get_json()["filename"]

    	crDb = request.get_json()["crDb"]

    	outlier = request.get_json()["outlier"]

    	table_data = pd.read_csv(dst_path+"/"+dst_file,usecols=['ACCOUNT_KEY','TRANS_CNT','Cr_Db','TRANS_AMT','outlier','Trans Code Type'])

    	table_data = table_data[(table_data['Trans Code Type']==transDesc(transCode))&(table_data['Cr_Db']==crDb)]

    	table_data = table_data.groupby(['ACCOUNT_KEY'],as_index=False).sum()

    	#table_data = table_data[(table_data['Trans Code Type']==transCodeType)&(table_data['Cr_Db']==crDb)]

    	if outlier!='1':
    		table_data = table_data[table_data['outlier']==0] 

    	if amount=='amt':  

    		bar_data = table_data.sort_values(by='TRANS_AMT', ascending=False)
    		line_data = bar_data['TRANS_AMT'].cumsum()/bar_data['TRANS_AMT'].sum()*100.00

    	else:
    		bar_data = table_data.sort_values(by='TRANS_CNT', ascending=False)
    		line_data = bar_data['TRANS_CNT'].cumsum()/bar_data['TRANS_CNT'].sum()*100.00    		
    	line_data = pd.Series(line_data, name='percentage')
    	pareto_data = pd.concat([bar_data, line_data], axis=1, sort=False)

    	return Response(pareto_data.to_json(orient='records'), mimetype='application/json')

    @expose('/highRiskVolume/scatterplot/<transCode>',methods=['POST'])
    @has_access
    def getHighRiskVolumeScatterPlotData(self,transCode):

    	highRiskVolumnFolder = self.HIGH_VALUE_VOLUMN_FOLDER_PREFIX+transCode

    	dst_path = RULE_UPLOAD_FOLDER+highRiskVolumnFolder+"/"+str(current_user.id)

    	dst_file = request.get_json()["filename"]

    	crDb = request.get_json()["crDb"]

    	def_volume_data = dst_path+"/"+dst_file

    	plot_data = pd.read_csv(def_volume_data)

    	plot_data = plot_data[(plot_data['Trans Code Type']==transDesc(transCode))&(plot_data['Cr_Db']==crDb)]
    	plot_data = plot_data[['TRANS_CNT','TRANS_AMT','ACCOUNT_KEY','Month of Trans Date','outlier']]
    	plot_data = plot_data[(plot_data['TRANS_AMT']>=100)]

    	return Response(plot_data.to_json(orient='split'), mimetype='application/json')

    @expose('/highRiskVolume/scatterstatistics/<transCode>',methods=['POST'])
    @has_access
    def getHighRiskVolumeScatterStatisticsData(self,transCode):

        highRiskVolumnFolder = self.HIGH_VALUE_VOLUMN_FOLDER_PREFIX+transCode

        dst_path = RULE_UPLOAD_FOLDER+highRiskVolumnFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

        crDb = request.get_json()["crDb"]

        amt_threshold_below = request.get_json()["amtThreshNum"]

        amt_threshold_above = request.get_json()["amtThreshNum2"]

        cnt_threshold_below = request.get_json()["cntThreshNum"]

        cnt_threshold_above = request.get_json()["cntThreshNum2"]

        def_volume_data = dst_path+"/"+dst_file

        plot_data = pd.read_csv(def_volume_data)

        plot_data = plot_data[(plot_data['Trans Code Type']==transDesc(transCode))&(plot_data['Cr_Db']==crDb)]
        plot_data = plot_data[['TRANS_CNT','TRANS_AMT','ACCOUNT_KEY','Month of Trans Date','outlier']]

        #plot_data = plot_data.groupby(['ACCOUNT_KEY','Month of Trans Date'],as_index=False).sum()
        amount = np.round(plot_data['TRANS_AMT'].sum(),decimals=2)
        count = plot_data['TRANS_CNT'].sum()

        plot_below = plot_data[(plot_data['TRANS_AMT']>=int(amt_threshold_below))&(plot_data['TRANS_CNT']>=int(cnt_threshold_below))]
        above_amount_below = np.round(plot_below['TRANS_AMT'].sum(),decimals=2)
        above_count_below = plot_below['TRANS_CNT'].sum()
        below_amount_below = np.round(amount - above_amount_below,decimals=2)
        below_count_below = count - above_count_below
        percent_amount_below = np.round(above_amount_below*100/amount,decimals=2)
        percent_acount_below = np.round(above_count_below*100/count,decimals=2)

        plot_above = plot_data[(plot_data['TRANS_AMT']>=int(amt_threshold_above))&(plot_data['TRANS_CNT']>=int(cnt_threshold_above))]
        above_amount_above = np.round(plot_above['TRANS_AMT'].sum(),decimals=2)
        above_count_above = plot_above['TRANS_CNT'].sum()
        below_amount_above = np.round(amount - above_amount_above,decimals=2)
        below_count_above = count - above_count_above
        percent_amount_above = np.round(above_amount_above*100/amount,decimals=2)
        percent_acount_above = np.round(above_count_above*100/count,decimals=2)

        return Response(pd.io.json.dumps({'amount':amount,'count':count,'above_amount_below':above_amount_below,'above_count_below':above_count_below,'below_amount_below':below_amount_below,'below_count_below':below_count_below,'percent_amount_below':percent_amount_below,'percent_acount_below':percent_acount_below,'above_amount_above':above_amount_above,'above_count_above':above_count_above,'below_amount_above':below_amount_above,'below_count_above':below_count_above,'percent_amount_above':percent_amount_above,'percent_acount_above':percent_acount_above}), mimetype='application/json')


    @expose('/highRiskVolume/tabledata/<transCode>',methods=['POST'])
    @has_access
    def getHighRiskVolumeTableData(self,transCode):

        highRiskVolumnFolder = self.HIGH_VALUE_VOLUMN_FOLDER_PREFIX+transCode

        dst_path = RULE_UPLOAD_FOLDER+highRiskVolumnFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

        crDb = request.get_json()["crDb"]

        amtThreshold = request.get_json()["amtThreshNum"]

        cntThreshold = request.get_json()["cntThreshNum"]

        amtThreshold2 = request.get_json()["amtThreshNum2"]

        cntThreshold2 = request.get_json()["cntThreshNum2"]

        def_volume_data = dst_path+"/"+dst_file

        table_data = pd.read_csv(def_volume_data)

        table_data = table_data[(table_data['TRANS_AMT']>=int(amtThreshold))&(table_data['TRANS_CNT']>=int(cntThreshold))&(table_data['Trans Code Type']==transDesc(transCode))&(table_data['Cr_Db']==crDb)]

        table_data = table_data[['ACCOUNT_KEY','Month of Trans Date','TRANS_AMT','TRANS_CNT']]

        table_data['run2'] = np.where((table_data['TRANS_AMT']>=int(amtThreshold2))&(table_data['TRANS_CNT']>=int(cntThreshold2)), '1', '0')

        db_result = db.session.query(func.count(VizAlerts.account_key).label('count'),VizAlerts.account_key).join(User, VizAlerts.created_by_fk == User.id).group_by(VizAlerts.account_key).filter(VizUser.company_id==current_user.company_id)

        db_frame = pd.DataFrame(db_result.all(),columns=[column['name'] for column in db_result.column_descriptions])

        db_frame = db_frame.rename(str.upper, axis='columns')

        table_data = pd.merge(table_data,db_frame,how='left',on='ACCOUNT_KEY')    

        table_data['ID'] = table_data.index	

        return Response(table_data.to_json(orient='records'), mimetype='application/json')

    @expose('/highRiskVolume/tablestatistics/<transCode>',methods=['POST'])
    @has_access
    def getHighRiskVolumeTableStatistics(self,transCode):

        highRiskVolumnFolder = self.HIGH_VALUE_VOLUMN_FOLDER_PREFIX+transCode

        dst_path = RULE_UPLOAD_FOLDER+highRiskVolumnFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

        crDb = request.get_json()["crDb"]

        amtThreshold = request.get_json()["amtThreshNum"]

        cntThreshold = request.get_json()["cntThreshNum"]

        amtThreshold2 = request.get_json()["amtThreshNum2"]

        cntThreshold2 = request.get_json()["cntThreshNum2"]

        def_volume_data = dst_path+"/"+dst_file

        table_data = pd.read_csv(def_volume_data)

        table_data = table_data[(table_data['TRANS_AMT']>=int(amtThreshold))&(table_data['TRANS_CNT']>=int(cntThreshold))&(table_data['Trans Code Type']==transDesc(transCode))&(table_data['Cr_Db']==crDb)]

        table_data = table_data[['ACCOUNT_KEY','Month of Trans Date','TRANS_AMT','TRANS_CNT']]

        table_data['run2'] = np.where((table_data['TRANS_AMT']>=int(amtThreshold2))&(table_data['TRANS_CNT']>=int(cntThreshold2)), '1', '0')

        db_result = db.session.query(func.count(Customer.id).label('count')).filter(Customer.company_id==current_user.company_id)

        db_result = [r._asdict() for r in db_result]

        total = db_result[0]["count"]

        run1_customer = table_data['ACCOUNT_KEY'].nunique()

        run1_customer_not = int(total)-int(run1_customer)

        run1_customer_percent = np.round(int(run1_customer)*100/total,decimals=2)

        run1_customer_percent_not = np.round(run1_customer_not*100/total,decimals=2)

        table_data2 = table_data[table_data['run2']=='1']

        run2_customer = table_data2['ACCOUNT_KEY'].nunique()

        run2_customer_not = int(total)-int(run2_customer)

        run2_customer_percent = np.round(int(run2_customer)*100/total,decimals=2)

        run2_customer_percent_not = np.round(run2_customer_not*100/total,decimals=2)

        return Response(pd.io.json.dumps({'total':total,'run1_customer':run1_customer,'run1_customer_percent':run1_customer_percent,'run2_customer':run2_customer,'run2_customer_percent':run2_customer_percent,'run1_customer_not':run1_customer_not,'run1_customer_percent_not':run1_customer_percent_not,'run2_customer_not':run2_customer_not,'run2_customer_percent_not':run2_customer_percent_not}), mimetype='application/json')


    @expose('/highRiskVolume/runDiff/<transCode>',methods=['POST'])
    @has_access
    def getHighRiskVolumeRunDiff(self,transCode):

        highRiskVolumnFolder = self.HIGH_VALUE_VOLUMN_FOLDER_PREFIX+transCode

        dst_path = RULE_UPLOAD_FOLDER+highRiskVolumnFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

        crDb = request.get_json()["crDb"]

        amtThreshold = request.get_json()["amtThreshNum"]

        cntThreshold = request.get_json()["cntThreshNum"]

        amtThreshold2 = request.get_json()["amtThreshNum2"]

        cntThreshold2 = request.get_json()["cntThreshNum2"]

        def_volume_data = dst_path+"/"+dst_file

        table_data = pd.read_csv(def_volume_data)

        table_data = table_data[(table_data['TRANS_AMT']>=int(amtThreshold))&(table_data['TRANS_CNT']>=int(cntThreshold))&(table_data['Trans Code Type']==transDesc(transCode))&(table_data['Cr_Db']==crDb)]

        table_data = table_data[['ACCOUNT_KEY','Month of Trans Date','TRANS_AMT','TRANS_CNT']]

        table_data['run2'] = np.where((table_data['TRANS_AMT']>=int(amtThreshold2))&(table_data['TRANS_CNT']>=int(cntThreshold2)), '1', '0')

        table_data_1 = table_data[table_data['run2']=='0']

        table_data_2 = table_data[table_data['run2']=='1']

        df_common = table_data_1.merge(table_data_2,on=['ACCOUNT_KEY'])

        table_data_3 = table_data_1[~table_data_1['ACCOUNT_KEY'].isin(df_common['ACCOUNT_KEY'])]

        rundiff = table_data_3.groupby(['ACCOUNT_KEY']).size().to_frame('size').reset_index()

        return Response(rundiff.to_json(orient='records'), mimetype='application/json')


    @expose('/highRiskVolume/alertdata/<transCode>',methods=['POST'])
    @has_access
    def createHighRiskVolumeAlertData(self,transCode):

        items = request.get_json()["items"]
        dataId = request.get_json()["dataId"]
        custType = request.get_json()["custType"]
        custRLel = request.get_json()["custRLel"]
        amtThreshNum = request.get_json()["amtThreshNum"]
        amtThreshNum2 = request.get_json()["amtThreshNum2"]
        cntThreshNum = request.get_json()["cntThreshNum"]
        cntThreshNum2 = request.get_json()["cntThreshNum2"]
        circleName = request.get_json()["circleName"]
        runName = request.get_json()["runName"]

        if transCode == 'Cash' :
            rule_name = RuleEnum.Cash_Activity_Limit
        elif transCode == 'Check' :
            rule_name = RuleEnum.Check_Activity_Limit
        elif transCode == 'Remote' :
            rule_name = RuleEnum.Remote_Deposit_Activity_Limit
        elif transCode == 'Wire' :
            rule_name = RuleEnum.Wire_Transfer_Activity_Limit
        else :
            rule_name = RuleEnum.ACH_Transfer_Activity_Limit

        circle = db.session.query(Circle.id).filter(Circle.name==circleName)

        if circle.count() == 0 :
            new_circle = Circle(name=circleName,company_id=current_user.company_id)
            self.appbuilder.get_session.add(new_circle)
            self.appbuilder.get_session.flush()
            circle_id = new_circle.id
        else :
            circle = [r._asdict() for r in circle]
            circle_id = circle[0]["id"]

        run = db.session.query(Run.id).filter(Run.circle_id==circle_id,Run.name==runName,Run.rule_group=='High Value Dectection',Run.product_type==transCode,Run.customer_type==custType,Run.customer_risk_level==custRLel,Run.current_threshold==amtThreshNum,Run.testing_threshold==amtThreshNum2,Run.current_cnt_threshold==cntThreshNum,Run.testing_cnt_threshold==cntThreshNum2,Run.data_id==dataId)

        if run.count() == 0 :
            new_run = Run(circle_id=circle_id,name=runName,rule_group='High Value Dectection',product_type=transCode,customer_type=custType,customer_risk_level=custRLel,current_threshold=amtThreshNum,testing_threshold=amtThreshNum2,current_cnt_threshold=cntThreshNum,testing_cnt_threshold=cntThreshNum2,data_id=dataId)
            self.appbuilder.get_session.add(new_run)
            self.appbuilder.get_session.flush()
            run_id = new_run.id
        else :
            run = [r._asdict() for r in run]
            run_id = run[0]["id"]

        for item in items:

            alertdata = VizAlerts(run_id=run_id,company_id=current_user.company_id,account_key=item['ACCOUNT_KEY'], trans_month=item['Month of Trans Date'], amount=item['TRANS_AMT'],cnt=item['TRANS_CNT'], rule_type=TypeEnum.High_Volume_Value,rule_status=StatusEnum.Open,trigger_rule=rule_name,current_step=ProcessEnum.Manager_Assign,operated_by_fk=current_user.id)
            self.appbuilder.get_session.add(alertdata)
            self.appbuilder.get_session.flush()
            alertproc = AlertProcess(alert_id=alertdata.id,process_type=ProcessEnum.Alert_Created,assigned_to_fk=current_user.id,syslog=Alert_Created.format(current_user.username,datetime.now(),rule_name.name,TypeEnum.High_Risk_Country.name,StatusEnum.Open.name))
            self.appbuilder.get_session.add(alertproc)

        self.appbuilder.get_session.commit()
        return  json.dumps({})

    @expose('/highRiskVolume/upload',methods=['POST','DELETE'])
    @has_access
    def getHighRiskVolumeFileData(self):

        highRiskVolumeFolder = self.HIGH_VALUE_VOLUMN_FOLDER_PREFIX+transCode

        dst_path = RULE_UPLOAD_FOLDER+highRiskVolumeFolder+"/"+str(current_user.id)

        if request.method == 'POST':
            files = request.files['file']

            if files:
                filename = secure_filename(files.filename)

                mime_type = files.content_type

                if not self.allowed_file(files.filename):
                    result = uploadfile(name=filename, type=mime_type, size=0, not_allowed_msg="File type not allowed")

                else:
                    if not os.path.exists(dst_path):
                        os.makedirs(dst_path)
                    files.save(os.path.join((dst_path), filename))
                    """
                    self.s3.Object('vizrules', 'highRiskCountry/'+filename).put(Body=files)
                    """

        if request.method == 'DELETE':
            keyname = request.get_json()["keyname"]
            os.remove(dst_path+"/"+keyname)
            """
            bucket = self.s3.Bucket(self.bucket_name)
            for key in bucket.objects.all():
                 
                 words = key.key.split('/')
                 if len(words)==2 and words[0]=='highRiskCountry' and words[1]==keyname:
                     key.delete()
            """    

        return  json.dumps({})

    """
    Rule3: profiling
    """        

    @expose('/profiling/<transCode>')
    @has_access
    def activityprofiling(self,transCode):

    	keyname = ''
    	profilingFolder = self.ACTIVITY_PROFILING_FOLDER_PREFIX+transCode
    	src_file = RULE_DEFAULT_FOLDER+profilingFolder+"/activityprofiling.csv"
    	dst_path = RULE_UPLOAD_FOLDER+profilingFolder+"/"+str(current_user.id)
    	if request.method == 'GET':
    		"""
    		for bucket in self.s3.buckets.all():
    			for key in bucket.objects.all():
    				words = key.key.split('/')
    				if len(words)==2 and words[0]=='highRiskVolume' and words[1]!='':
    					keyname=words[1]
    		"""
    		if not os.path.exists(dst_path):   
    			os.makedirs(dst_path)
    		if not os.listdir(dst_path):
    			shutil.copy(src_file, dst_path)
    		p = Path(dst_path)
    		for child in p.iterdir():
    			keyname = PurePath(child).name
        	#self.s3.Object('vizrules', 'highRiskCountry/highRiskCountry.csv').put(Body=open('app/static/csv/rules/highRiskCountry.csv', 'rb'))
    		return self.render_template('rules/rule_high_risk_profiling.html',keyname=keyname,transCode=transTitle(transCode))

    @expose('/profiling/statisticsdata/<transCode>',methods=['POST'])
    @has_access
    def getProfilingStatisticsData(self,transCode):

    	profilingFolder = self.ACTIVITY_PROFILING_FOLDER_PREFIX+transCode

    	dst_path = RULE_UPLOAD_FOLDER+profilingFolder+"/"+str(current_user.id)

    	dst_file = request.get_json()["filename"]

    	#crDb = request.get_json()["crDb"]

    	outlier = request.get_json()["outlier"]

    	table_data = pd.read_csv(dst_path+"/"+dst_file)

    	table_data['TRANS_CNT'] = table_data['Credit+TRANS_CNT'] + table_data['Debit+TRANS_CNT']

    	#table_data = table_data[(table_data['Trans Code Type']==transDesc(transCode))&(table_data['Cr_Db']==crDb)]

    	if outlier!='1':
    		table_data = table_data[table_data['outlier']!=1]

    	amt_min_data = table_data['TRANS_AMT'].min()

    	amt_max_data = table_data['TRANS_AMT'].max()
    	
    	amt_median_data = table_data['TRANS_AMT'].median()

    	amt_mean_data = table_data['TRANS_AMT'].mean()

    	cnt_min_data = table_data['TRANS_CNT'].min()

    	cnt_max_data = table_data['TRANS_CNT'].max()
    	
    	cnt_median_data = table_data['TRANS_CNT'].median()

    	cnt_mean_data = table_data['TRANS_CNT'].mean()

    	return Response(pd.io.json.dumps([{'amt_min_data':amt_min_data,'amt_max_data':amt_max_data,'amt_median_data':amt_median_data,'amt_mean_data':amt_mean_data
    		,'cnt_min_data':cnt_min_data,'cnt_max_data':cnt_max_data,'cnt_median_data':cnt_median_data,'cnt_mean_data':cnt_mean_data}]), mimetype='application/json')

    @expose('/profiling/percentiledata/<amount>/<transCode>',methods=['POST'])
    def getProfilingPercentileData(self,amount,transCode):

    	profilingFolder = self.ACTIVITY_PROFILING_FOLDER_PREFIX+transCode

    	dst_path = RULE_UPLOAD_FOLDER+profilingFolder+"/"+str(current_user.id)

    	dst_file = request.get_json()["filename"]

    	#crDb = request.get_json()["crDb"]

    	outlier = request.get_json()["outlier"]

    	table_data = pd.read_csv(dst_path+"/"+dst_file,usecols=['TRANS_AMT','Credit+TRANS_CNT','Debit+TRANS_CNT','outlier'])

    	table_data['TRANS_CNT'] = table_data['Credit+TRANS_CNT'] + table_data['Debit+TRANS_CNT']

    	#table_data = table_data[(table_data['Trans Code Type']==transDesc(transCode))&(table_data['Cr_Db']==crDb)]

    	#table_data = table_data.groupby(['ACCOUNT_KEY', 'Month of Trans Date'],as_index=False).sum()

    	#table_data = table_data[(table_data['Trans Code Type']==transCodeType)&(table_data['Cr_Db']==crDb)]

    	if outlier!='1':
    		table_data = table_data[table_data['outlier'].isnull()]

    	if amount=='amt':
    	 	percentile_data = table_data['TRANS_AMT'].quantile([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])
    	else:
    		percentile_data = table_data['TRANS_CNT'].quantile([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])

    	return Response(percentile_data.to_json(orient='records'), mimetype='application/json')

    @expose('/profiling/paretodata/<amount>/<transCode>',methods=['POST'])
    def getProfilingParetoData(self,amount,transCode):

    	profilingFolder = self.ACTIVITY_PROFILING_FOLDER_PREFIX+transCode

    	dst_path = RULE_UPLOAD_FOLDER+profilingFolder+"/"+str(current_user.id)

    	dst_file = request.get_json()["filename"]

    	#crDb = request.get_json()["crDb"]

    	outlier = request.get_json()["outlier"]

    	table_data = pd.read_csv(dst_path+"/"+dst_file,usecols=['ACCOUNT_KEY','Credit+TRANS_CNT','Debit+TRANS_CNT','TRANS_AMT','outlier'])

    	table_data['TRANS_CNT'] = table_data['Credit+TRANS_CNT'] + table_data['Debit+TRANS_CNT']

    	#table_data = table_data[(table_data['Trans Code Type']==transDesc(transCode))&(table_data['Cr_Db']==crDb)]

    	table_data = table_data.groupby(['ACCOUNT_KEY'],as_index=False).sum()

    	#table_data = table_data[(table_data['Trans Code Type']==transCodeType)&(table_data['Cr_Db']==crDb)]

    	if outlier!='1':
    		table_data = table_data[table_data['outlier']==0] 

    	if amount=='amt':  

    		bar_data = table_data.sort_values(by='TRANS_AMT', ascending=False)
    		line_data = bar_data['TRANS_AMT'].cumsum()/bar_data['TRANS_AMT'].sum()*100.00

    	else:
    		bar_data = table_data.sort_values(by='TRANS_CNT', ascending=False)
    		line_data = bar_data['TRANS_CNT'].cumsum()/bar_data['TRANS_CNT'].sum()*100.00    		
    	line_data = pd.Series(line_data, name='percentage')
    	pareto_data = pd.concat([bar_data, line_data], axis=1, sort=False)

    	return Response(pareto_data.to_json(orient='records'), mimetype='application/json')

    @expose('/profiling/scatterplot/<transCode>',methods=['POST'])
    @has_access
    def getProfilingScatterPlotData(self,transCode):

    	profilingFolder = self.ACTIVITY_PROFILING_FOLDER_PREFIX+transCode

    	dst_path = RULE_UPLOAD_FOLDER+profilingFolder+"/"+str(current_user.id)

    	dst_file = request.get_json()["filename"]

    	#crDb = request.get_json()["crDb"]

    	def_volume_data = dst_path+"/"+dst_file

    	plot_data = pd.read_csv(def_volume_data,usecols=['ACCOUNT_KEY','YearMonth','Credit+TRANS_CNT','Debit+TRANS_CNT','TRANS_AMT','outlier'])

    	plot_data['TRANS_CNT'] = plot_data['Credit+TRANS_CNT'] + plot_data['Debit+TRANS_CNT']

    	plot_data = plot_data[['TRANS_CNT','TRANS_AMT','ACCOUNT_KEY','YearMonth','outlier']]

    	plot_data = plot_data[(plot_data['TRANS_AMT']>=100)]

    	#plot_data = plot_data[(plot_data['Trans Code Type']==transDesc(transCode))&(plot_data['Cr_Db']==crDb)]

    	return Response(plot_data.to_json(orient='split'), mimetype='application/json')

    @expose('/profiling/scatterstatistics/<transCode>',methods=['POST'])
    @has_access
    def getProfilingScatterStatisticsData(self,transCode):

        profilingFolder = self.ACTIVITY_PROFILING_FOLDER_PREFIX+transCode

        dst_path = RULE_UPLOAD_FOLDER+profilingFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

        amt_threshold_below = request.get_json()["amtThreshNum"]

        amt_threshold_above = request.get_json()["amtThreshNum2"]

        cnt_threshold_below = request.get_json()["cntThreshNum"]

        cnt_threshold_above = request.get_json()["cntThreshNum2"]

        def_volume_data = dst_path+"/"+dst_file

        plot_data = pd.read_csv(def_volume_data)

        plot_data = pd.read_csv(def_volume_data,usecols=['ACCOUNT_KEY','YearMonth','Credit+TRANS_CNT','Debit+TRANS_CNT','TRANS_AMT','outlier'])

        plot_data['TRANS_CNT'] = plot_data['Credit+TRANS_CNT'] + plot_data['Debit+TRANS_CNT']

        plot_data = plot_data[['TRANS_CNT','TRANS_AMT','ACCOUNT_KEY','YearMonth','outlier']]

        #plot_data = plot_data.groupby(['ACCOUNT_KEY','Month of Trans Date'],as_index=False).sum()
        amount = np.round(plot_data['TRANS_AMT'].sum(),decimals=2)
        count = plot_data['TRANS_CNT'].sum()

        plot_below = plot_data[(plot_data['TRANS_AMT']>=int(amt_threshold_below))&(plot_data['TRANS_CNT']>=int(cnt_threshold_below))]
        above_amount_below = np.round(plot_below['TRANS_AMT'].sum(),decimals=2)
        above_count_below = plot_below['TRANS_CNT'].sum()
        below_amount_below = np.round(amount - above_amount_below,decimals=2)
        below_count_below = count - above_count_below
        percent_amount_below = np.round(above_amount_below*100/amount,decimals=2)
        percent_acount_below = np.round(above_count_below*100/count,decimals=2)

        plot_above = plot_data[(plot_data['TRANS_AMT']>=int(amt_threshold_above))&(plot_data['TRANS_CNT']>=int(cnt_threshold_above))]
        above_amount_above = np.round(plot_above['TRANS_AMT'].sum(),decimals=2)
        above_count_above = plot_above['TRANS_CNT'].sum()
        below_amount_above = np.round(amount - above_amount_above,decimals=2)
        below_count_above = count - above_count_above
        percent_amount_above = np.round(above_amount_above*100/amount,decimals=2)
        percent_acount_above = np.round(above_count_above*100/count,decimals=2)

        return Response(pd.io.json.dumps({'amount':amount,'count':count,'above_amount_below':above_amount_below,'above_count_below':above_count_below,'below_amount_below':below_amount_below,'below_count_below':below_count_below,'percent_amount_below':percent_amount_below,'percent_acount_below':percent_acount_below,'above_amount_above':above_amount_above,'above_count_above':above_count_above,'below_amount_above':below_amount_above,'below_count_above':below_count_above,'percent_amount_above':percent_amount_above,'percent_acount_above':percent_acount_above}), mimetype='application/json')


    @expose('/profiling/tabledata/<transCode>',methods=['POST'])
    @has_access
    def getProfilingTableData(self,transCode):

        profilingFolder = self.ACTIVITY_PROFILING_FOLDER_PREFIX+transCode

        dst_path = RULE_UPLOAD_FOLDER+profilingFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

    	#crDb = request.get_json()["crDb"]

        amtThreshold = request.get_json()["amtThreshNum"]

        cntThreshold = request.get_json()["cntThreshNum"]

        amtThreshold2 = request.get_json()["amtThreshNum2"]

        cntThreshold2 = request.get_json()["cntThreshNum2"]

        def_volume_data = dst_path+"/"+dst_file

        table_data = pd.read_csv(def_volume_data,usecols=['ACCOUNT_KEY','YearMonth','Credit+TRANS_CNT','Debit+TRANS_CNT','TRANS_AMT','outlier'])

        table_data['TRANS_CNT'] = table_data['Credit+TRANS_CNT'] + table_data['Debit+TRANS_CNT']

        table_data = table_data[(table_data['TRANS_AMT']>=int(amtThreshold))&(table_data['TRANS_CNT']>=int(cntThreshold))] 

        table_data['run2'] = np.where((table_data['TRANS_AMT']>=int(amtThreshold2))&(table_data['TRANS_CNT']>=int(cntThreshold2)), '1', '0')

        db_result = db.session.query(func.count(VizAlerts.account_key).label('count'),VizAlerts.account_key).join(User, VizAlerts.created_by_fk == User.id).group_by(VizAlerts.account_key).filter(VizUser.company_id==current_user.company_id)

        db_frame = pd.DataFrame(db_result.all(),columns=[column['name'] for column in db_result.column_descriptions])

        db_frame = db_frame.rename(str.upper, axis='columns')

        table_data = pd.merge(table_data,db_frame,how='left',on='ACCOUNT_KEY')

        table_data['ID'] = table_data.index	

        return Response(table_data.to_json(orient='records'), mimetype='application/json')

    @expose('/profiling/tablestatistics/<transCode>',methods=['POST'])
    @has_access
    def getProfilingTableStatistics(self,transCode):

        profilingFolder = self.ACTIVITY_PROFILING_FOLDER_PREFIX+transCode

        dst_path = RULE_UPLOAD_FOLDER+profilingFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

        amtThreshold = request.get_json()["amtThreshNum"]

        cntThreshold = request.get_json()["cntThreshNum"]

        amtThreshold2 = request.get_json()["amtThreshNum2"]

        cntThreshold2 = request.get_json()["cntThreshNum2"]

        def_volume_data = dst_path+"/"+dst_file

        table_data = pd.read_csv(def_volume_data,usecols=['ACCOUNT_KEY','YearMonth','Credit+TRANS_CNT','Debit+TRANS_CNT','TRANS_AMT','outlier'])

        table_data['TRANS_CNT'] = table_data['Credit+TRANS_CNT'] + table_data['Debit+TRANS_CNT']

        table_data = table_data[(table_data['TRANS_AMT']>=int(amtThreshold))&(table_data['TRANS_CNT']>=int(cntThreshold))]

        table_data['run2'] = np.where((table_data['TRANS_AMT']>=int(amtThreshold2))&(table_data['TRANS_CNT']>=int(cntThreshold2)), '1', '0')

        db_result = db.session.query(func.count(Customer.id).label('count')).filter(Customer.company_id==current_user.company_id)

        db_result = [r._asdict() for r in db_result]

        total = db_result[0]["count"]

        run1_customer = table_data['ACCOUNT_KEY'].nunique()

        run1_customer_not = int(total)-int(run1_customer)

        run1_customer_percent = np.round(int(run1_customer)*100/total,decimals=2)

        run1_customer_percent_not = np.round(run1_customer_not*100/total,decimals=2)

        table_data2 = table_data[table_data['run2']=='1']

        run2_customer = table_data2['ACCOUNT_KEY'].nunique()

        run2_customer_not = int(total)-int(run2_customer)

        run2_customer_percent = np.round(int(run2_customer)*100/total,decimals=2)

        run2_customer_percent_not = np.round(run2_customer_not*100/total,decimals=2)

        return Response(pd.io.json.dumps({'total':total,'run1_customer':run1_customer,'run1_customer_percent':run1_customer_percent,'run2_customer':run2_customer,'run2_customer_percent':run2_customer_percent,'run1_customer_not':run1_customer_not,'run1_customer_percent_not':run1_customer_percent_not,'run2_customer_not':run2_customer_not,'run2_customer_percent_not':run2_customer_percent_not}), mimetype='application/json')


    @expose('/profiling/ruledata/<transCode>',methods=['POST'])
    @has_access
    def getProfilingRuleData(self,transCode):

    	profilingFolder = self.ACTIVITY_PROFILING_FOLDER_PREFIX+transCode

    	dst_path = RULE_UPLOAD_FOLDER+profilingFolder+"/"+str(current_user.id)

    	dst_file = request.get_json()["filename"]

    	#crDb = request.get_json()["crDb"]

    	accountid = request.get_json()["ACCOUNT_KEY"]

    	amtThreshold = request.get_json()["amtThreshNum"]

    	cntThreshold = request.get_json()["cntThreshNum"]

    	minSD = request.get_json()["minSD"]

    	def_volume_data = dst_path+"/"+dst_file

    	table_data = pd.read_csv(def_volume_data,usecols=['ACCOUNT_KEY','SD of 6 Month','Mean of 6 Month','YearMonth','Credit+TRANS_CNT','Debit+TRANS_CNT','TRANS_AMT','outlier'])

    	table_data['TRANS_CNT'] = table_data['Credit+TRANS_CNT'] + table_data['Debit+TRANS_CNT']

    	table_data = table_data[(table_data['ACCOUNT_KEY']==accountid)]

    	table_data = table_data.sort_values(by=['YearMonth'])

    	table_data['alert'] = (table_data['TRANS_AMT']>=int(amtThreshold))&(table_data['TRANS_CNT']>=int(cntThreshold))&(table_data['TRANS_AMT']>=(table_data['Mean of 6 Month']+int(minSD)*table_data['SD of 6 Month']))

    	return Response(table_data.to_json(orient='records'), mimetype='application/json')


    @expose('/profiling/alertdata/<transCode>',methods=['POST'])
    @has_access
    def createProfilingAlertData(self,transCode):

        if transCode == 'Cash' :
            rule_name = RuleEnum.Cash_Activity_Profiling
        elif transCode == 'Check' :
            rule_name = RuleEnum.Check_Activity_Profiling
        elif transCode == 'Remote' :
            rule_name = RuleEnum.Remote_Deposit_Activity_Profiling
        elif transCode == 'Wire' :
            rule_name = RuleEnum.Wire_Transfer_Activity_Profiling
        else :
            rule_name = RuleEnum.ACH_Transfer_Activity_Profiling

        items = request.get_json()["items"]
        dataId = request.get_json()["dataId"]
        amtThreshNum = request.get_json()["amtThreshNum"]
        amtThreshNum2 = request.get_json()["amtThreshNum2"]
        cntThreshNum = request.get_json()["cntThreshNum"]
        cntThreshNum2 = request.get_json()["cntThreshNum2"]
        circleName = request.get_json()["circleName"]
        runName = request.get_json()["runName"]

        circle = db.session.query(Circle.id).filter(Circle.name==circleName)

        if circle.count() == 0 :
            new_circle = Circle(name=circleName,company_id=current_user.company_id)
            self.appbuilder.get_session.add(new_circle)
            self.appbuilder.get_session.flush()
            circle_id = new_circle.id
        else :
            circle = [r._asdict() for r in circle]
            circle_id = circle[0]["id"]

        run = db.session.query(Run.id).filter(Run.circle_id==circle_id,Run.name==runName,Run.rule_group=='Profiling',Run.product_type==transCode,Run.customer_type=='',Run.customer_risk_level=='',Run.current_threshold==amtThreshNum,Run.testing_threshold==amtThreshNum2,Run.current_cnt_threshold==cntThreshNum,Run.testing_cnt_threshold==cntThreshNum2,Run.data_id==dataId)

        if run.count() == 0 :
            new_run = Run(circle_id=circle_id,name=runName,rule_group='Profiling',product_type=transCode,customer_type='',customer_risk_level='',current_threshold=amtThreshNum,testing_threshold=amtThreshNum2,current_cnt_threshold=cntThreshNum,testing_cnt_threshold=cntThreshNum2,data_id=dataId)
            self.appbuilder.get_session.add(new_run)
            self.appbuilder.get_session.flush()
            run_id = new_run.id
        else :
            run = [r._asdict() for r in run]
            run_id = run[0]["id"]

        for item in items:

            alertdata = VizAlerts(run_id=run_id,company_id=current_user.company_id,account_key=item['ACCOUNT_KEY'], trans_month=item['YearMonth'], amount=item['TRANS_AMT'],cnt=item['TRANS_CNT'],rule_type=TypeEnum.Profiling,rule_status=StatusEnum.Open,trigger_rule=rule_name,current_step=ProcessEnum.Manager_Assign,operated_by_fk=current_user.id)
            self.appbuilder.get_session.add(alertdata)
            self.appbuilder.get_session.flush()
            alertproc = AlertProcess(alert_id=alertdata.id,process_type=ProcessEnum.Alert_Created,assigned_to_fk=current_user.id,syslog=Alert_Created.format(current_user.username,datetime.now(),rule_name.name,TypeEnum.High_Risk_Country.name,StatusEnum.Open.name))
            self.appbuilder.get_session.add(alertproc)

        self.appbuilder.get_session.commit()
        return  json.dumps({})

    @expose('/profiling/runDiff/<transCode>',methods=['POST'])
    @has_access
    def getProfilingRunDiff(self,transCode):

        profilingFolder = self.ACTIVITY_PROFILING_FOLDER_PREFIX+transCode

        dst_path = RULE_UPLOAD_FOLDER+profilingFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

        amtThreshold = request.get_json()["amtThreshNum"]

        cntThreshold = request.get_json()["cntThreshNum"]

        amtThreshold2 = request.get_json()["amtThreshNum2"]

        cntThreshold2 = request.get_json()["cntThreshNum2"]

        def_volume_data = dst_path+"/"+dst_file

        table_data = pd.read_csv(def_volume_data,usecols=['ACCOUNT_KEY','YearMonth','Credit+TRANS_CNT','Debit+TRANS_CNT','TRANS_AMT','outlier'])

        table_data['TRANS_CNT'] = table_data['Credit+TRANS_CNT'] + table_data['Debit+TRANS_CNT']

        table_data = table_data[(table_data['TRANS_AMT']>=int(amtThreshold))&(table_data['TRANS_CNT']>=int(cntThreshold))]

        table_data['run2'] = np.where((table_data['TRANS_AMT']>=int(amtThreshold2))&(table_data['TRANS_CNT']>=int(cntThreshold2)), '1', '0')

        table_data_1 = table_data[table_data['run2']=='0']

        table_data_2 = table_data[table_data['run2']=='1']

        df_common = table_data_1.merge(table_data_2,on=['ACCOUNT_KEY'])

        table_data_3 = table_data_1[~table_data_1['ACCOUNT_KEY'].isin(df_common['ACCOUNT_KEY'])]

        rundiff = table_data_3.groupby(['ACCOUNT_KEY']).size().to_frame('size').reset_index()

        return Response(rundiff.to_json(orient='records'), mimetype='application/json')

    @expose('/profiling/upload/<transCode>',methods=['POST','DELETE'])
    @has_access
    def getProfilingFileData(self,transCode):

        profilingFolder = self.ACTIVITY_PROFILING_FOLDER_PREFIX+transCode

        dst_path = RULE_UPLOAD_FOLDER+profilingFolder+"/"+str(current_user.id)

        if request.method == 'POST':
            files = request.files['file']

            if files:
                filename = secure_filename(files.filename)

                mime_type = files.content_type

                if not self.allowed_file(files.filename):
                    result = uploadfile(name=filename, type=mime_type, size=0, not_allowed_msg="File type not allowed")

                else:
                    if not os.path.exists(dst_path):
                        os.makedirs(dst_path)
                    files.save(os.path.join((dst_path), filename))
                    """
                    self.s3.Object('vizrules', 'highRiskCountry/'+filename).put(Body=files)
                    """

        if request.method == 'DELETE':
            keyname = request.get_json()["keyname"]
            os.remove(dst_path+"/"+keyname)
            """
            bucket = self.s3.Bucket(self.bucket_name)
            for key in bucket.objects.all():
                 
                 words = key.key.split('/')
                 if len(words)==2 and words[0]=='highRiskCountry' and words[1]==keyname:
                     key.delete()
            """    

        return  json.dumps({})

    """
    Rule4: FLow-Through
    """        

    @expose('/flowthrough/<rule_code>')
    @has_access
    def activityflowthrough(self,rule_code):

        keyname = ''
        flowthroughFolder = self.ACTIVITY_FLOW_THROUGH_FOLDER_PREFIX+'Flow'
        src_file = RULE_DEFAULT_FOLDER+flowthroughFolder+"/activityflowthrough.csv"
        dst_path = RULE_UPLOAD_FOLDER+flowthroughFolder+"/"+str(current_user.id)
        if request.method == 'GET':
            """
            for bucket in self.s3.buckets.all():
            	for key in bucket.objects.all():
            		words = key.key.split('/')
            		if len(words)==2 and words[0]=='highRiskVolume' and words[1]!='':
            			keyname=words[1]
            """
            if not os.path.exists(dst_path):   
            	os.makedirs(dst_path)
            if not os.listdir(dst_path):
            	shutil.copy(src_file, dst_path)
            p = Path(dst_path)
            for child in p.iterdir():
            	keyname = PurePath(child).name
            #self.s3.Object('vizrules', 'highRiskCountry/highRiskCountry.csv').put(Body=open('app/static/csv/rules/highRiskCountry.csv', 'rb'))


            rules = db.session.query(Rules.id,Rules.company_id,Rules.rule_code,Rules.rule_group,Rules.product_type,Rules.viz_template,Rules.rule_description_short,Rules.rule_description,Rules.susp_type,Rules.schedule,Rules.viz_schedule,
                Rules.pre_post_EOD,Rules.cust_acct,Rules.template_rule,Rules.time_horizon,Rules.customer_type,Rules.customer_risk_level,Rules.customer_risk_class,Rules.min_trans_no,Rules.min_ind_trans_amt,
                Rules.max_ind_trans_amt,Rules.min_agg_trans_amt,Rules.max_agg_trans_amt,Rules.additional,Rules.cash_ind,Rules.trans_code,Rules.trans_code_group,Rules.in_cash_ind,Rules.in_trans_code,
                Rules.in_trans_code_group,Rules.out_cash_ind,Rules.out_trans_code,Rules.out_trans_code_group,Rules.in_out_ratio_min,Rules.in_out_ratio_max,Rules.is_seleced).filter(Rules.company_id==current_user.company_id,Rules.rule_code==rule_code)

            rules = [r._asdict() for r in rules]

            return self.render_template('rules/rule_high_risk_flowthrough.html',keyname=keyname,rulename=rules[0]["rule_description_short"],customertype=rules[0]["customer_type"],customerrisklevel=rules[0]["customer_risk_level"],in_trans_code_group=rules[0]["in_trans_code_group"],out_trans_code_group=rules[0]["out_trans_code_group"])

    @expose('/flowthrough/scatterplot',methods=['POST'])
    @has_access
    def getFlowthroughScatterPlotData(self):

    	flowthroughFolder = self.ACTIVITY_FLOW_THROUGH_FOLDER_PREFIX+'Flow'

    	dst_path = RULE_UPLOAD_FOLDER+flowthroughFolder+"/"+str(current_user.id)

    	dst_file = request.get_json()["filename"]

    	amtThreshNum = request.get_json()["amtThreshNum"]

    	lowerRatio = request.get_json()["lowerRatio"]

    	upperRatio = request.get_json()["upperRatio"]

    	#crDb = request.get_json()["crDb"]

    	def_volume_data = dst_path+"/"+dst_file

    	plot_data = pd.read_csv(def_volume_data,usecols=['ACCOUNT_KEY','YearMonth','Credit+TRANS_AMT','Debit+TRANS_AMT','outlier'])

    	#plot_data['TRANS_CNT'] = plot_data['Credit+TRANS_CNT'] + plot_data['Debit+TRANS_CNT']

    	plot_data = plot_data[['Debit+TRANS_AMT','Credit+TRANS_AMT','ACCOUNT_KEY','YearMonth','outlier']]

    	plot_data = plot_data[(plot_data['Debit+TRANS_AMT']>=100)&(plot_data['Credit+TRANS_AMT']>=100)]

    	plot_data['outlier'] = (plot_data['Debit+TRANS_AMT']+plot_data['Credit+TRANS_AMT']>=int(amtThreshNum))&((plot_data['Credit+TRANS_AMT']/plot_data['Debit+TRANS_AMT']*100.00)>=int(lowerRatio))&((plot_data['Credit+TRANS_AMT']/plot_data['Debit+TRANS_AMT']*100.00)<=int(upperRatio))

    	#plot_data = plot_data[(plot_data['Trans Code Type']==transDesc(transCode))&(plot_data['Cr_Db']==crDb)]

    	return Response(plot_data.to_json(orient='split'), mimetype='application/json')

    @expose('/flowthrough/scatterstatistics',methods=['POST'])
    @has_access
    def getFlowthroughScatterStatisticsData(self):

        flowthroughFolder = self.ACTIVITY_FLOW_THROUGH_FOLDER_PREFIX+'Flow'

        dst_path = RULE_UPLOAD_FOLDER+flowthroughFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

        threshold_below = request.get_json()["amtThreshNum"]

        threshold_above = request.get_json()["amtThreshNum2"]

        def_volume_data = dst_path+"/"+dst_file

        plot_data = pd.read_csv(def_volume_data,usecols=['ACCOUNT_KEY','YearMonth','Credit+TRANS_AMT','Debit+TRANS_AMT','outlier','Credit+TRANS_CNT','Debit+TRANS_CNT'])

        #plot_data = plot_data[['Debit+TRANS_AMT','Credit+TRANS_AMT','ACCOUNT_KEY','YearMonth','outlier']]
        #plot_data = plot_data.groupby(['ACCOUNT_KEY','Month of Trans Date'],as_index=False).sum()
        plot_data['Trans_Amt'] = plot_data['Debit+TRANS_AMT']+plot_data['Credit+TRANS_AMT']
        plot_data['Trans_Count'] = plot_data['Debit+TRANS_CNT']+plot_data['Credit+TRANS_CNT']
        #plot_data = plot_data[plot_data['Trans_Code_Type']==transDesc(transCode)]
        amount = np.round(plot_data['Trans_Amt'].sum(),decimals=2)
        count = plot_data['Trans_Count'].sum()

        plot_below = plot_data[(plot_data['Trans_Amt']>=int(threshold_below))]
        above_amount_below = np.round(plot_below['Trans_Amt'].sum(),decimals=2)
        above_count_below = plot_below['Trans_Count'].sum()
        below_amount_below = np.round(amount - above_amount_below,decimals=2)
        below_count_below = count - above_count_below
        percent_amount_below = np.round(above_amount_below*100/amount,decimals=2)
        percent_acount_below = np.round(above_count_below*100/count,decimals=2)

        plot_above = plot_data[(plot_data['Trans_Amt']>=int(threshold_above))]
        above_amount_above = np.round(plot_above['Trans_Amt'].sum(),decimals=2)
        above_count_above = plot_above['Trans_Count'].sum()
        below_amount_above = np.round(amount - above_amount_above,decimals=2)
        below_count_above = count - above_count_above
        percent_amount_above = np.round(above_amount_above*100/amount,decimals=2)
        percent_acount_above = np.round(above_count_above*100/count,decimals=2)

        return Response(pd.io.json.dumps({'amount':amount,'count':count,'above_amount_below':above_amount_below,'above_count_below':above_count_below,'below_amount_below':below_amount_below,'below_count_below':below_count_below,'percent_amount_below':percent_amount_below,'percent_acount_below':percent_acount_below,'above_amount_above':above_amount_above,'above_count_above':above_count_above,'below_amount_above':below_amount_above,'below_count_above':below_count_above,'percent_amount_above':percent_amount_above,'percent_acount_above':percent_acount_above}), mimetype='application/json')


    @expose('/flowthrough/tabledata',methods=['POST'])
    @has_access
    def getFlowthroughTableData(self):

        flowthroughFolder = self.ACTIVITY_FLOW_THROUGH_FOLDER_PREFIX+'Flow'

        dst_path = RULE_UPLOAD_FOLDER+flowthroughFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

    	#crDb = request.get_json()["crDb"]

        amtThreshold = request.get_json()["amtThreshNum"]

        amtThreshold2 = request.get_json()["amtThreshNum2"]

        lowerRatio = request.get_json()["lowerRatio"]

        upperRatio = request.get_json()["upperRatio"]

        def_volume_data = dst_path+"/"+dst_file

        table_data = pd.read_csv(def_volume_data,usecols=['ACCOUNT_KEY','YearMonth','Credit+TRANS_AMT','Debit+TRANS_AMT','TRANS_AMT','outlier'])

        table_data = table_data[(table_data['TRANS_AMT']>=int(amtThreshold))&((table_data['Credit+TRANS_AMT']/table_data['Debit+TRANS_AMT']*100.00)>=int(lowerRatio))&((table_data['Credit+TRANS_AMT']/table_data['Debit+TRANS_AMT']*100.00)<=int(upperRatio))] 	

        table_data['run2'] = np.where(table_data['TRANS_AMT']>=int(amtThreshold2), '1', '0')

        db_result = db.session.query(func.count(VizAlerts.account_key).label('count'),VizAlerts.account_key).join(User, VizAlerts.created_by_fk == User.id).group_by(VizAlerts.account_key).filter(VizUser.company_id==current_user.company_id)

        db_frame = pd.DataFrame(db_result.all(),columns=[column['name'] for column in db_result.column_descriptions])

        db_frame = db_frame.rename(str.upper, axis='columns')

        table_data = pd.merge(table_data,db_frame,how='left',on='ACCOUNT_KEY')

        table_data['ID'] = table_data.index	

        return Response(table_data.to_json(orient='records'), mimetype='application/json')

    @expose('/flowthrough/tablestatistics',methods=['POST'])
    @has_access
    def getFlowThoughTableStatistics(self):

        flowthroughFolder = self.ACTIVITY_FLOW_THROUGH_FOLDER_PREFIX+'Flow'

        dst_path = RULE_UPLOAD_FOLDER+flowthroughFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

        amtThreshold = request.get_json()["amtThreshNum"]

        amtThreshold2 = request.get_json()["amtThreshNum2"]

        lowerRatio = request.get_json()["lowerRatio"]

        upperRatio = request.get_json()["upperRatio"]

        def_volume_data = dst_path+"/"+dst_file

        table_data = pd.read_csv(def_volume_data,usecols=['ACCOUNT_KEY','YearMonth','Credit+TRANS_AMT','Debit+TRANS_AMT','TRANS_AMT','outlier'])

        table_data = table_data[(table_data['TRANS_AMT']>=int(amtThreshold))&((table_data['Credit+TRANS_AMT']/table_data['Debit+TRANS_AMT']*100.00)>=int(lowerRatio))&((table_data['Credit+TRANS_AMT']/table_data['Debit+TRANS_AMT']*100.00)<=int(upperRatio))]     

        table_data['run2'] = np.where(table_data['TRANS_AMT']>=int(amtThreshold2), '1', '0')

        db_result = db.session.query(func.count(Customer.id).label('count')).filter(Customer.company_id==current_user.company_id)

        db_result = [r._asdict() for r in db_result]

        total = db_result[0]["count"]

        run1_customer = table_data['ACCOUNT_KEY'].nunique()

        run1_customer_not = int(total)-int(run1_customer)

        run1_customer_percent = np.round(int(run1_customer)*100/total,decimals=2)

        run1_customer_percent_not = np.round(run1_customer_not*100/total,decimals=2)

        table_data2 = table_data[table_data['run2']=='1']

        run2_customer = table_data2['ACCOUNT_KEY'].nunique()

        run2_customer_not = int(total)-int(run2_customer)

        run2_customer_percent = np.round(int(run2_customer)*100/total,decimals=2)

        run2_customer_percent_not = np.round(run2_customer_not*100/total,decimals=2)

        return Response(pd.io.json.dumps({'total':total,'run1_customer':run1_customer,'run1_customer_percent':run1_customer_percent,'run2_customer':run2_customer,'run2_customer_percent':run2_customer_percent,'run1_customer_not':run1_customer_not,'run1_customer_percent_not':run1_customer_percent_not,'run2_customer_not':run2_customer_not,'run2_customer_percent_not':run2_customer_percent_not}), mimetype='application/json')

    @expose('/flowthrough/runDiff',methods=['POST'])
    @has_access
    def getFlowThroughRunDiff(self):

        flowthroughFolder = self.ACTIVITY_FLOW_THROUGH_FOLDER_PREFIX+'Flow'

        dst_path = RULE_UPLOAD_FOLDER+flowthroughFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

        amtThreshold = request.get_json()["amtThreshNum"]

        amtThreshold2 = request.get_json()["amtThreshNum2"]

        lowerRatio = request.get_json()["lowerRatio"]

        upperRatio = request.get_json()["upperRatio"]

        def_volume_data = dst_path+"/"+dst_file

        table_data = pd.read_csv(def_volume_data,usecols=['ACCOUNT_KEY','YearMonth','Credit+TRANS_AMT','Debit+TRANS_AMT','TRANS_AMT','outlier'])

        table_data = table_data[(table_data['TRANS_AMT']>=int(amtThreshold))&((table_data['Credit+TRANS_AMT']/table_data['Debit+TRANS_AMT']*100.00)>=int(lowerRatio))&((table_data['Credit+TRANS_AMT']/table_data['Debit+TRANS_AMT']*100.00)<=int(upperRatio))]     

        table_data['run2'] = np.where(table_data['TRANS_AMT']>=int(amtThreshold2), '1', '0')

        table_data_1 = table_data[table_data['run2']=='0']

        table_data_2 = table_data[table_data['run2']=='1']

        df_common = table_data_1.merge(table_data_2,on=['ACCOUNT_KEY'])

        table_data_3 = table_data_1[~table_data_1['ACCOUNT_KEY'].isin(df_common['ACCOUNT_KEY'])]

        rundiff = table_data_3.groupby(['ACCOUNT_KEY']).size().to_frame('size').reset_index()

        return Response(rundiff.to_json(orient='records'), mimetype='application/json')


    @expose('/flowthrough/alertdata',methods=['POST'])
    @has_access
    def createFlowThroughAlertData(self):

        rule_name = RuleEnum.FLow_Through_Activity_Pattern

        items = request.get_json()["items"]
        dataId = request.get_json()["dataId"]
        custType = request.get_json()["custType"]
        custRLel = request.get_json()["custRLel"]
        threshNum = request.get_json()["threshNum"]
        threshNum2 = request.get_json()["threshNum2"]
        circleName = request.get_json()["circleName"]
        runName = request.get_json()["runName"]

        circle = db.session.query(Circle.id).filter(Circle.name==circleName)

        if circle.count() == 0 :
            new_circle = Circle(name=circleName,company_id=current_user.company_id)
            self.appbuilder.get_session.add(new_circle)
            self.appbuilder.get_session.flush()
            circle_id = new_circle.id
        else :
            circle = [r._asdict() for r in circle]
            circle_id = circle[0]["id"]

        run = db.session.query(Run.id).filter(Run.circle_id==circle_id,Run.name==runName,Run.rule_group=='Flow_Through',Run.product_type=='ALL',Run.customer_type==custType,Run.customer_risk_level==custRLel,Run.current_threshold==threshNum,Run.testing_threshold==threshNum2,Run.current_cnt_threshold==0,Run.testing_cnt_threshold==0,Run.data_id==dataId)

        if run.count() == 0 :
            new_run = Run(circle_id=circle_id,name=runName,rule_group='Flow_Through',product_type='ALL',customer_type=custType,customer_risk_level=custRLel,current_threshold=threshNum,testing_threshold=threshNum2,current_cnt_threshold=0,testing_cnt_threshold=0,data_id=dataId)
            self.appbuilder.get_session.add(new_run)
            self.appbuilder.get_session.flush()
            run_id = new_run.id
        else :
            run = [r._asdict() for r in run]
            run_id = run[0]["id"]

        for item in items:

            alertdata = VizAlerts(run_id=run_id,company_id=current_user.company_id,account_key=item['ACCOUNT_KEY'], trans_month=item['YearMonth'], amount=item['TRANS_AMT'],rule_type=TypeEnum.Flow_Through,rule_status=StatusEnum.Open,trigger_rule=rule_name,current_step=ProcessEnum.Manager_Assign,operated_by_fk=current_user.id)
            self.appbuilder.get_session.add(alertdata)
            self.appbuilder.get_session.flush()
            alertproc = AlertProcess(alert_id=alertdata.id,process_type=ProcessEnum.Alert_Created,assigned_to_fk=current_user.id,syslog=Alert_Created.format(current_user.username,datetime.now(),rule_name.name,TypeEnum.High_Risk_Country.name,StatusEnum.Open.name))
            self.appbuilder.get_session.add(alertproc)

        self.appbuilder.get_session.commit()
        return  json.dumps({})

    @expose('/flowthrough/upload',methods=['POST','DELETE'])
    @has_access
    def getFlowthroughFileData(self):

        flowthroughFolder = self.ACTIVITY_FLOW_THROUGH_FOLDER_PREFIX+'Flow'

        dst_path = RULE_UPLOAD_FOLDER+flowthroughFolder+"/"+str(current_user.id)

        if request.method == 'POST':
            files = request.files['file']

            if files:
                filename = secure_filename(files.filename)

                mime_type = files.content_type

                if not self.allowed_file(files.filename):
                    result = uploadfile(name=filename, type=mime_type, size=0, not_allowed_msg="File type not allowed")

                else:
                    if not os.path.exists(dst_path):
                        os.makedirs(dst_path)
                    files.save(os.path.join((dst_path), filename))
                    """
                    self.s3.Object('vizrules', 'highRiskCountry/'+filename).put(Body=files)
                    """

        if request.method == 'DELETE':
            keyname = request.get_json()["keyname"]
            os.remove(dst_path+"/"+keyname)
            """
            bucket = self.s3.Bucket(self.bucket_name)
            for key in bucket.objects.all():
                 
                 words = key.key.split('/')
                 if len(words)==2 and words[0]=='highRiskCountry' and words[1]==keyname:
                     key.delete()
            """    

        return  json.dumps({})

class AlertView(BaseView):

    route_base = '/alerts'
    s3 = boto3.resource('s3')
    #datamodel = SQLAInterface(VizAlerts)

    """
    Alert Management
    """        

    @expose('/management/index')
    @has_access
    def alertMgt(self):

    	is_analysis_manager = isManager()

    	return self.render_template('alerts/alertMgt.html',is_analysis_manager=is_analysis_manager)

    @expose('/management/statuschart',methods=['POST'])
    @has_access
    def getStatusChartData(self):

        is_analysis_manager = isManager()

        if is_analysis_manager is True:
            status_result = db.session.query(func.count(VizAlerts.rule_status).label('count'),VizAlerts.rule_status.name).join(User, VizAlerts.created_by_fk == User.id).group_by(VizAlerts.rule_status).filter(VizUser.company_id==current_user.company_id)
        else:
            status_result = db.session.query(func.count(VizAlerts.rule_status).label('count'),VizAlerts.rule_status.name).group_by(VizAlerts.rule_status).filter(VizAlerts.operated_by_fk==current_user.id)
        status_result = [r for r in status_result]
        return Response(pd.io.json.dumps(status_result), mimetype='application/json')

    @expose('/management/dateagingchart',methods=['GET'])
    @has_access
    def getDateAgingChartData(self):

        is_analysis_manager = isManager()

        if is_analysis_manager is True:
            status_result = db.session.query(func.count(VizAlerts.id).label('count'),case([(func.date_part('day',func.current_date()-VizAlerts.created_on)<=20,'0~20'),(func.date_part('day',func.current_date()-VizAlerts.created_on)<=25,'20~25'),(func.date_part('day',func.current_date()-VizAlerts.created_on)<=29,'25~29'),(func.date_part('day',func.current_date()-VizAlerts.created_on)==30,'Due Today(30)')],else_='Past Due 31+').label('aging')).join(User, VizAlerts.created_by_fk == User.id).group_by(case([(func.date_part('day',func.current_date()-VizAlerts.created_on)<=20,'0~20'),(func.date_part('day',func.current_date()-VizAlerts.created_on)<=25,'20~25'),(func.date_part('day',func.current_date()-VizAlerts.created_on)<=29,'25~29'),(func.date_part('day',func.current_date()-VizAlerts.created_on)==30,'Due Today(30)')],else_='Past Due 31+')).filter(VizUser.company_id==current_user.company_id,VizAlerts.rule_status==StatusEnum.Open)
        else:
            status_result = db.session.query(func.count(VizAlerts.id).label('count'),case([(func.date_part('day',func.current_date()-VizAlerts.created_on)<=20,'0~20'),(func.date_part('day',func.current_date()-VizAlerts.created_on)<=25,'20~25'),(func.date_part('day',func.current_date()-VizAlerts.created_on)<=29,'25~29'),(func.date_part('day',func.current_date()-VizAlerts.created_on)==30,'Due Today(30)')],else_='Past Due 31+').label('aging')).group_by(case([(func.date_part('day',func.current_date()-VizAlerts.created_on)<=20,'0~20'),(func.date_part('day',func.current_date()-VizAlerts.created_on)<=25,'20~25'),(func.date_part('day',func.current_date()-VizAlerts.created_on)<=29,'25~29'),(func.date_part('day',func.current_date()-VizAlerts.created_on)==30,'Due Today(30)')],else_='Past Due 31+')).filter(VizAlerts.operated_by_fk==current_user.id,VizAlerts.rule_status==StatusEnum.Open)
        status_result = [r._asdict() for r in status_result]

        print(status_result)
        return Response(pd.io.json.dumps(status_result), mimetype='application/json')

    @expose('/management/typechart',methods=['POST'])
    @has_access
    def getTypeChartData(self):

        is_analysis_manager = isManager()

        if is_analysis_manager is True:
            type_result = db.session.query(func.count(VizAlerts.rule_type).label('count'),VizAlerts.rule_type.name).join(User, VizAlerts.created_by_fk == User.id).group_by(VizAlerts.rule_type).filter(VizUser.company_id==current_user.company_id,VizAlerts.rule_status==StatusEnum.Open)
        else:
            type_result = db.session.query(func.count(VizAlerts.rule_type).label('count'),VizAlerts.rule_type.name).group_by(VizAlerts.rule_type).filter(VizAlerts.operated_by_fk==current_user.id,VizAlerts.rule_status==StatusEnum.Open)
        type_result = [r for r in type_result]
        return Response(pd.io.json.dumps(type_result), mimetype='application/json')

    @expose('/management/cusalertstop10',methods=['POST'])
    @has_access
    def getCustomerAlertTop10(self):

        is_analysis_manager = isManager()

        if is_analysis_manager is True:
            type_result = db.session.query(func.count(VizAlerts.id).label('count'),VizAlerts.account_key).join(User, VizAlerts.created_by_fk == User.id).group_by(VizAlerts.account_key).filter(VizUser.company_id==current_user.company_id,VizAlerts.rule_status==StatusEnum.Open).order_by(func.count(VizAlerts.id).desc()).having(func.count(VizAlerts.id) <= 10)
        else:
            type_result = db.session.query(func.count(VizAlerts.id).label('count'),VizAlerts.account_key).group_by(VizAlerts.account_key).filter(VizAlerts.operated_by_fk==current_user.id,VizAlerts.rule_status==StatusEnum.Open).order_by(func.count(VizAlerts.id).desc()).having(func.count(VizAlerts.id) <= 10)
        type_result = [r for r in type_result]
        return Response(pd.io.json.dumps(type_result), mimetype='application/json')

    #only for manager
    @expose('/management/barchart/<run>',methods=['POST'])
    @has_access
    def getBarChartData(self,run):

        #type_result = db.session.query(func.count(VizAlerts.rule_status).label('count'),User.username,VizAlerts.rule_status.name).outerjoin(User, VizAlerts.operated_by_fk == User.id).group_by(User.id,User.username,VizAlerts.rule_status).filter(VizUser.company_id==current_user.company_id).order_by(User.id)
        is_analysis_manager = isManager()

        if is_analysis_manager is True:
            type_result = db.session.query(func.count(VizAlerts.id).label('count'),VizAlerts.rule_type.name,VizAlerts.rule_status.name).outerjoin(User, VizAlerts.operated_by_fk == User.id).group_by(VizAlerts.rule_type,VizAlerts.rule_status).filter(VizAlerts.run_id == run,VizUser.company_id==current_user.company_id).order_by(VizAlerts.rule_type)
        else:
            type_result = db.session.query(func.count(VizAlerts.id).label('count'),VizAlerts.rule_type.name,VizAlerts.rule_status.name).outerjoin(User, VizAlerts.operated_by_fk == User.id).group_by(VizAlerts.rule_type,VizAlerts.rule_status).filter(VizAlerts.run_id == run,VizAlerts.operated_by_fk==current_user.id).order_by(VizAlerts.rule_type)
        type_result = [r for r in type_result]
        return Response(pd.io.json.dumps(type_result), mimetype='application/json')

    @expose('/management/gettabledata/<run>/<status>',methods=['GET'])
    @has_access
    def getAlertTableData(self,run,status):

        data_result = []

        is_analysis_manager = isManager()

        if is_analysis_manager is True:
            alert_result = db.session.query(VizAlerts.id,VizAlerts.rule_type.name,VizAlerts.account_key,VizAlerts.trans_month,VizAlerts.country_abbr,VizAlerts.country_name,VizAlerts.amount,VizAlerts.cnt,VizAlerts.rule_status.name,User.id.label('uid'),User.username,VizAlerts.trigger_rule.name,func.to_char(VizAlerts.created_on, 'YYYY-MM-DD HH24:MI:SS').label("created_on"),func.to_char(VizAlerts.finished_on, 'YYYY-MM-DD HH24:MI:SS').label("finished_on"),VizAlerts.current_step.name,Circle.name.label('cycle_name'),Run.name.label('run_name'),Run.rule_group,Run.product_type,Run.customer_type,Run.customer_risk_level,Run.current_threshold,Run.testing_threshold,Run.data_id).join(User, VizAlerts.operated_by_fk == User.id).outerjoin(Run,VizAlerts.run_id == Run.id).outerjoin(Circle,Run.circle_id == Circle.id).filter(VizAlerts.run_id == run,VizUser.company_id==current_user.company_id).order_by(VizAlerts.operated_on.desc())
        else:            
            alert_result = db.session.query(VizAlerts.id,VizAlerts.rule_type.name,VizAlerts.account_key,VizAlerts.trans_month,VizAlerts.country_abbr,VizAlerts.country_name,VizAlerts.amount,VizAlerts.cnt,VizAlerts.rule_status.name,User.id.label('uid'),User.username,VizAlerts.trigger_rule.name,func.to_char(VizAlerts.created_on, 'YYYY-MM-DD HH24:MI:SS').label("created_on"),func.to_char(VizAlerts.finished_on, 'YYYY-MM-DD HH24:MI:SS').label("finished_on"),VizAlerts.current_step.name,Circle.name.label('cycle_name'),Run.name.label('run_name'),Run.rule_group,Run.product_type,Run.customer_type,Run.customer_risk_level,Run.current_threshold,Run.testing_threshold,Run.data_id).join(User, VizAlerts.operated_by_fk == User.id).outerjoin(Run,VizAlerts.run_id == Run.id).outerjoin(Circle,Run.circle_id == Circle.id).filter(VizAlerts.run_id == run,VizAlerts.operated_by_fk==current_user.id).order_by(VizAlerts.operated_on.desc())

        if status!='0':
            alert_result = alert_result.filter(VizAlerts.rule_type==status)

        data_result = [r._asdict() for r in alert_result]

        return Response(pd.io.json.dumps(data_result), mimetype='application/json')

    @expose('/management/getanalystsbycompany',methods=['GET'])
    @has_access
    def getAnalystsByCompany(self):

        data_result = []

        is_analysis_manager = isManager()

        sql = text('select a.id,a.username from ab_user a left join ab_user_role b on a.id=b.user_id where b.role_id in ('+ASSIGN_USER_ROLE+') and a.company_id='+str(current_user.company_id)+' order by a.id')
        result = db.engine.execute(sql)
        for row in result:
            data_result.append({'value':row['id'],'text':row['username']})
        result.close()

        return Response(pd.io.json.dumps(data_result), mimetype='application/json')

    @expose('/management/assignanalyst',methods=['POST'])
    @has_access
    def assignAnalyst(self):

        alert_id = request.form["hid_alertid"]
        comment = request.form["assginCommentTextArea"]
        analyst = request.form["assignCtl"]

        alert_id_list = alert_id.split(',')

        for aid in alert_id_list:
        
            user_result = db.session.query(User.username).filter(User.id==analyst).one()
            assginedUser = [r for r in user_result]

            alertProcess = AlertProcess(alert_id=aid, assigned_to_fk=analyst, assigned_on=func.now(), process_type=ProcessEnum.Manager_Assign, syslog=Manager_Assign.format(current_user.username,assginedUser[0],datetime.now()))
            self.appbuilder.get_session.add(alertProcess)
            self.appbuilder.get_session.flush()
            process_id = alertProcess.id

            proComment = AlertProcessComments(process_id=process_id, comment=comment)
            self.appbuilder.get_session.add(proComment)
            viz_alert = self.appbuilder.get_session.query(VizAlerts).filter(VizAlerts.id==aid).update({'operated_by_fk':analyst,'operated_on':datetime.now(),'current_step':ProcessEnum.Analyst_Process})
        
        self.appbuilder.get_session.commit()

        return Response(pd.io.json.dumps({}), mimetype='application/json')

    @expose('/management/getcurrentnote',methods=['POST'])
    @has_access
    def getCurrentNote(self):

        data_result = []

        alert_id = request.get_json()["alertid"]

        procss_sub = db.session.query(AlertProcess.id,AlertProcess.alert_id).filter(AlertProcess.alert_id==alert_id,AlertProcess.process_type==ProcessEnum.Analyst_Process).subquery()

        alert_result = db.session.query(VizAlerts.id,VizAlerts.rule_status.name,AlertProcessComments.comment,procss_sub.c.id.label('pid')).outerjoin(procss_sub, VizAlerts.id==procss_sub.c.alert_id).outerjoin(AlertProcessComments, procss_sub.c.id==AlertProcessComments.process_id).filter(VizAlerts.id==alert_id)

        data_result = [r._asdict() for r in alert_result][0]

        return Response(pd.io.json.dumps(data_result), mimetype='application/json')

    @expose('/management/addnote',methods=['POST'])
    @has_access
    def addNote(self):

        alert_id = request.get_json()["alert_id"]
        process_id = request.get_json()["process_id"]
        comment = request.get_json()["comment"]
        attachment = request.get_json()["attached"]
        status = request.get_json()["status"]
        alert_status = StatusEnum.Close_False
        full_attached_path = ''
        if status is True:
            alert_status = StatusEnum.Close_True

        if not process_id:
           alertProcess = AlertProcess(alert_id=alert_id, process_type=ProcessEnum.Analyst_Process, syslog=Analyst_Process.format(current_user.username,datetime.now(),alert_status.name,comment))
           self.appbuilder.get_session.add(alertProcess)
           self.appbuilder.get_session.flush()
           process_id = alertProcess.id

        proComment = AlertProcessComments(process_id=process_id, comment=comment)
        self.appbuilder.get_session.add(proComment)
        self.appbuilder.get_session.flush()
        comment_id=proComment.id
        if attachment:
            full_attached_path = 'alerts/'+str(alert_id)+"/"+str(process_id)+"/"+str(comment_id)+"/"+attachment
            bucket = self.s3.Bucket(S3_BUCKET_RULES)
            bucket.copy({'Bucket': S3_BUCKET_RULES, 'Key': 'alerts/'+str(alert_id)+"/"+attachment}, full_attached_path)
            bucket.delete_objects(Delete={'Objects': [{'Key': 'alerts/'+str(alert_id)+"/"+attachment}]})
            self.s3.Object(S3_BUCKET_RULES,full_attached_path).Acl().put(ACL='public-read')
            self.appbuilder.get_session.query(AlertProcessComments).filter(AlertProcessComments.id==comment_id).update({'attachment':full_attached_path})
        self.appbuilder.get_session.query(VizAlerts).filter(VizAlerts.id==alert_id,VizAlerts.current_step!=None).update({'rule_status':alert_status,'operated_on':datetime.now(),'finished_on':datetime.now(),'current_step':None})
        self.appbuilder.get_session.commit()

        return Response(pd.io.json.dumps({}), mimetype='application/json')

    @expose('/management/prioralert',methods=['POST'])
    @has_access
    def getPriorAlertData(self):

        account_key = request.get_json()["account_key"]

        data_result = db.session.query(func.count(VizAlerts.rule_type).label('count'),VizAlerts.rule_type).join(User, VizAlerts.created_by_fk == User.id).group_by(VizAlerts.rule_type).filter(VizUser.company_id==current_user.company_id,VizAlerts.account_key==account_key)

        data_result = [r._asdict() for r in data_result]

        print(data_result)

        return Response(pd.io.json.dumps(data_result), mimetype='application/json')

    @expose('/management/alertDetail/<aid>',methods=['GET'])
    @has_access
    def getAlertDetail(self,aid):

        creator = aliased(User)
        operator = aliased(User)
        assigner = aliased(User)

        alert_result = db.session.query(VizAlerts.id,VizAlerts.rule_type.name,VizAlerts.account_key,VizAlerts.trans_month,VizAlerts.country_abbr,VizAlerts.country_name,VizAlerts.amount,VizAlerts.cnt,VizAlerts.rule_status.name,creator.username.label('cuid'),operator.username.label('ouid'),VizAlerts.trigger_rule.name,func.to_char(VizAlerts.created_on, 'YYYY-MM-DD HH24:MI:SS').label("created_on"),func.to_char(VizAlerts.operated_on, 'YYYY-MM-DD HH24:MI:SS').label("operated_on"),func.to_char(VizAlerts.finished_on, 'YYYY-MM-DD HH24:MI:SS').label("finished_on"),VizAlerts.current_step.name,AlertProcess.process_type.name,AlertProcess.syslog,func.to_char(AlertProcess.assigned_on, 'YYYY-MM-DD HH24:MI:SS').label("assigned_on"),assigner.username.label("assigner"),AlertProcess.id.label('pid')).outerjoin(AlertProcess, VizAlerts.id == AlertProcess.alert_id).join(creator, VizAlerts.created_by_fk == creator.id).join(operator, VizAlerts.operated_by_fk == operator.id).join(assigner, AlertProcess.created_by_fk == assigner.id).filter(VizAlerts.id==aid).order_by(AlertProcess.created_on.desc())

        data_result = [r._asdict() for r in alert_result]

        return Response(pd.io.json.dumps(data_result), mimetype='application/json')

    @expose('/management/procescomments/<pid>',methods=['GET'])
    @has_access
    def getProcesComments(self,pid):

        creator = aliased(User)

        alert_result = db.session.query(AlertProcessComments.comment,AlertProcessComments.attachment,func.to_char(AlertProcessComments.created_on, 'YYYY-MM-DD HH24:MI:SS').label("created_on"),creator.username.label("creator")).join(creator, AlertProcessComments.created_by_fk == creator.id).filter(AlertProcessComments.process_id==pid).order_by(AlertProcessComments.created_on.desc())

        data_result = [r._asdict() for r in alert_result]

        return Response(pd.io.json.dumps(data_result), mimetype='application/json')

    @expose('/management/procescomments/<aid>/<step>',methods=['GET'])
    @has_access
    def getProcesCommentsByStep(self,aid,step):

        creator = aliased(User)

        alert_result = db.session.query(AlertProcess.assigned_to_fk,AlertProcessComments.comment,AlertProcessComments.attachment,func.to_char(AlertProcessComments.created_on, 'YYYY-MM-DD HH24:MI:SS').label("created_on"),creator.username.label("creator")).outerjoin(AlertProcessComments,AlertProcess.id==AlertProcessComments.process_id).join(creator, AlertProcessComments.created_by_fk == creator.id).filter(AlertProcess.alert_id==aid,AlertProcess.process_type==step).order_by(AlertProcessComments.created_on.desc())

        data_result = [r._asdict() for r in alert_result]

        if step=='Manager_Assign' and not data_result :
            alert_result = db.session.query(VizAlerts.operated_by_fk,User.username,bindparam('comment',value='')).join(User,VizAlerts.operated_by_fk==User.id).filter(VizAlerts.id==aid)
            data_result = [r._asdict() for r in alert_result]

        return Response(pd.io.json.dumps(data_result), mimetype='application/json')

    @expose('/management/upload/<aid>/<cid>',methods=['POST','DELETE'])
    @has_access
    def uploadFile2S3(self,aid,cid):

        if request.method == 'POST':
            files = request.files['file']

            if files:
                filename = secure_filename(files.filename)

                if cid=='0':
                    bucket = self.s3.Bucket(S3_BUCKET_RULES)
                    for obj in bucket.objects.filter(Prefix='alerts/'+aid):
                        if len(obj.key.split("/"))==3:
                            print( obj.key )
                            obj.delete()
                    


                """
                mime_type = files.content_type

                if not self.allowed_file(files.filename):
                    result = uploadfile(name=filename, type=mime_type, size=0, not_allowed_msg="File type not allowed")

                else:
                    if not os.path.exists(dst_path):
                        os.makedirs(dst_path)
                    files.save(os.path.join((dst_path), filename))
                """
                self.s3.Object(S3_BUCKET_RULES, 'alerts/'+aid+"/"+filename).put(Body=files)


        if request.method == 'DELETE':
            keyname = request.get_json()["keyname"]
            if cid=='0':
                bucket = self.s3.Bucket(S3_BUCKET_RULES)
                for obj in bucket.objects.filter(Prefix='alerts/'+aid+'/'+keyname):
                    obj.delete()
            """
            bucket = self.s3.Bucket(self.bucket_name)
            for key in bucket.objects.all():
                 
                 words = key.key.split('/')
                 if len(words)==2 and words[0]=='highRiskCountry' and words[1]==keyname:
                     key.delete()
            """    

        return  json.dumps({})

    @expose('/management/initTrans',methods=['GET'])
    @has_access
    def initTrans(self):

        trans_data = pd.read_csv(RULE_DEFAULT_FOLDER+'/initb.csv')

        for index, row in trans_data.iterrows():
            tran = Transanction(trans_no=row['TransNo'], customer_id=row['CustomerID'], account_key=row['AccountKey'], account_key10=row['AccountKey10'], trans_amt=row['TransAmt'], trans_code=row['TransCode'], is_cash_trans=row['IsCashTrans']
                , trans_date=row['TransDate'], bene_name=('' if pd.isna(row['BeneName']) else row['BeneName']), bene_country=('' if pd.isna(row['BeneCountry']) else row['BeneCountry']), bene_bank_country=('' if pd.isna(row['BeneBankCountry']) else row['BeneBankCountry']), by_order_name=('' if pd.isna(row['ByOrderName']) else row['ByOrderName'])
                , by_order_country=('' if pd.isna(row['ByOrderCountry']) else row['ByOrderCountry']), by_order_bank_country=('' if pd.isna(row['ByOrderBankCountry']) else row['ByOrderBankCountry']))
            self.appbuilder.get_session.add(tran)
        self.appbuilder.get_session.commit()

        return  json.dumps({})


    @expose('/management/getTrans/<custid>',methods=['GET'])
    @has_access
    def getTransByCust(self,custid):

        print(custid)

        trans_result = db.session.query(Transanction.id,Transanction.customer_id,Transanction.account_key,Transanction.account_key10,Transanction.trans_amt,Transanction.trans_code
            ,Transanction.trans_date,Transanction.bene_name,Transanction.bene_country,Transanction.bene_bank_country,Transanction.by_order_name
            ,Transanction.by_order_country,Transanction.by_order_bank_country).filter(Transanction.customer_id==custid).order_by(Transanction.trans_date.desc())

        data_result = [r._asdict() for r in trans_result]

        return Response(pd.io.json.dumps(data_result), mimetype='application/json')


    @expose('/management/getCycleData',methods=['GET'])
    @has_access
    def getCycleData(self):

        trans_result = db.session.query(Circle.id,Circle.name).filter(Circle.company_id==current_user.company_id).order_by(Circle.id)

        data_result = [r._asdict() for r in trans_result]

        return Response(pd.io.json.dumps(data_result), mimetype='application/json')

    @expose('/management/getRunDataByCycle/<cycleid>',methods=['GET'])
    @has_access
    def getRunDataByCycle(self,cycleid):

        trans_result = db.session.query(Run.id,func.concat(Run.id,'-',Run.name).label('name')).filter(Run.circle_id==cycleid).order_by(Run.id)

        data_result = [r._asdict() for r in trans_result]

        return Response(pd.io.json.dumps(data_result), mimetype='application/json')

    @expose('/archive')
    @has_access
    def alertArchiveMgt(self):

        is_analysis_manager = isManager()

        return self.render_template('alerts/alertArchive.html',is_analysis_manager=is_analysis_manager)

    @expose('/archive/gettabledata',methods=['GET'])
    @has_access
    def getArchiveData(self):

        data_result = []

        is_analysis_manager = isManager()

        if is_analysis_manager is True:
            alert_result = db.session.query(VizAlerts.id,VizAlerts.rule_type.name,VizAlerts.account_key,VizAlerts.trans_month,VizAlerts.country_abbr,VizAlerts.country_name,VizAlerts.amount,VizAlerts.cnt,VizAlerts.rule_status.name,User.id.label('uid'),User.username,VizAlerts.trigger_rule.name,func.to_char(VizAlerts.created_on, 'YYYY-MM-DD HH24:MI:SS').label("created_on"),func.to_char(VizAlerts.finished_on, 'YYYY-MM-DD HH24:MI:SS').label("finished_on"),VizAlerts.current_step.name).join(User, VizAlerts.operated_by_fk == User.id).filter(VizUser.company_id==current_user.company_id,VizAlerts.current_step == None).order_by(VizAlerts.operated_on.desc())
        else:
            alert_result = db.session.query(VizAlerts.id,VizAlerts.rule_type.name,VizAlerts.account_key,VizAlerts.trans_month,VizAlerts.country_abbr,VizAlerts.country_name,VizAlerts.amount,VizAlerts.cnt,VizAlerts.rule_status.name,User.id.label('uid'),User.username,VizAlerts.trigger_rule.name,func.to_char(VizAlerts.created_on, 'YYYY-MM-DD HH24:MI:SS').label("created_on"),func.to_char(VizAlerts.finished_on, 'YYYY-MM-DD HH24:MI:SS').label("finished_on"),VizAlerts.current_step.name).join(User, VizAlerts.operated_by_fk == User.id).filter(VizAlerts.operated_by_fk==current_user.id,VizAlerts.current_step == None).order_by(VizAlerts.operated_on.desc())
        
        data_result = [r._asdict() for r in alert_result]

        return Response(pd.io.json.dumps(data_result), mimetype='application/json')

class DataCenterView(BaseView):

    route_base = '/datacenter'
    s3 = boto3.resource('s3')

    @expose('/bankdata/tb/index')
    @has_access
    def bankdatatd(self):

        return self.render_template('datacenter/bankdataTB.html')

    @expose('/bankdata/tb/upload',methods=['POST'])
    @has_access
    def bankdatatdupload(self):

        #dst_path = RULE_UPLOAD_FOLDER+str(current_user.company_id)

        if request.method == 'POST':
            files = request.files['file']

            if files:
                filename = secure_filename(files.filename)
                full_attached_path = getCompanyName()+"/"+str(current_user.id)
                bucket = self.s3.Bucket(S3_BUCKET_COMPANYS)
                self.s3.Object(S3_BUCKET_COMPANYS, full_attached_path+"/"+filename).put(Body=files)

                row = UploadHis(file_path=full_attached_path,file_name=filename)
                self.appbuilder.get_session.add(row)
                self.appbuilder.get_session.commit() 
 

        return  Response(pd.io.json.dumps({'id':row.id}), mimetype='application/json')

    @expose('/bankdata/uploadhis',methods=['GET','POST','PUT'])
    @has_access
    def getuploadhis(self):

        if request.method == 'GET':

            TargetFile = aliased(UploadHis)
            SourceFile = aliased(UploadHis)

            his_result = db.session.query(ValidHis.id,TargetFile.id.label("target_id"),TargetFile.file_name.label("target_file_name"),SourceFile.id.label("source_id"),SourceFile.file_name.label("source_file_name"),ValidHis.start_date,ValidHis.end_date,func.to_char(ValidHis.created_on, 'YYYY-MM-DD HH24:MI:SS').label("created_on"),case([(ValidHis.customer_valid==0,'Fail'),(ValidHis.customer_valid==1,'Pass')],else_='-').label("customer_valid"),ValidHis.id.label("source_id"),case([(ValidHis.account_valid==0,'Fail'),(ValidHis.account_valid==1,'Pass')],else_='-').label("account_valid"),case([(ValidHis.transaction_valid==0,'Fail'),(ValidHis.transaction_valid==1,'Pass')],else_='-').label("transaction_valid"),ValidHis.id.label("alert_id"),User.username).join(TargetFile, ValidHis.target_file_id == TargetFile.id).join(SourceFile, ValidHis.source_file_id == SourceFile.id).join(User, ValidHis.created_by_fk == User.id).filter(ValidHis.company_id==current_user.company_id).order_by(ValidHis.created_on.desc())

            his_result = [r._asdict() for r in his_result]

            return Response(pd.io.json.dumps(his_result), mimetype='application/json')

        if request.method == 'POST':

            start_date = request.get_json()["start_date"]
            end_date = request.get_json()["end_date"]
            targetid = request.get_json()["targetid"]
            sourceid = request.get_json()["sourceid"]

            validhis = ValidHis(company_id=current_user.company_id,source_file_id=sourceid, target_file_id=targetid, start_date=start_date, end_date = end_date)
            self.appbuilder.get_session.add(validhis)
            self.appbuilder.get_session.commit()
            return  json.dumps({})

        if request.method == 'PUT':

            his_id = request.get_json()["his_id"]
            customer_valid = request.get_json()["customer_valid"]
            account_valid = request.get_json()["account_valid"]
            transaction_valid = request.get_json()["transaction_valid"]

            validhis = self.appbuilder.get_session.query(ValidHis).filter(ValidHis.id==his_id).update({"customer_valid":customer_valid, "account_valid":account_valid, "transaction_valid":transaction_valid})

            self.appbuilder.get_session.commit()
            return  json.dumps({})

    @expose('/bankdata/download/<id>',methods=['GET'])
    @has_access
    def bankddatatbdownload(self,id):

        his_result = db.session.query(UploadHis.id,UploadHis.file_path,UploadHis.file_name).filter(UploadHis.id==id)

        his_result = [r._asdict() for r in his_result]

        full_file_path = his_result[0]['file_path']+"/"+his_result[0]['file_name']     

        file = self.s3.Object(S3_BUCKET_COMPANYS, full_file_path).get() 

        response = make_response(file['Body'].read())    

        response.headers["Content-Disposition"] = "attachment; filename={0}".format(his_result[0]['file_name'])   

        response.mimetype = file['ContentType']

        return response

    @expose('/rules/index')
    @has_access
    def rulesIndex(self):

        is_admin = isAdmin()

        companies = []

        if is_admin is True:
            companies = db.session.query(Company.id,Company.name).order_by(Company.id)
        else:
            companies = db.session.query(Company.id,Company.name).filter(Company.id==current_user.company_id).order_by(Company.id)

        companies = [r._asdict() for r in companies]

        return self.render_template('datacenter/rules_config.html',companies=companies)

    @expose('/rules/getRuleByCompany/<company>')
    @has_access
    def getRuleByCompany(self,company):

        rule_groups = []

        rules = []

        result = dict()

        rule_num = db.session.query(func.count(Rules.id).label('count')).filter(Rules.company_id==company)

        rule_num = [r._asdict() for r in rule_num]

        print(rule_num)

        if rule_num[0]['count'] == 0: 

            rule_data = pd.read_csv(RULE_DEFAULT_FOLDER+'/initRule.csv')

            for index, row in rule_data.iterrows():
                rule = Rules(company_id=company, rule_code=row['RuleCode'], rule_group=row['RuleGroup'], product_type=row['ProductType'], viz_template=row['VizTemplate'], rule_description_short=row['RuleDescShort'], rule_description=('' if pd.isna(row['RuleDescription']) else row['RuleDescription']), rule_type=('' if pd.isna(row['Type']) else row['Type'])
                    , susp_type=('' if pd.isna(row['SuspType']) else row['SuspType']), schedule=('' if pd.isna(row['Schedule']) else row['Schedule']), viz_schedule=('' if pd.isna(row['VizSchedule']) else row['VizSchedule']), pre_post_EOD=('' if pd.isna(row['PrePostEOD']) else row['PrePostEOD']), cust_acct=('' if pd.isna(row['CustAcct']) else row['CustAcct']), template_rule=('' if pd.isna(row['TemplateRule']) else row['TemplateRule'])
                    , time_horizon=('' if pd.isna(row['TimeHorizon']) else row['TimeHorizon']), customer_type=('' if pd.isna(row['CustomerType']) else row['CustomerType']), customer_risk_level=('' if pd.isna(row['CustomerRiskLevel']) else row['CustomerRiskLevel']), customer_risk_class=('' if pd.isna(row['CustomerRiskClass']) else row['CustomerRiskClass']), min_trans_no=(-1 if pd.isna(row['Min_Trans_No']) else row['Min_Trans_No']), min_ind_trans_amt=(-1 if pd.isna(row['Min_Ind_Trans_Amt']) else row['Min_Ind_Trans_Amt'])
                    , max_ind_trans_amt=(-1 if pd.isna(row['Max_Ind_Trans_Amt']) else row['Max_Ind_Trans_Amt']), min_agg_trans_amt=(-1 if pd.isna(row['Min_Agg_Trans_Amt']) else row['Min_Agg_Trans_Amt']), max_agg_trans_amt=(-1 if pd.isna(row['Max_Agg_Trans_Amt']) else row['Max_Agg_Trans_Amt']), additional=('' if pd.isna(row['Additional']) else row['Additional']), cash_ind=(-1 if pd.isna(row['Cash_Ind']) else row['Cash_Ind']), trans_code=('' if pd.isna(row['Trans_Code']) else row['Trans_Code'])
                    , trans_code_group=('' if pd.isna(row['Trans_Code_Group']) else row['Trans_Code_Group']), in_cash_ind=(-1 if pd.isna(row['In_Cash_Ind']) else row['In_Cash_Ind']), in_trans_code=('' if pd.isna(row['In_Trans_Code']) else row['In_Trans_Code']), in_trans_code_group=('' if pd.isna(row['In_Trans_Code_Group']) else row['In_Trans_Code_Group']), out_cash_ind=(-1 if pd.isna(row['Out_Cash_Ind']) else row['Out_Cash_Ind']), out_trans_code=('' if pd.isna(row['Out_Trans_Code']) else row['Out_Trans_Code'])
                    , out_trans_code_group=('' if pd.isna(row['Out_Trans_Code_Group']) else row['Out_Trans_Code_Group']), in_out_ratio_min=(-1 if pd.isna(row['In_Out_Ratio_Min']) else row['In_Out_Ratio_Min']*100.00), in_out_ratio_max=(-1 if pd.isna(row['In_Out_Ratio_Max']) else row['In_Out_Ratio_Max']*100.00))
                self.appbuilder.get_session.add(rule)
            self.appbuilder.get_session.commit()

        rule_groups = db.session.query(Rules.rule_group).distinct().order_by(Rules.rule_group)

        rule_groups = [r._asdict() for r in rule_groups]

        rules = db.session.query(Rules.id,Rules.company_id,Rules.rule_code,Rules.rule_group,Rules.product_type,Rules.viz_template,Rules.rule_description_short,Rules.rule_description,Rules.susp_type,Rules.schedule,Rules.viz_schedule,
            Rules.pre_post_EOD,Rules.cust_acct,Rules.template_rule,Rules.time_horizon,Rules.customer_type,Rules.customer_risk_level,Rules.customer_risk_class,Rules.min_trans_no,Rules.min_ind_trans_amt,
            Rules.max_ind_trans_amt,Rules.min_agg_trans_amt,Rules.max_agg_trans_amt,Rules.additional,Rules.cash_ind,Rules.trans_code,Rules.trans_code_group,Rules.in_cash_ind,Rules.in_trans_code,
            Rules.in_trans_code_group,Rules.out_cash_ind,Rules.out_trans_code,Rules.out_trans_code_group,Rules.in_out_ratio_min,Rules.in_out_ratio_max,Rules.is_seleced).filter(Rules.company_id==company).order_by(Rules.rule_group,Rules.id)

        rules = [r._asdict() for r in rules]

        for group in rule_groups:
            result[group['rule_group']]=[]
            for rule in rules:
                if group['rule_group'] == rule['rule_group']:
                    result[group['rule_group']].append(rule)
                if rule["rule_code"]=='blvelshwir':
                    print(rule)

        return Response(pd.io.json.dumps(result), mimetype='application/json')

    @expose('/rules/<rule_id>')
    @has_access
    def getRuleById(self,rule_id):

        rule = db.session.query(Rules).filter(Rules.id==rule_id).first()

        return Response(json.dumps(rule.__dict__, default = jsonconverter), mimetype='application/json')

class HomeView(BaseView):

    route_base = '/home'

    @expose('/alerts/monthPerf',methods=['GET'])
    @has_access
    def getMonthPerformanceData(self):

        data_result = []

        is_analysis_manager = isManager()

        if is_analysis_manager is True:
            alert_result = db.session.query(func.to_char(VizAlerts.created_on, 'YYYYMM').label('month'),VizAlerts.rule_status,func.count(VizAlerts.id).label("count")).join(User, VizAlerts.operated_by_fk == User.id).filter(VizUser.company_id==current_user.company_id).group_by(func.to_char(VizAlerts.created_on, 'YYYYMM'),VizAlerts.rule_status).order_by(func.to_char(VizAlerts.created_on, 'YYYYMM'))
        else:
            alert_result = db.session.query(func.to_char(VizAlerts.created_on, 'YYYYMM').label('month'),VizAlerts.rule_status,func.count(VizAlerts.id).label("count")).join(User, VizAlerts.operated_by_fk == User.id).filter(VizAlerts.operated_by_fk==current_user.id).group_by(func.to_char(VizAlerts.created_on, 'YYYYMM'),VizAlerts.rule_status).order_by(func.to_char(VizAlerts.created_on, 'YYYYMM'))
        
        data_result = [r._asdict() for r in alert_result]

        return Response(pd.io.json.dumps(data_result), mimetype='application/json')

    @expose('/alerts/monthYields',methods=['GET'])
    @has_access
    def getMonthYieldsData(self):

        data_result = []

        is_analysis_manager = isManager()

        if is_analysis_manager is True:
            alert_result = db.session.query(func.to_char(VizAlerts.created_on, 'YYYYMM').label('month'),case([(func.count(VizAlerts.id)==0,0)],else_=(func.sum(case([(VizAlerts.rule_status==StatusEnum.Close_True,1)],else_=0))*100.00/func.count(VizAlerts.id))).label("ratio")).join(User, VizAlerts.operated_by_fk == User.id).filter(VizUser.company_id==current_user.company_id).group_by(func.to_char(VizAlerts.created_on, 'YYYYMM')).order_by(func.to_char(VizAlerts.created_on, 'YYYYMM'))
        else:
            alert_result = db.session.query(func.to_char(VizAlerts.created_on, 'YYYYMM').label('month'),case([(func.count(VizAlerts.id)==0,0)],else_=(func.sum(case([(VizAlerts.rule_status==StatusEnum.Close_True,1)],else_=0))*100.00/func.count(VizAlerts.id))).label("ratio")).join(User, VizAlerts.operated_by_fk == User.id).filter(VizAlerts.operated_by_fk==current_user.id).group_by(func.to_char(VizAlerts.created_on, 'YYYYMM')).order_by(func.to_char(VizAlerts.created_on, 'YYYYMM'))
        
        data_result = [r._asdict() for r in alert_result]

        return Response(pd.io.json.dumps(data_result), mimetype='application/json')

    @expose('/alert/initCusts',methods=['GET'])
    @has_access
    def initCusts(self):

        custs_data = pd.read_csv(RULE_DEFAULT_FOLDER+'/initct.csv',encoding = 'unicode_escape')

        for index, row in custs_data.iterrows():
            customer = Customer(company_id=current_user.company_id,customer_id=row['CustomerID'], customer_name=row['CustomerName'], customer_type=row['CustomerType'], customer_risk_class=row['CustomerRiskClass'], customer_risk_level=row['CustomerRiskLevel']
                , is_charity_org=(0 if pd.isna(row['IsCharityOrg']) else 1),is_closed=(0 if pd.isna(row['IsClosed']) else 1), is_corr_bank=(0 if pd.isna(row['IsCorrBank']) else 1), is_FEP=(0 if pd.isna(row['IsFEP']) else 1)
                , is_MSB=(0 if pd.isna(row['IsMSB']) else 1), is_offshore_bank=(0 if pd.isna(row['IsOffshoreBank']) else 1), is_PEP=(0 if pd.isna(row['IsPEP']) else 1), is_PSP=(0 if pd.isna(row['IsPSP']) else 1)
                , is_CIB=(0 if pd.isna(row['IsCIB']) else 1), is_NBFI=(0 if pd.isna(row['IsNBFI']) else 1), is_FCB=(0 if pd.isna(row['IsFCB']) else 1))
            self.appbuilder.get_session.add(customer)
        self.appbuilder.get_session.commit()

        return  json.dumps({})

    @expose('/alerts/getCusPieData',methods=['GET'])
    @has_access
    def getCusPieData(self):

        total_result = db.session.query(func.count(Customer.id).label("total")).filter(Customer.company_id==current_user.company_id)
        total_result = [r._asdict() for r in total_result]
        cus_result = db.session.query(func.count(distinct(VizAlerts.account_key)).label("Alert Customer")).join(Customer, VizAlerts.account_key == Customer.customer_id).filter(Customer.company_id==current_user.company_id)
        cus_result = [r._asdict() for r in cus_result]

        total_result = total_result+cus_result
        others = total_result[0].get("total")-cus_result[0].get("Alert Customer")
        cus_result.append({'Others':others})

        return Response(pd.io.json.dumps(cus_result), mimetype='application/json')

class VizAlertsView(ModelView):

    datamodel = SQLAInterface(VizAlerts)
    list_title = "Alert Archive"
    base_permissions = ['can_list']

    search_columns = ['id', 'account_key', 'trigger_rule', 'rule_type', 'country_abbr', 'country_name','amount','cnt','rule_status','trans_month','created_on','finished_on']
    label_columns = {'alert_id': 'Item ID','trigger_rule':'Alert Rule','country_abbr': 'Opposite Country','amount': 'Trans Amount','cnt': 'Trans Cnt','rule_status': 'Status','trans_month': 'Month of Trans Date','created_on': 'Item Date','finished_on': 'Closed Date'}
    list_columns = ['alert_id', 'account_key', 'trigger_rule', 'rule_type', 'country_abbr', 'country_name','amount','cnt','rule_status','trans_month','created_on','finished_on']
    formatters_columns = {'country_abbr':lambda x: x if x else '-','country_name':lambda x: x if x else '-','amount':lambda x: '${:,.2f}'.format(x) if x else '$0','cnt':lambda x: x if x else 0,'created_on': lambda x: x.strftime("%Y-%m-%d %H:%M:%S"),'finished_on': lambda x: x.strftime("%Y-%m-%d %H:%M:%S") }
    base_filters = [['current_step',FilterEqual,None]]
    base_order = ('changed_on','desc')

class AMLProgView(ModelView):

    datamodel = SQLAInterface(AmlProgram)

    label_columns = {'days_between':'Days to Next Review', 'download': 'Download'}
    list_columns = ['file_name','title','last_update_date','next_review_date','days_between','status','created_by','download']
    show_columns = ['file_name','title','last_update_date','next_review_date','days_between','status','created_by','created_on','changed_by','changed_on','download']
    add_columns =  ['title','last_update_date','next_review_date','file']
    edit_columns = ['title','last_update_date','next_review_date','file']
    base_filters = [['company_id',FilterEqualFunction,getCompany]]
    list_title = 'Upload Your AML Program, Policy and Procedures Documents'
    #base_filters = [['created_by',FilterEqualFunction,getUser]]

    def pre_add(self, item):
        item.company_id = current_user.company_id


@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404

db.create_all()
appbuilder.add_separator("Security")
appbuilder.add_view(CompanyModelView, "Companys", icon="fa-folder-open-o",category='Security')
appbuilder.add_view(DataCenterView, "Bank File Upload", href='/datacenter/bankdata/tb/index',category='Data Center')
appbuilder.add_link("Rules Configuration", href='/datacenter/rules/index',category='Rules')
appbuilder.add_view(AMLProgView, "AML Program Management", category='AML Program')
appbuilder.add_view(TransView, "Transaction Monitoring", href='/trans/category',category='Quantitative Testing')
#appbuilder.add_view(RuleView, "High Risk Country Wire Activity", href='/rules/highRiskCountry/Wire',category='Quantitative')
#appbuilder.add_link("High Risk Country ACH Activity", href='/rules/highRiskCountry/ACH', category='Quantitative')
#appbuilder.add_link("Cash Activity Limit", href='/rules/highRiskVolume/Cash', category='Quantitative')
#appbuilder.add_link("Check Activity Limit", href='/rules/highRiskVolume/Check', category='Quantitative')
#appbuilder.add_link("Remote Deposit Activity Limit", href='/rules/highRiskVolume/Remote', category='Quantitative')
#appbuilder.add_link("Wire Transfer Activity Limit", href='/rules/highRiskVolume/Wire', category='Quantitative')
#appbuilder.add_link("ACH Transfer Activity Limit", href='/rules/highRiskVolume/ACH', category='Quantitative')
#appbuilder.add_link("Cash Activity Profiling", href='/rules/profiling/Cash', category='Quantitative')
#appbuilder.add_link("Check Activity Profiling", href='/rules/profiling/Check', category='Quantitative')
#appbuilder.add_link("Remote Deposit Activity Profiling", href='/rules/profiling/Remote', category='Quantitative')
#appbuilder.add_link("Wire Transfer Activity Profiling", href='/rules/profiling/Wire', category='Quantitative')
#appbuilder.add_link("ACH Transfer Activity Profiling", href='/rules/profiling/ACH', category='Quantitative')
#appbuilder.add_link("FLow Through Activity Pattern", href='/rules/flowthrough', category='Quantitative')
appbuilder.add_view(AlertView, "Transaction Monitoring Q/A Alerts", href='/alerts/management/index',category='Quanlitative Testing')
#appbuilder.add_link("Alert Archive", href='/alerts/archive',category='Quanlitative')
appbuilder.add_view_no_menu(HomeView())
appbuilder.add_view_no_menu(RuleView())

