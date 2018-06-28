from flask import render_template, request, Response
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import AppBuilder, BaseView, ModelView, expose, has_access
from werkzeug import secure_filename
from app import appbuilder, db
from app.fileUtils import *

import numpy as np
import pandas as pd
import json

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
class RuleView(BaseView):
    
    route_base = '/rules'
    default_view = 'highRiskCountry'
    s3 = boto3.resource('s3')
    bucket_name='vizrules'

    ALLOWED_RND_EXTENSIONS = set(['csv'])

    def allowed_file(self,filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.ALLOWED_RND_EXTENSIONS

    """
    Rule1: High Risk Countries
    """        

    @expose('/highRiskCountry')
    @has_access
    def highRiskCountry(self):

    	keyname = ''
    	if request.method == 'GET':
    		for bucket in self.s3.buckets.all():
    			for key in bucket.objects.all():
    				words = key.key.split('/')
    				if len(words)==2 and words[0]=='highRiskCountry' and words[1]!='':
    					keyname=words[1]
        	#self.s3.Object('vizrules', 'highRiskCountry/highRiskCountry.csv').put(Body=open('app/static/csv/rules/highRiskCountry.csv', 'rb'))
    		return self.render_template('rules/rule_high_risk_country.html',keyname=keyname)

    @expose('/highRiskCountry/heatmap',methods=['POST'])
    @has_access
    def getHighRiskCountryHeatMapData(self):

        def_data_county = 'app/static/csv/rules/highRiskCountry.csv'

        heat_map_data = pd.read_csv(def_data_county,usecols=['Month of Trans Date','OPP_CNTRY','Trans Amt'])
        #min_month = heat_map_data['Month of Trans Date'].min()
        #heat_map_result = heat_map_data.loc[heat_map_data['Month of Trans Date'] == min_month]
        heat_map_result = heat_map_data.groupby(['Month of Trans Date','OPP_CNTRY']).sum().reset_index()
        #print(heat_map_result.to_json(orient='records'))

        return Response(heat_map_result.to_json(orient='records'), mimetype='application/json')

    @expose('/highRiskCountry/scatterplot',methods=['POST'])
    @has_access
    def getHighRiskCountryScatterPlotData(self):

    	def_data_no_county = 'app/static/csv/rules/highRiskNoCountry.csv'

    	plot_data = pd.read_csv(def_data_no_county,usecols=['Trans Count','Trans Amt','ACCOUNT_KEY','Month of Trans Date'])
    	plot_data = plot_data[['Trans Count','Trans Amt','ACCOUNT_KEY','Month of Trans Date']]

    	return Response(plot_data.to_json(orient='split'), mimetype='application/json')

    @expose('/highRiskCountry/tabledata',methods=['POST'])
    @has_access
    def getHighRiskCountryTableData(self):

    	threshold = request.get_json()["threshNum"]

    	def_data_no_county = 'app/static/csv/rules/highRiskNoCountry.csv'

    	table_data = pd.read_csv(def_data_no_county,usecols=['ACCOUNT_KEY','Month of Trans Date','Trans Amt'])

    	table_data = table_data[table_data['Trans Amt']>=int(threshold)]

    	return Response(table_data.to_json(orient='records'), mimetype='application/json')

    @expose('/highRiskCountry/upload',methods=['POST','DELETE'])
    @has_access
    def getHighRiskCountryFileData(self):

        if request.method == 'POST':
            files = request.files['file']

            if files:
                filename = secure_filename(files.filename)

                mime_type = files.content_type

                if not self.allowed_file(files.filename):
                    result = uploadfile(name=filename, type=mime_type, size=0, not_allowed_msg="File type not allowed")

                else:
                    self.s3.Object('vizrules', 'highRiskCountry/'+filename).put(Body=files)

        if request.method == 'DELETE':
            keyname = request.get_json()["keyname"]
            bucket = self.s3.Bucket(self.bucket_name)
            for key in bucket.objects.all():
                 
                 words = key.key.split('/')
                 if len(words)==2 and words[0]=='highRiskCountry' and words[1]==keyname:
                     key.delete()
                

        return  json.dumps({})


    """
    Rule2: High Risk Volume
    """        

    @expose('/highRiskVolume')
    @has_access
    def highRiskVolume(self):

    	keyname = ''
    	if request.method == 'GET':
    		for bucket in self.s3.buckets.all():
    			for key in bucket.objects.all():
    				words = key.key.split('/')
    				if len(words)==2 and words[0]=='highRiskVolume' and words[1]!='':
    					keyname=words[1]
        	#self.s3.Object('vizrules', 'highRiskCountry/highRiskCountry.csv').put(Body=open('app/static/csv/rules/highRiskCountry.csv', 'rb'))
    		return self.render_template('rules/rule_high_risk_volume.html',keyname=keyname)

    @expose('/highRiskVolume/statisticsdata',methods=['POST'])
    @has_access
    def getHighRiskVolumeStatisticsData(self):

    	def_volume_data = 'app/static/csv/rules/highValueVolume.csv'

    	outlier = request.get_json()["outlier"]

    	table_data = pd.read_csv(def_volume_data)

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
                    self.s3.Object('vizrules', 'highRiskVolume/'+filename).put(Body=files)

        if request.method == 'DELETE':
            keyname = request.get_json()["keyname"]
            print(keyname)
            bucket = self.s3.Bucket(self.bucket_name)
            for key in bucket.objects.all():
                 print(key.key)
                 words = key.key.split('/')
                 if len(words)==2 and words[0]=='highRiskVolume' and words[1]==keyname:
                     key.delete()


        return  json.dumps({})



@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404

db.create_all()

appbuilder.add_view(RuleView, "High Risk Countries", category='Rules')
appbuilder.add_link("High Risk Volume", href='/rules/highRiskVolume', category='Rules')


