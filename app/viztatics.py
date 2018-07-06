from flask_appbuilder.security.sqla.manager import SecurityManager
from .models import VizUser
from .security_views import VizUserDBModelView
from flask_appbuilder.security.views import UserInfoEditView

class VizSecurityManager(SecurityManager):
    user_model = VizUser
    userdbmodelview = VizUserDBModelView