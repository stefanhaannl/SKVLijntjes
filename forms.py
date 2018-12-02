from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Email, InputRequired


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')


class SignUpForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(3, 64), Email()])
    name = StringField("Name", validators=[DataRequired(), Length(3, 64)])
    password = PasswordField("Password", validators=[DataRequired(), Length(6, 64), EqualTo('password2', message="Password fields do not match.")])
    password2 = PasswordField("Repeat Password", validators=[DataRequired(), Length(6, 64)])


class AddLineForm(FlaskForm):
    user1 = SelectField("User 1", coerce=int, validators=[InputRequired()])
    user2 = SelectField("User 2", coerce=int, validators=[InputRequired()])
    description = TextAreaField("Description")

