from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Email, InputRequired


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')


class AddUserForm(FlaskForm):
    club = SelectField("Vereniging", coerce=int, validators=[InputRequired()])
    name = StringField("Naam", validators=[DataRequired(), Length(3, 64)])
    email = StringField("Email")


class AddLineForm(FlaskForm):
    user1 = SelectField("Wie", coerce=int, validators=[InputRequired()])
    user2 = SelectField("Met wie", coerce=int, validators=[InputRequired()])
    description = TextAreaField("Omschrijving")

