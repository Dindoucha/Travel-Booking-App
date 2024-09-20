from app import app

with app.app_context():
  # automatically add travels journies to database and delete old ones 
  # to make user test website with prefilled data
  from website.models import Journey
  Journey.renew_data()
  print("here")