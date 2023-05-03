# where we define the forms for the application
# Using Flask WTF to handle forms
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class LeaderBoardForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    # add a submit button to our leaderboardform
    submit = SubmitField('Submit')



