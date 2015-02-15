from flask.ext.wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

class Address(Form):
    addressa = StringField('addressa', validators=[DataRequired()])
    addressb = StringField('addressb', validators=[DataRequired()])