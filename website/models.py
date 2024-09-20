from . import db
from datetime import datetime, timedelta
import random

CITIES = ['Newcastle', 'Bristol', 'Cardiff', 'Edinburgh', 'Manchester', 'London', 'Glasgow', 'Portsmouth', 'Dundee', 'Southampton', 'Birmingham', 'Aberdeen']
ROUTE_PRICES = {
    ('Dundee','Portsmout'):100,
    ('Bristol','Manchester'):60,
    ('Bristol','Newcastle'):80,
    ('Bristol','Glasgow'):90,
    ('Bristol','London'):60,
    ('Manchester','Southampton'):70,
    ('Cardiff','Edinburgh'):80,
}
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    
class Journey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    departure = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    travel_option = db.Column(db.Enum('Air', 'Coach', 'Train'), nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2))
    def get_max_seats(self):
        if self.travel_option == 'Air':
            return 120
        elif self.travel_option == 'Coach':
            return 50
        elif self.travel_option == 'Train':
            return 300

    def update_available_seats(self):
        self.available_seats = self.get_max_seats() - sum(booking.seats_booked for booking in self.bookings)

    def get_route_price(self):
        price = ROUTE_PRICES.get(tuple(sorted([self.departure,self.destination])),75)
        if self.travel_option == 'Air':
            return price
        elif self.travel_option == 'Coach':
            return round(price*1/3, 2)
        elif self.travel_option == 'Train':
            return round(price*2.5, 2)
        
    @classmethod
    def renew_data(cls):
        past_journeys = cls.query.filter(cls.departure_time < datetime.now()).all()

        # Delete each journey
        for journey in past_journeys:
            db.session.delete(journey)

        db.session.commit() 
        for departure in CITIES:
            for destination in CITIES:
                if departure == destination : continue
                for i in range(10):
                    departure_time = datetime.now()+timedelta(days=random.randint(0,90))
                    arrival_time = departure_time+timedelta(days=random.randint(1,7))
                    journey = cls(departure=departure, destination=destination, departure_time=departure_time,
                                    arrival_time=arrival_time, travel_option=random.choice(['Air', 'Coach', 'Train']))

                    journey.available_seats = journey.get_max_seats()
                    journey.price = journey.get_route_price()
                    db.session.add(journey)
        db.session.commit()

    
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    journey_id = db.Column(db.Integer, db.ForeignKey('journey.id', ondelete='CASCADE'), nullable=False)
    booking_time = db.Column(db.DateTime, nullable=False)
    seats_booked = db.Column(db.Integer, nullable=False)
    amount_paid = db.Column(db.Numeric(10,2), nullable=False)
    is_business = db.Column(db.Boolean, nullable=False, default=False)
    user = db.relationship('User', backref=db.backref('bookings', lazy=True))
    journey = db.relationship('Journey', backref=db.backref('bookings', lazy=True))


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    transaction_time = db.Column(db.DateTime, nullable=False)
    journey_id = db.Column(db.Integer, db.ForeignKey('journey.id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    is_refund = db.Column(db.Boolean, nullable=False, default=False)
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))
    journey = db.relationship('Journey', backref=db.backref('transactions', lazy=True))
