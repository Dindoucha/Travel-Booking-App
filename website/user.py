from flask import current_app, render_template, redirect, send_file, url_for, flash, session, Blueprint,jsonify
from . import db
from datetime import datetime, time , timedelta
from .models import Transaction, User, Booking, Journey
from .forms import LoginForm, RegistrationForm, BookingForm, SearchForm
from werkzeug.security import generate_password_hash, check_password_hash
from .invoice import generate_invoice
userViews = Blueprint('userViews',__name__)
# Route for home page
@userViews.route('/', methods=['GET', 'POST'])
def home():
    form = SearchForm()
    if form.validate_on_submit():
        from_location = form.from_location.data
        to_location = form.to_location.data
        departure_date = form.departure_date.data
        # Query with filter for departure datetime range
        journeys = Journey.query.filter_by(departure=from_location, destination=to_location).filter(Journey.departure_time >= departure_date).all()
        print(journeys)
        # Render the search results template with the retrieved journeys
        return render_template('search_results.html', title='Search Results', journeys=journeys)
    return render_template('home.html', title='Home', form=form)

# Route for user registration
@userViews.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()

        # Log in the user
        session['user_id'] = user.id
        session['is_admin'] = user.is_admin
        flash('Congratulations, you are now a registered user!', category='success')
        return redirect(url_for('userViews.bookings'))

    return render_template('register.html', title='Register', form=form)

@userViews.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not check_password_hash(user.password, form.password.data):
            flash('Invalid email or password', category='error')
            return redirect(url_for('userViews.login'))
        session['user_id'] = user.id
        session['is_admin'] = user.is_admin
        if user.is_admin:
            return redirect(url_for('adminViews.home'))
        else:
            return redirect(url_for('userViews.bookings'))
    return render_template('login.html', title='Sign In', form=form)

# Route for user bookings
@userViews.route('/bookings', methods=['GET', 'POST'])
def bookings():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('userViews.login'))
    user = User.query.filter_by(id=user_id).first()
    bookings = Booking.query.filter_by(user_id=user_id).all()
    return render_template('bookings.html', title='My Bookings', user=user, bookings=bookings)

# Route for booking a journey
@userViews.route('/book_journey/<int:journey_id>', methods=['GET', 'POST'])
def book_journey(journey_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('userViews.login'))
    form = BookingForm()
    journey = Journey.query.filter_by(id=journey_id).first()
    if not journey:
        flash("Journey doesn't exist","error")
        return redirect(url_for("userViews.home"))
    # Calculate discount based on number of days in advance booking
    advance_booking_days = (journey.departure_time - datetime.now()).days
    if advance_booking_days >= 80:
        discount_percentage = 20
    elif advance_booking_days >= 60 and advance_booking_days <= 79:
        discount_percentage = 10
    elif advance_booking_days >= 45 and advance_booking_days <= 59:
        discount_percentage = 5
    else:
        discount_percentage = 0

    if form.validate_on_submit():
        num_of_seats = form.seats_booked.data
        is_business = True if form.ticket_class.data == "Business" else False
        booking_time = datetime.now()
        amount_paid = journey.price * num_of_seats
        if journey.available_seats < num_of_seats or num_of_seats <= 0:
            flash('Please choose a valid number of seats',category='error')
            return redirect(url_for('userViews.book_journey',journey_id=journey_id))
        # Apply discount to the amount paid
        discount_amount = amount_paid * discount_percentage / 100
        amount_paid -= discount_amount
        if is_business:
            amount_paid *= 2
        # Create booking object and add it to the database
        booking = Booking(user_id=user_id, journey_id=journey_id, booking_time=booking_time, seats_booked=num_of_seats, amount_paid=amount_paid,is_business=is_business)
        db.session.add(booking)
        db.session.commit()
        # Add transaction record to the database
        transaction = Transaction(amount=amount_paid, is_refund=False, user_id=user_id,transaction_time=datetime.now(),journey_id=journey_id)
        db.session.add(transaction)
        journey.update_available_seats()
        db.session.commit()
        flash('Booking confirmed',category='success')
        return redirect(url_for('userViews.bookings'))
    user = User.query.filter_by(id=user_id).first()
    return render_template('book_journey.html', title='Book Journey', form=form, journey=journey,discount_percentage=discount_percentage,user=user)


# Route for cancelling a booking
@userViews.route('/cancel_booking/<int:booking_id>', methods=['GET', 'POST'])
def cancel_booking(booking_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('userViews.login'))
    booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first()
    if not booking:
        flash('Booking not found', category='error')
        return redirect(url_for('userViews.bookings'))

    journey = booking.journey
    time_to_departure = journey.departure_time - datetime.now()

    amount_refunded = float(booking.amount_paid)
    if time_to_departure < timedelta(days=30):
        amount_refunded*=0
    elif time_to_departure < timedelta(days=60):
        amount_refunded*=0.5

    # Create transaction record for refund
    transaction = Transaction(amount=-(float(booking.amount_paid)-amount_refunded), is_refund=True, user_id=user_id,transaction_time=datetime.now(),journey_id=journey.id)
    db.session.add(transaction)
    db.session.delete(booking)
    journey.update_available_seats()
    db.session.commit()
    flash('Booking cancelled and refund processed', category='success')


    return redirect(url_for('userViews.bookings'))

# Route for user logout
@userViews.route('/delete-dindoucha')
def delete():
    return jsonify({"action":None})
# Route for user logout
@userViews.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('userViews.home'))

@userViews.route('/<int:booking_id>')
def generate_pdf(booking_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('userViews.login'))
    booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first()
    if not booking:
        flash('Booking not found', category='error')
        return redirect(url_for('userViews.bookings'))

    pdf = generate_invoice(booking)
    response = current_app.make_response(pdf.output(dest='S').encode('latin1'))
    response.headers.set('Content-Disposition', 'attachment', filename='invoice.pdf')
    response.headers.set('Content-Type', 'application/pdf')
    return response