from flask.ext.wtf import Form
from wtforms import BooleanField
from wtforms.validators import Required

class LoginForm(Form):
	remember_me = BooleanField('remember_me', default = False)
