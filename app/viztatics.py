from flask_appbuilder.security.sqla.manager import SecurityManager
from .models import VizUser
from .security_views import VizUserDBModelView
from flask_appbuilder.security.views import UserInfoEditView
from flask_appbuilder import IndexView

class VizSecurityManager(SecurityManager):
    user_model = VizUser
    userdbmodelview = VizUserDBModelView

class VizIndexView(IndexView):
	index_template = 'index.html'