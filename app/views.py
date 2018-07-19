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
class CompanyModelView(ModelView):
    datamodel = SQLAInterface(Company)


class RuleView(BaseView):
    
    route_base = '/rules'
    default_view = 'highRiskCountry'
    HIGH_RISK_COUNTRY_WIRE_FOLDER = 'highRiskCountryWire'
    CASH_ACTIVITY_LIMIT_FOLDER = 'cashActivityLimit'
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

    @expose('/highRiskCountry')
    @has_access
    def highRiskCountry(self):

    	keyname = ''
    	src_file = RULE_DEFAULT_FOLDER+self.HIGH_RISK_COUNTRY_WIRE_FOLDER+"/highRiskCountry.csv"
    	dst_path = RULE_UPLOAD_FOLDER+self.HIGH_RISK_COUNTRY_WIRE_FOLDER+"/"+str(current_user.id)
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
    		return self.render_template('rules/rule_high_risk_country.html',keyname=keyname)

    @expose('/highRiskCountry/statisticsdata',methods=['POST'])
    def getHighRiskCountryStatisticsData(self):

    	dst_path = RULE_UPLOAD_FOLDER+self.HIGH_RISK_COUNTRY_WIRE_FOLDER+"/"+str(current_user.id)

    	dst_file = request.get_json()["filename"]

    	#transCodeType = request.get_json()["transCodeType"]

    	#crDb = request.get_json()["crDb"]

    	outlier = request.get_json()["outlier"]

    	table_data = pd.read_csv(dst_path+"/"+dst_file,usecols=['ACCOUNT_KEY', 'Month of Trans Date','Trans_Amt','outlier'])

    	#table_data = table_data.groupby(['ACCOUNT_KEY', 'Month of Trans Date'],as_index=False).sum()

    	#table_data = table_data[(table_data['Trans Code Type']==transCodeType)&(table_data['Cr_Db']==crDb)]

    	if outlier!='1':
    		table_data = table_data[table_data['outlier'].isnull()]

    	min_data = table_data['Trans_Amt'].min()

    	max_data = table_data['Trans_Amt'].max()
    	
    	median_data = table_data['Trans_Amt'].median()

    	mean_data = table_data['Trans_Amt'].mean()

    	return Response(pd.io.json.dumps([{'min_data':min_data,'max_data':max_data,'median_data':median_data,'mean_data':mean_data}]), mimetype='application/json')
    
    @expose('/highRiskCountry/percentiledata',methods=['POST'])
    def getHighRiskCountryPercentileData(self):

    	dst_path = RULE_UPLOAD_FOLDER+self.HIGH_RISK_COUNTRY_WIRE_FOLDER+"/"+str(current_user.id)

    	dst_file = request.get_json()["filename"]

    	outlier = request.get_json()["outlier"]

    	table_data = pd.read_csv(dst_path+"/"+dst_file,usecols=['ACCOUNT_KEY', 'Month of Trans Date','Trans_Amt','outlier'])

    	#table_data = table_data.groupby(['ACCOUNT_KEY', 'Month of Trans Date'],as_index=False).sum()

    	#table_data = table_data[(table_data['Trans Code Type']==transCodeType)&(table_data['Cr_Db']==crDb)]

    	if outlier!='1':
    		table_data = table_data[table_data['outlier'].isnull()]    	

    	percentile_data = table_data['Trans_Amt'].quantile([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1])

    	return Response(percentile_data.to_json(orient='records'), mimetype='application/json')

    @expose('/highRiskCountry/paretodata',methods=['POST'])
    def getHighRiskCountryParetoData(self):

    	dst_path = RULE_UPLOAD_FOLDER+self.HIGH_RISK_COUNTRY_WIRE_FOLDER+"/"+str(current_user.id)

    	dst_file = request.get_json()["filename"]

    	outlier = request.get_json()["outlier"]

    	table_data = pd.read_csv(dst_path+"/"+dst_file,usecols=['ACCOUNT_KEY', 'Trans_Amt','outlier'])

    	table_data = table_data.groupby(['ACCOUNT_KEY'],as_index=False).sum()

    	#table_data = table_data[(table_data['Trans Code Type']==transCodeType)&(table_data['Cr_Db']==crDb)]

    	if outlier!='1':
    		table_data = table_data[table_data['outlier']==0]   

    	bar_data = table_data.sort_values(by='Trans_Amt', ascending=False)

    	line_data = bar_data['Trans_Amt'].cumsum()/bar_data['Trans_Amt'].sum()*100.00

    	line_data = pd.Series(line_data, name='percentage')

    	pareto_data = pd.concat([bar_data, line_data], axis=1, sort=False)

    	return Response(pareto_data.to_json(orient='records'), mimetype='application/json')

    @expose('/highRiskCountry/heatmap',methods=['POST'])
    @has_access
    def getHighRiskCountryHeatMapData(self):

        dst_path = RULE_UPLOAD_FOLDER+self.HIGH_RISK_COUNTRY_WIRE_FOLDER+"/"+str(current_user.id)

        dst_file = request.get_json()["filename"]

        threshold = request.get_json()["threshNum"]

        def_data_county = dst_path+"/"+dst_file

        heat_map_data = pd.read_csv(def_data_county,usecols=['Month of Trans Date','OPP_CNTRY','Trans_Amt'])
        #min_month = heat_map_data['Month of Trans Date'].min()
        #heat_map_result = heat_map_data.loc[heat_map_data['Month of Trans Date'] == min_month]
        heat_map_result = heat_map_data.groupby(['Month of Trans Date','OPP_CNTRY']).sum().reset_index()
        #print(heat_map_result.to_json(orient='records'))
        heat_map_result = heat_map_result[heat_map_result['Trans_Amt']>=int(threshold)]

        return Response(heat_map_result.to_json(orient='records'), mimetype='application/json')

    @expose('/highRiskCountry/scatterplot',methods=['POST'])
    @has_access
    def getHighRiskCountryScatterPlotData(self):

    	dst_path = RULE_UPLOAD_FOLDER+self.HIGH_RISK_COUNTRY_WIRE_FOLDER+"/"+str(current_user.id)

    	dst_file = request.get_json()["filename"]

    	def_data_no_county = dst_path+"/"+dst_file

    	plot_data = pd.read_csv(def_data_no_county,usecols=['Trans_Count','Trans_Amt','ACCOUNT_KEY','Month of Trans Date','outlier'])
    	#plot_data = plot_data.groupby(['ACCOUNT_KEY','Month of Trans Date'],as_index=False).sum()
    	plot_data = plot_data[['Trans_Count','Trans_Amt','ACCOUNT_KEY','Month of Trans Date','outlier']]

    	return Response(plot_data.to_json(orient='split'), mimetype='application/json')

    @expose('/highRiskCountry/tabledata',methods=['POST'])
    @has_access
    def getHighRiskCountryTableData(self):

    	dst_path = RULE_UPLOAD_FOLDER+self.HIGH_RISK_COUNTRY_WIRE_FOLDER+"/"+str(current_user.id)

    	dst_file = request.get_json()["filename"]

    	threshold = request.get_json()["threshNum"]

    	def_data_no_county = dst_path+"/"+dst_file

    	table_data = pd.read_csv(def_data_no_county,usecols=['ACCOUNT_KEY','Month of Trans Date','OPP_CNTRY','Country Name','Trans_Amt'])

    	#table_data = table_data.groupby(['ACCOUNT_KEY', 'Month of Trans Date'],as_index=False).sum()

    	table_data = table_data[table_data['Trans_Amt']>=int(threshold)]

    	return Response(table_data.to_json(orient='records'), mimetype='application/json')

    @expose('/highRiskCountry/upload',methods=['POST','DELETE'])
    @has_access
    def getHighRiskCountryFileData(self):

        dst_path = RULE_UPLOAD_FOLDER+self.HIGH_RISK_COUNTRY_WIRE_FOLDER+"/"+str(current_user.id)

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

    @expose('/highRiskVolume')
    @has_access
    def highRiskVolume(self):

    	keyname = ''
    	if request.method == 'GET':
    		"""
    		for bucket in self.s3.buckets.all():
    			for key in bucket.objects.all():
    				words = key.key.split('/')
    				if len(words)==2 and words[0]=='highRiskVolume' and words[1]!='':
    					keyname=words[1]
    		"""
    		if not os.path.exists(RULE_UPLOAD_FOLDER+self.CASH_ACTIVITY_LIMIT_FOLDER):
    			os.makedirs(RULE_UPLOAD_FOLDER+self.CASH_ACTIVITY_LIMIT_FOLDER)
    		p = Path(RULE_UPLOAD_FOLDER+self.CASH_ACTIVITY_LIMIT_FOLDER)
    		for child in p.iterdir():
    				keyname = PurePath(child).name
        	#self.s3.Object('vizrules', 'highRiskCountry/highRiskCountry.csv').put(Body=open('app/static/csv/rules/highRiskCountry.csv', 'rb'))
    		return self.render_template('rules/rule_high_risk_volume.html',keyname=keyname)

    @expose('/highRiskVolume/statisticsdata',methods=['POST'])
    @has_access
    def getHighRiskVolumeStatisticsData(self):

    	def_volume_data = 'app/static/csv/rules/highValueVolume.csv'

    	transCodeType = request.get_json()["transCodeType"]

    	crDb = request.get_json()["crDb"]

    	outlier = request.get_json()["outlier"]

    	table_data = pd.read_csv(def_volume_data)

    	table_data = table_data[(table_data['Trans Code Type']==transCodeType)&(table_data['Cr_Db']==crDb)]

    	if outlier!='1':
    		table_data = table_data[table_data['outlier']!=1]

    	min_data = table_data['TRANS_AMT'].min()

    	max_data = table_data['TRANS_AMT'].max()
    	
    	median_data = table_data['TRANS_AMT'].median()

    	mean_data = table_data['TRANS_AMT'].mean()

    	return Response(pd.io.json.dumps([{'min_data':min_data,'max_data':max_data,'median_data':median_data,'mean_data':mean_data}]), mimetype='application/json')

    @expose('/highRiskVolume/scatterplot',methods=['POST'])
    @has_access
    def getHighRiskVolumeScatterPlotData(self):

    	transCodeType = request.get_json()["transCodeType"]

    	crDb = request.get_json()["crDb"]

    	def_volume_data = 'app/static/csv/rules/highValueVolume.csv'

    	plot_data = pd.read_csv(def_volume_data)

    	plot_data = plot_data[(plot_data['Trans Code Type']==transCodeType)&(plot_data['Cr_Db']==crDb)]
    	plot_data = plot_data[['TRANS_CNT','TRANS_AMT','ACCOUNT_KEY','Month of Trans Date','outlier']]

    	return Response(plot_data.to_json(orient='split'), mimetype='application/json')

    @expose('/highRiskVolume/tabledata',methods=['POST'])
    @has_access
    def getHighRiskVolumeTableData(self):

    	transCodeType = request.get_json()["transCodeType"]

    	crDb = request.get_json()["crDb"]

    	amtThreshold = request.get_json()["amtThreshNum"]

    	cntThreshold = request.get_json()["cntThreshNum"]

    	def_volume_data = 'app/static/csv/rules/highValueVolume.csv'

    	table_data = pd.read_csv(def_volume_data)

    	table_data = table_data[(table_data['TRANS_AMT']>=int(amtThreshold))&(table_data['TRANS_CNT']>=int(cntThreshold))&(table_data['Trans Code Type']==transCodeType)&(table_data['Cr_Db']==crDb)]

    	table_data = table_data[['ACCOUNT_KEY','Month of Trans Date','TRANS_AMT','TRANS_CNT']]
    	

    	return Response(table_data.to_json(orient='records'), mimetype='application/json')

    @expose('/highRiskVolume/upload',methods=['POST','DELETE'])
    @has_access
    def getHighRiskVolumeFileData(self):

        if request.method == 'POST':            

            files = request.files['file']

            if files:
                filename = secure_filename(files.filename)

                mime_type = files.content_type

                if not self.allowed_file(files.filename):
                    result = uploadfile(name=filename, type=mime_type, size=0, not_allowed_msg="File type not allowed")
                else:
                    if not os.path.exists(RULE_UPLOAD_FOLDER+self.CASH_ACTIVITY_LIMIT_FOLDER):
                        os.makedirs(RULE_UPLOAD_FOLDER+self.CASH_ACTIVITY_LIMIT_FOLDER)
                    files.save(os.path.join((RULE_UPLOAD_FOLDER+self.CASH_ACTIVITY_LIMIT_FOLDER), filename))
                    """
                    self.s3.Object('vizrules', 'highRiskVolume/'+filename).put(Body=files)
                    """

        if request.method == 'DELETE':
            keyname = request.get_json()["keyname"]
            os.remove(RULE_UPLOAD_FOLDER+self.CASH_ACTIVITY_LIMIT_FOLDER+"/"+keyname)
            """
            bucket = self.s3.Bucket(self.bucket_name)
            for key in bucket.objects.all():
                 print(key.key)
                 words = key.key.split('/')
                 if len(words)==2 and words[0]=='highRiskVolume' and words[1]==keyname:
                     key.delete()
            """


        return  json.dumps({})



@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404

db.create_all()
appbuilder.add_separator("Security")
appbuilder.add_view(CompanyModelView, "Companys", icon="fa-folder-open-o",category='Security')
appbuilder.add_view(RuleView, "High Risk Country Wire Activity", category='Rules')
appbuilder.add_link("High Risk Volume", href='/rules/highRiskVolume', category='Rules')


