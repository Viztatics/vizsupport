from flask import render_template, request, Response
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import AppBuilder, BaseView, ModelView, expose, has_access
from app import appbuilder, db

import numpy as np
import pandas as pd

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

    @expose('/highRiskCountry',methods=['POST','GET'])
    @has_access
    def highRiskCountry(self):

        if request.method == 'GET':
            return self.render_template('rules/rule_high_risk_country.html')

        if request.method == 'POST':

        	def_data_county = 'app/static/csv/rules/highRiskCountry.csv'

        	heat_map_data = pd.read_csv(def_data_county)

        	min_month = heat_map_data['Month of Trans Date'].min()

        	heat_map_result = heat_map_data.loc[heat_map_data['Month of Trans Date'] == min_month]

        	print(heat_map_result.to_json(orient='records'))

        	return Response(heat_map_result.to_json(orient='records'), mimetype='application/json')



@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404

db.create_all()

appbuilder.add_view(RuleView, "High Risk Countries", category='Rules')


