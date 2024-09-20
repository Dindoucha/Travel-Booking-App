from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField,PasswordField, SubmitField, SelectField, DateField, IntegerField, TimeField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange
from .models import CITIES
from datetime import date, datetime
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class BookingForm(FlaskForm):
    seats_booked = IntegerField('Seats Booked', validators=[DataRequired(), NumberRange(min=1)],default=1)
    ticket_class = SelectField('Ticket Class', choices=[('Economy', 'Economy'), ('Business', 'Business')], validators=[DataRequired()])
    submit = SubmitField('Book Now')

class JourneyForm(FlaskForm):
    departure = SelectField('Departure', validators=[DataRequired()], choices=CITIES)
    destination = SelectField('Destination', validators=[DataRequired()], choices=CITIES)
    departure_date = DateField('Departure Date', validators=[DataRequired()], format='%Y-%m-%d', default=date.today(),render_kw={"min": date.today()})
    departure_time = TimeField('Departure Time (HH:MM:SS)', validators=[DataRequired()], default=datetime.now().time())
    arrival_date = DateField('Arrival Date', validators=[DataRequired()], format='%Y-%m-%d', default=date.today(),render_kw={"min": date.today()})
    arrival_time = TimeField('Arrival Time (HH:MM:SS)', validators=[DataRequired()], default=datetime.now().time())
    travel_option = SelectField('Travel Option', choices=[('Air', 'Air'), ('Coach', 'Coach'), ('Train', 'Train')], validators=[DataRequired()])
    submit = SubmitField('Add Journey')

class SearchForm(FlaskForm):
    from_location = SelectField('From', validators=[DataRequired()], choices=CITIES)
    to_location = SelectField('To', validators=[DataRequired()], choices=CITIES)
    departure_date = DateField('Departure Date', validators=[DataRequired()], format='%Y-%m-%d', render_kw={"min": date.today()})
    submit = SubmitField('Search for Flights')

class PriceForm(FlaskForm):
    city1 = SelectField('Departure City', validators=[DataRequired()],choices=CITIES)
    city2 = SelectField('Destination City', validators=[DataRequired()],choices=CITIES)
    airfare = DecimalField('Airfare', validators=[DataRequired()])
    submit = SubmitField('Add Price')
