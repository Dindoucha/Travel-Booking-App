from flask import Blueprint, render_template, redirect, url_for, flash, session
from datetime import datetime 
from .models import Transaction, db,  Journey, Booking
from .forms import JourneyForm 

adminViews = Blueprint('adminViews', __name__)


@adminViews.route('/')
def home():
    if 'user_id' not in session or not session['is_admin']:
        flash('You are not authorized to view that page', category='error')
        return redirect(url_for('userViews.home'))
  
    journeys = Journey.query.order_by(Journey.id.desc()).all()
    bookings = Booking.query.order_by(Booking.id.desc()).all()
    transactions = Transaction.query.order_by(Transaction.id.desc()).all()
    return render_template('admin/home.html', journeys=journeys, bookings=bookings, transactions=transactions)

@adminViews.route('/add_journey', methods=['GET', 'POST'])
def add_journey():
    if 'user_id' not in session or not session['is_admin']:
        flash('You are not authorized to view that page', category='error')
        return redirect(url_for('userViews.login'))

    form = JourneyForm()
    if form.validate_on_submit():
        departure = form.departure.data
        destination = form.destination.data
        departure_time = datetime.combine(form.departure_date.data, form.departure_time.data)
        arrival_time = datetime.combine(form.arrival_date.data, form.arrival_time.data)
        if departure == destination:
            flash("Please choose a different departure/destination time","error")
            return redirect(url_for('adminViews.add_journey'))
        if departure_time >= arrival_time:
            flash("Please select a valid departure/arrival time","error")
            return redirect(url_for('adminViews.add_journey'))
        
        travel_option = form.travel_option.data

        # create a new journey instance
        journey = Journey(departure=departure, destination=destination, departure_time=departure_time,
                          arrival_time=arrival_time, travel_option=travel_option)

        # calculate the available seats and price
        journey.available_seats = journey.get_max_seats()
        journey.price = journey.get_route_price()
        # add the journey to the database
        db.session.add(journey)
        db.session.commit()

        flash('Journey added successfully!', 'success')
        return redirect(url_for('adminViews.home'))

    return render_template('admin/add_journey.html', form=form)

@adminViews.route('/edit_journey/<int:id>', methods=['GET', 'POST'])
def edit_journey(id):
    if 'user_id' not in session or not session['is_admin']:
        flash('You are not authorized to view that page', category='error')
        return redirect(url_for('userViews.login'))

    journey = Journey.query.get(id)
    if not journey:
        flash('Journey not found', category='error')
        return redirect(url_for('adminViews.home'))

    form = JourneyForm(obj=journey)
    
    if form.validate_on_submit():
        journey.departure = form.departure.data
        journey.destination = form.destination.data
        journey.departure_time = datetime.combine(form.departure_date.data, form.departure_time.data)
        journey.arrival_time = datetime.combine(form.arrival_date.data, form.arrival_time.data)
        journey.travel_option = form.travel_option.data
        # calculate the available seats and price
        journey.available_seats = journey.get_max_seats()
        journey.price = journey.get_route_price()
        db.session.commit()
        flash('Journey updated successfully!', 'success')
        return redirect(url_for('adminViews.home'))
    form.departure_date.data = journey.departure_time.date()
    form.departure_time.data = journey.departure_time.time()
    form.arrival_date.data = journey.arrival_time.date()
    form.arrival_time.data = journey.arrival_time.time()
    return render_template('admin/edit_journey.html', form=form)

@adminViews.route('/delete_journey/<int:id>', methods=['POST'])
def delete_journey(id):
    if 'user_id' not in session or not session['is_admin']:
        flash('You are not authorized to view that page', category='error')
        return redirect(url_for('userViews.login'))

    journey = Journey.query.get(id)
    if not journey:
        flash('Journey not found', category='error')
        return redirect(url_for('adminViews.home'))

    db.session.delete(journey)
    db.session.commit()
    flash('Journey deleted successfully!', 'success')
    return redirect(url_for('adminViews.home'))
