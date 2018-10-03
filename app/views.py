from flask import render_template, request, Response, jsonify, make_response
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.models.sqla.filters import FilterEqual
from flask_appbuilder.security.sqla.models import User
from flask_appbuilder import AppBuilder, BaseView, ModelView, expose, has_access
from flask_login import current_user
from sqlalchemy import func,inspect,text
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

def isManager():

    is_analysis_manager = False
    for role in current_user.roles:
        if role.name=='AnalysisManager':
            is_analysis_manager = True
    return is_analysis_manager

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

    @expose('/highRiskCountry/<transCode>')
    @has_access
    def highRiskCountry(self,transCode):

    	keyname = ''
    	highRiskCountryFolder = self.HIGH_RISK_COUNTRY_FOLDER_PREFIX+transCode
    	src_file = RULE_DEFAULT_FOLDER+highRiskCountryFolder+"/highRiskCountry.csv"
    	dst_path = RULE_UPLOAD_FOLDER+highRiskCountryFolder+"/"+str(current_user.id)
    	if request.method == 'GET':
    		"""
    		for bucket in self.s3.buckets.all():
    			for key in bucket.objects.all():
    				words = key.key.split('/')
    				if len(words)==2 and words[0]=='highRiskCountry' and words[1]!='':
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
    		return self.render_template('rules/rule_high_risk_country.html',keyname=keyname,transCode=transTitle(transCode))

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

    @expose('/highRiskCountry/tabledata/<transCode>',methods=['POST'])
    @has_access
    def getHighRiskCountryTableData(self,transCode):

        highRiskCountryFolder = self.HIGH_RISK_COUNTRY_FOLDER_PREFIX+transCode

        dst_path = RULE_UPLOAD_FOLDER+highRiskCountryFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

        threshold = request.get_json()["threshNum"]

        def_data_no_county = dst_path+"/"+dst_file

        table_data = pd.read_csv(def_data_no_county,usecols=['ACCOUNT_KEY','Month of Trans Date','OPP_CNTRY','Country Name','Trans_Amt','Trans_Code_Type'])

        #table_data = table_data.groupby(['ACCOUNT_KEY', 'Month of Trans Date'],as_index=False).sum()

        table_data = table_data[(table_data['Trans_Amt']>=int(threshold))&(table_data['Trans_Code_Type']==transDesc(transCode))&(table_data['OPP_CNTRY'].notnull())&((table_data['OPP_CNTRY'])!='US')]

        db_result = db.session.query(func.count(VizAlerts.account_key).label('count'),VizAlerts.account_key).join(User, VizAlerts.created_by_fk == User.id).group_by(VizAlerts.account_key).filter(VizUser.company_id==current_user.company_id)

        db_frame = pd.DataFrame(db_result.all(),columns=[column['name'] for column in db_result.column_descriptions])

        db_frame = db_frame.rename(str.upper, axis='columns')

        table_data = pd.merge(table_data,db_frame,how='left',on='ACCOUNT_KEY')

        table_data['ID'] = table_data.index

        return Response(table_data.to_json(orient='records'), mimetype='application/json')

    @expose('/highRiskCountry/alertdata/<transCode>',methods=['POST'])
    @has_access
    def createHighRiskCountryAlertData(self,transCode):

        items = request.get_json()["items"]

        if transCode == 'Wire' :
            rule_name = RuleEnum.High_Risk_Country_Wire_Activity
        else:
            rule_name = RuleEnum.High_Risk_Country_ACH_Activity

        for item in items:

            alertdata = VizAlerts(account_key=item['ACCOUNT_KEY'], trans_month=item['Month of Trans Date'], country_abbr=item['OPP_CNTRY'], country_name = item['Country Name'], amount=item['Trans_Amt'],rule_type=TypeEnum.High_Risk_Country,rule_status=StatusEnum.Open,trigger_rule=rule_name,current_step=ProcessEnum.Manager_Assign,operated_by_fk=current_user.id)
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

    @expose('/highRiskVolume/<transCode>')
    @has_access
    def highRiskVolume(self,transCode):

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
    		return self.render_template('rules/rule_high_risk_volume.html',keyname=keyname,transCode=transTitle(transCode))

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

    @expose('/highRiskVolume/tabledata/<transCode>',methods=['POST'])
    @has_access
    def getHighRiskVolumeTableData(self,transCode):

        highRiskVolumnFolder = self.HIGH_VALUE_VOLUMN_FOLDER_PREFIX+transCode

        dst_path = RULE_UPLOAD_FOLDER+highRiskVolumnFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

        crDb = request.get_json()["crDb"]

        amtThreshold = request.get_json()["amtThreshNum"]

        cntThreshold = request.get_json()["cntThreshNum"]

        def_volume_data = dst_path+"/"+dst_file

        table_data = pd.read_csv(def_volume_data)

        table_data = table_data[(table_data['TRANS_AMT']>=int(amtThreshold))&(table_data['TRANS_CNT']>=int(cntThreshold))&(table_data['Trans Code Type']==transDesc(transCode))&(table_data['Cr_Db']==crDb)]

        table_data = table_data[['ACCOUNT_KEY','Month of Trans Date','TRANS_AMT','TRANS_CNT']]

        db_result = db.session.query(func.count(VizAlerts.account_key).label('count'),VizAlerts.account_key).join(User, VizAlerts.created_by_fk == User.id).group_by(VizAlerts.account_key).filter(VizUser.company_id==current_user.company_id)

        db_frame = pd.DataFrame(db_result.all(),columns=[column['name'] for column in db_result.column_descriptions])

        db_frame = db_frame.rename(str.upper, axis='columns')

        table_data = pd.merge(table_data,db_frame,how='left',on='ACCOUNT_KEY')    

        table_data['ID'] = table_data.index	

        return Response(table_data.to_json(orient='records'), mimetype='application/json')

    @expose('/highRiskVolume/alertdata/<transCode>',methods=['POST'])
    @has_access
    def createHighRiskVolumeAlertData(self,transCode):

        items = request.get_json()["items"]

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

        for item in items:

            alertdata = VizAlerts(account_key=item['ACCOUNT_KEY'], trans_month=item['Month of Trans Date'], amount=item['TRANS_AMT'],cnt=item['TRANS_CNT'], rule_type=TypeEnum.High_Volume_Value,rule_status=StatusEnum.Open,trigger_rule=rule_name,current_step=ProcessEnum.Manager_Assign,operated_by_fk=current_user.id)
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

    @expose('/profiling/tabledata/<transCode>',methods=['POST'])
    @has_access
    def getProfilingTableData(self,transCode):

        profilingFolder = self.ACTIVITY_PROFILING_FOLDER_PREFIX+transCode

        dst_path = RULE_UPLOAD_FOLDER+profilingFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

    	#crDb = request.get_json()["crDb"]

        amtThreshold = request.get_json()["amtThreshNum"]

        cntThreshold = request.get_json()["cntThreshNum"]

        def_volume_data = dst_path+"/"+dst_file

        table_data = pd.read_csv(def_volume_data,usecols=['ACCOUNT_KEY','YearMonth','Credit+TRANS_CNT','Debit+TRANS_CNT','TRANS_AMT','outlier'])

        table_data['TRANS_CNT'] = table_data['Credit+TRANS_CNT'] + table_data['Debit+TRANS_CNT']

        table_data = table_data[(table_data['TRANS_AMT']>=int(amtThreshold))&(table_data['TRANS_CNT']>=int(cntThreshold))] 

        db_result = db.session.query(func.count(VizAlerts.account_key).label('count'),VizAlerts.account_key).join(User, VizAlerts.created_by_fk == User.id).group_by(VizAlerts.account_key).filter(VizUser.company_id==current_user.company_id)

        db_frame = pd.DataFrame(db_result.all(),columns=[column['name'] for column in db_result.column_descriptions])

        db_frame = db_frame.rename(str.upper, axis='columns')

        table_data = pd.merge(table_data,db_frame,how='left',on='ACCOUNT_KEY')

        table_data['ID'] = table_data.index	

        return Response(table_data.to_json(orient='records'), mimetype='application/json')

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

        for item in items:

            alertdata = VizAlerts(account_key=item['ACCOUNT_KEY'], trans_month=item['YearMonth'], amount=item['TRANS_AMT'],cnt=item['TRANS_CNT'],rule_type=TypeEnum.Profiling,rule_status=StatusEnum.Open,trigger_rule=rule_name,current_step=ProcessEnum.Manager_Assign,operated_by_fk=current_user.id)
            self.appbuilder.get_session.add(alertdata)
            self.appbuilder.get_session.flush()
            alertproc = AlertProcess(alert_id=alertdata.id,process_type=ProcessEnum.Alert_Created,assigned_to_fk=current_user.id,syslog=Alert_Created.format(current_user.username,datetime.now(),rule_name.name,TypeEnum.High_Risk_Country.name,StatusEnum.Open.name))
            self.appbuilder.get_session.add(alertproc)

        self.appbuilder.get_session.commit()
        return  json.dumps({})

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

    @expose('/flowthrough')
    @has_access
    def activityflowthrough(self):

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
    		return self.render_template('rules/rule_high_risk_flowthrough.html',keyname=keyname)

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

    @expose('/flowthrough/tabledata',methods=['POST'])
    @has_access
    def getFlowthroughTableData(self):

        flowthroughFolder = self.ACTIVITY_FLOW_THROUGH_FOLDER_PREFIX+'Flow'

        dst_path = RULE_UPLOAD_FOLDER+flowthroughFolder+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

    	#crDb = request.get_json()["crDb"]

        amtThreshold = request.get_json()["amtThreshNum"]

        lowerRatio = request.get_json()["lowerRatio"]

        upperRatio = request.get_json()["upperRatio"]

        def_volume_data = dst_path+"/"+dst_file

        table_data = pd.read_csv(def_volume_data,usecols=['ACCOUNT_KEY','YearMonth','Credit+TRANS_AMT','Debit+TRANS_AMT','TRANS_AMT','outlier'])

        table_data = table_data[(table_data['TRANS_AMT']>=int(amtThreshold))&((table_data['Credit+TRANS_AMT']/table_data['Debit+TRANS_AMT']*100.00)>=int(lowerRatio))&((table_data['Credit+TRANS_AMT']/table_data['Debit+TRANS_AMT']*100.00)<=int(upperRatio))] 	

        db_result = db.session.query(func.count(VizAlerts.account_key).label('count'),VizAlerts.account_key).join(User, VizAlerts.created_by_fk == User.id).group_by(VizAlerts.account_key).filter(VizUser.company_id==current_user.company_id)

        db_frame = pd.DataFrame(db_result.all(),columns=[column['name'] for column in db_result.column_descriptions])

        db_frame = db_frame.rename(str.upper, axis='columns')

        table_data = pd.merge(table_data,db_frame,how='left',on='ACCOUNT_KEY')

        table_data['ID'] = table_data.index	

        return Response(table_data.to_json(orient='records'), mimetype='application/json')

    @expose('/flowthrough/alertdata',methods=['POST'])
    @has_access
    def createFlowThroughAlertData(self):

        rule_name = RuleEnum.FLow_Through_Activity_Pattern

        items = request.get_json()["items"]

        for item in items:

            alertdata = VizAlerts(account_key=item['ACCOUNT_KEY'], trans_month=item['YearMonth'], amount=item['TRANS_AMT'],rule_type=TypeEnum.Flow_Through,rule_status=StatusEnum.Open,trigger_rule=rule_name,current_step=ProcessEnum.Manager_Assign,operated_by_fk=current_user.id)
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
    @expose('/management/barchart',methods=['POST'])
    @has_access
    def getBarChartData(self):

    	type_result = db.session.query(func.count(VizAlerts.rule_status).label('count'),User.username,VizAlerts.rule_status.name).outerjoin(User, VizAlerts.operated_by_fk == User.id).group_by(User.id,User.username,VizAlerts.rule_status).filter(VizUser.company_id==current_user.company_id).order_by(User.id)
    	type_result = [r for r in type_result]
    	return Response(pd.io.json.dumps(type_result), mimetype='application/json')

    @expose('/management/gettabledata/<start>/<end>/<atype>/<customer>',methods=['GET'])
    @has_access
    def getAlertTableData(self,start,end,atype,customer):

        data_result = []
        iStart = int(start)
        iEnd = int(end)

        is_analysis_manager = isManager()

        if is_analysis_manager is True:
            alert_result = db.session.query(VizAlerts.id,VizAlerts.rule_type.name,VizAlerts.account_key,VizAlerts.trans_month,VizAlerts.country_abbr,VizAlerts.country_name,VizAlerts.amount,VizAlerts.cnt,VizAlerts.rule_status.name,User.id.label('uid'),User.username,VizAlerts.trigger_rule.name,func.to_char(VizAlerts.created_on, 'YYYY-MM-DD HH24:MI:SS').label("created_on"),func.to_char(VizAlerts.finished_on, 'YYYY-MM-DD HH24:MI:SS').label("finished_on"),VizAlerts.current_step.name).join(User, VizAlerts.operated_by_fk == User.id).filter(VizUser.company_id==current_user.company_id,VizAlerts.rule_status==StatusEnum.Open.name).order_by(VizAlerts.operated_on.desc())
        else:            
            alert_result = db.session.query(VizAlerts.id,VizAlerts.rule_type.name,VizAlerts.account_key,VizAlerts.trans_month,VizAlerts.country_abbr,VizAlerts.country_name,VizAlerts.amount,VizAlerts.cnt,VizAlerts.rule_status.name,User.id.label('uid'),User.username,VizAlerts.trigger_rule.name,func.to_char(VizAlerts.created_on, 'YYYY-MM-DD HH24:MI:SS').label("created_on"),func.to_char(VizAlerts.finished_on, 'YYYY-MM-DD HH24:MI:SS').label("finished_on"),VizAlerts.current_step.name).join(User, VizAlerts.operated_by_fk == User.id).filter(VizAlerts.operated_by_fk==current_user.id,VizAlerts.rule_status==StatusEnum.Open.name).order_by(VizAlerts.operated_on.desc())

        if iStart>=0 and iEnd!=0 : 
            alert_result = alert_result.filter(func.date_part('day',func.current_date()-VizAlerts.created_on)>=iStart,func.date_part('day',func.current_date()-VizAlerts.created_on)<=iEnd,VizAlerts.rule_type==atype)
        if atype!='0':
            alert_result = alert_result.filter(VizAlerts.rule_type==atype)
        if customer!='0':
            alert_result = alert_result.filter(VizAlerts.account_key==customer)

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
            bucket = self.s3.Bucket(S3_BUCKET)
            bucket.copy({'Bucket': S3_BUCKET, 'Key': 'alerts/'+str(alert_id)+"/"+attachment}, full_attached_path)
            bucket.delete_objects(Delete={'Objects': [{'Key': 'alerts/'+str(alert_id)+"/"+attachment}]})
            self.s3.Object(S3_BUCKET,full_attached_path).Acl().put(ACL='public-read')
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
                    bucket = self.s3.Bucket(S3_BUCKET)
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
                self.s3.Object(S3_BUCKET, 'alerts/'+aid+"/"+filename).put(Body=files)


        if request.method == 'DELETE':
            keyname = request.get_json()["keyname"]
            if cid=='0':
                bucket = self.s3.Bucket(S3_BUCKET)
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

    @expose('/bankdata/tb/index')
    @has_access
    def bankdatatd(self):

        return self.render_template('datacenter/bankdataTB.html')

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
            alert_result = db.session.query(func.to_char(VizAlerts.created_on, 'YYYYMM').label('month'),VizAlerts.rule_status,func.count(VizAlerts.id).label("count")).join(User, VizAlerts.operated_by_fk == User.id).filter(VizUser.company_id==current_user.company_id).group_by(func.to_char(VizAlerts.created_on, 'YYYYMM'),VizAlerts.rule_status)
        else:
            alert_result = db.session.query(func.to_char(VizAlerts.created_on, 'YYYYMM').label('month'),VizAlerts.rule_status,func.count(VizAlerts.id).label("count")).join(User, VizAlerts.operated_by_fk == User.id).filter(VizAlerts.operated_by_fk==current_user.id).group_by(func.to_char(VizAlerts.created_on, 'YYYYMM'),VizAlerts.rule_status)
        
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


@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404

db.create_all()
appbuilder.add_separator("Security")
appbuilder.add_view(CompanyModelView, "Companys", icon="fa-folder-open-o",category='Security')
appbuilder.add_view(RuleView, "High Risk Country Wire Activity", href='/rules/highRiskCountry/Wire',category='Rules')
appbuilder.add_link("High Risk Country ACH Activity", href='/rules/highRiskCountry/ACH', category='Rules')
appbuilder.add_link("Cash Activity Limit", href='/rules/highRiskVolume/Cash', category='Rules')
appbuilder.add_link("Check Activity Limit", href='/rules/highRiskVolume/Check', category='Rules')
appbuilder.add_link("Remote Deposit Activity Limit", href='/rules/highRiskVolume/Remote', category='Rules')
appbuilder.add_link("Wire Transfer Activity Limit", href='/rules/highRiskVolume/Wire', category='Rules')
appbuilder.add_link("ACH Transfer Activity Limit", href='/rules/highRiskVolume/ACH', category='Rules')
appbuilder.add_link("Cash Activity Profiling", href='/rules/profiling/Cash', category='Rules')
appbuilder.add_link("Check Activity Profiling", href='/rules/profiling/Check', category='Rules')
appbuilder.add_link("Remote Deposit Activity Profiling", href='/rules/profiling/Remote', category='Rules')
appbuilder.add_link("Wire Transfer Activity Profiling", href='/rules/profiling/Wire', category='Rules')
appbuilder.add_link("ACH Transfer Activity Profiling", href='/rules/profiling/ACH', category='Rules')
appbuilder.add_link("FLow Through Activity Pattern", href='/rules/flowthrough', category='Rules')
appbuilder.add_view(AlertView, "Alert Management", href='/alerts/management/index',category='Alerts')
appbuilder.add_link("Alert Archive", href='/alerts/archive',category='Alerts')
appbuilder.add_view(DataCenterView, "Bank File Upload", href='/datacenter/bankdata/tb/index',category='Data Center')
appbuilder.add_link("Rules Configuration", href='/datacenter/rules/index',category='Data Center')
appbuilder.add_view_no_menu(HomeView())

