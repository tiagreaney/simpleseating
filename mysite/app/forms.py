from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, DateTimeField, IntegerField, TextAreaField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User, CompanySeats
from flask_login import current_user

class RegisterCompanyForm(FlaskForm):
    company_username = StringField('Company Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    company_name = StringField('Company Name', validators=[DataRequired()])
    department = StringField('Department', validators=[DataRequired()])
    password = PasswordField('Create a Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register my company')

    def validate_company_username(self, company_username):
        user = User.query.filter_by(company_username=company_username.data).first()
        if user is not None:
            raise ValidationError('Please use a different company username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class RegisterEmployeeForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    company_username = StringField('Company Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    department = StringField('Department', validators=[DataRequired()])
    password = PasswordField('Create a Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register as employee')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')


class AddCompanySeatForm(FlaskForm):
    seat_id_name = StringField('Seat ID/Name', validators=[DataRequired()])
    seat_description = StringField('Seat Description')
    submit = SubmitField('Add Seat')

class DeleteCompanySeatForm(FlaskForm):
    company_seat_id = QuerySelectField('Seat ID/Name:', query_factory=lambda: getCompanySeats())
    submit = SubmitField('Delete Seat')

class AddSeatBookingForm(FlaskForm):
    company_seat_id = QuerySelectField('Seat ID/Name:', query_factory=lambda: getCompanySeats())
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    start_time = DateTimeField('Start Time', format="%H:%M", validators=[DataRequired()])
    end_time = DateTimeField('End Time', format="%H:%M", validators=[DataRequired()])
    submit = SubmitField('Add Seat Booking')

def getCompanySeats():
    company_seats = CompanySeats.query.filter(CompanySeats.comp_id==current_user.company.id).order_by(CompanySeats.seat_id_name.asc()).all()
    return company_seats

class AddCompanyUpdateForm(FlaskForm):
    company_updates = TextAreaField('Company Update', validators=[DataRequired()])
    submit = SubmitField('Add Company Update')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class FilterSeatDepartmentForm(FlaskForm):
    department = StringField('Department')
    submit = SubmitField('Filter')