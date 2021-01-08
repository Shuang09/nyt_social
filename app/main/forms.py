#coding=gbk
from flask_wtf import Form
from wtforms import StringField,SubmitField,BooleanField,DateField,IntegerField
from wtforms.validators import Required

class NoteForm(Form):
    s_travelnote_title=StringField()
    s_scenery=StringField()
    s_travelnote_content=StringField()
    s_traveler=StringField()
    dt_record=DateField()
