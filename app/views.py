from flask import render_template, request, Response
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import AppBuilder, BaseView, ModelView, expose, has_access
from flask_login import current_user
from werkzeug import secure_filename
from app import appbuilder, db
from config import *
from .fileUtils import *
from .models import Company

import numpy as np
import pandas as pd
import json
from pathlib import Path,PurePath
import shutil

#import boto3

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

def transDesc(transCode):

	return 'WIRE TRANSFER' if transCode=='Wire' else transCode.upper()

class CompanyModelView(ModelView):
    datamodel = SQLAInterface(Company)


class RuleView(BaseView):
    
    route_base = '/rules'
    HIGH_RISK_COUNTRY_FOLDER_PREFIX = 'highRiskCountry'
    HIGH_VALUE_VOLUMN_FOLDER_PREFIX = 'highValueVolume'
    ACTIVITY_PROFILING_FOLDER_PREFIX = 'activityProfiling'
    """
    s3 = boto3.resource(
        's3',
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY,
    )
    """
    #s3 = boto3.resource('s3')
    bucket_name='vizrules'

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
    		return self.render_template('rules/rule_high_risk_country.html',keyname=keyname,transCode=transCode)

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

    	return Response(table_data.to_json(orient='records'), mimetype='application/json')

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
    		return self.render_template('rules/rule_high_risk_volume.html',keyname=keyname,transCode=transCode)

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

    	return Response(table_data.to_json(orient='records'), mimetype='application/json')

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
    		return self.render_template('rules/rule_high_risk_profiling.html',keyname=keyname,transCode=transCode)

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

    	return Response(table_data.to_json(orient='records'), mimetype='application/json')

    @expose('/profiling/upload',methods=['POST','DELETE'])
    @has_access
    def getProfilingFileData(self):

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
appbuilder.add_link("Cash Activity profiling", href='/rules/profiling/Cash', category='Rules')
appbuilder.add_link("Check Activity profiling", href='/rules/profiling/Check', category='Rules')
appbuilder.add_link("Remote Deposit Activity profiling", href='/rules/profiling/Remote', category='Rules')
appbuilder.add_link("Wire Transfer Activity profiling", href='/rules/profiling/Wire', category='Rules')
appbuilder.add_link("ACH Transfer Activity profiling", href='/rules/profiling/ACH', category='Rules')


