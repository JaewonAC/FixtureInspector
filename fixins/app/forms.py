from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField

class ShootForm(FlaskForm):
  lot_number = StringField('Lot Number')
  usb_drive = SelectField("Choose USB", choices=[])
  shoot = SubmitField('Shoot')
  