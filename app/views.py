from flask import render_template, request, Response
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import AppBuilder, BaseView, ModelView, expose, has_access
from werkzeug import secure_filename
from app import appbuilder, db
from app.fileUtils import *

import numpy as np
import pandas as pd
import json

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

    ALLOWED_RND_EXTENSIONS = set(['csv'])

    def allowed_file(self,filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.ALLOWED_RND_EXTENSIONS

    @expose('/highRiskCountry')
    @has_access
    def highRiskCountry(self):

        if request.method == 'GET':
            return self.render_template('rules/rule_high_risk_country.html')

    @expose('/highRiskCountry/heatmap',methods=['POST'])
    @has_access
    def getHeatMapData(self):

        def_data_county = 'app/static/csv/rules/highRiskCountry.csv'

        heat_map_data = pd.read_csv(def_data_county,usecols=['Month of Trans Date','OPP_CNTRY','Trans Amt'])
        #min_month = heat_map_data['Month of Trans Date'].min()
        #heat_map_result = heat_map_data.loc[heat_map_data['Month of Trans Date'] == min_month]
        heat_map_result = heat_map_data.groupby(['Month of Trans Date','OPP_CNTRY']).sum().reset_index()
        #print(heat_map_result.to_json(orient='records'))

        return Response(heat_map_result.to_json(orient='records'), mimetype='application/json')

    @expose('/highRiskCountry/scatterplot',methods=['POST'])
    @has_access
    def getScatterPlotData(self):

    	def_data_no_county = 'app/static/csv/rules/highRiskNoCountry.csv'

    	plot_data = pd.read_csv(def_data_no_county,usecols=['Trans Count','Trans Amt'])

    	return Response(plot_data.to_json(orient='split'), mimetype='application/json')

    @expose('/highRiskCountry/alerttable',methods=['POST'])
    @has_access
    def getAlertTableData(self):

    	threshold = request.get_json()["threshNum"]

    	def_data_no_county = 'app/static/csv/rules/highRiskNoCountry.csv'

    	table_data = pd.read_csv(def_data_no_county,usecols=['ACCOUNT_KEY','Month of Trans Date','Trans Amt'])

    	table_data = table_data[table_data['Trans Amt']>int(threshold)]

    	return Response(table_data.to_json(orient='records'), mimetype='application/json')

    @expose('/highRiskCountry/upload',methods=['POST','DELETE'])
    @has_access
    def getAlertTableData(self):

    	if request.method == 'POST':
            files = request.files['file']

            if files:
                filename = secure_filename(files.filename)

                mime_type = files.content_type

                if not self.allowed_file(files.filename):
                    result = uploadfile(name=filename, type=mime_type, size=0, not_allowed_msg="File type not allowed")
                

    	return  json.dumps({})



@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404

db.create_all()

appbuilder.add_view(RuleView, "High Risk Countries", category='Rules')


