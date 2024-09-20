from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from decouple import config
# from flask_apscheduler import APScheduler


db = SQLAlchemy()
# scheduler = APScheduler() pythonanywhere threads closed

DB_USERNAME = config('DB_USERNAME')
DB_PASSWORD = config('DB_PASSWORD')
DB_HOST = config('DB_HOST')
DB_NAME = config('DB_NAME') 

# def travels_auto_inserts():
#     # automatically add travels journies to database and delete old ones 
#     # to make user test website with prefilled data
#     with scheduler.app.app_context():
#         from .models import Journey
#         Journey.renew_data()
#         print("here")

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'jkedjzmeoiepz'
    # app.config['JOBS'] = [
    #     {
    #         "id": "task1",
    #         "func": travels_auto_inserts,
    #         "trigger": "cron",
    #         "day_of_week": "sun",
    #         "hour": 12,
    #         "minute": 0 
    #     }
    # ]
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    db.init_app(app)
    # scheduler.init_app(app)
    # Import the views module to register the routes
    from .user import userViews
    app.register_blueprint(userViews, url_prefix='/')
    from .admin import adminViews
    app.register_blueprint(adminViews, url_prefix='/admin')
    create_database(app)
    # scheduler.start()
    return app

def create_database(app) : 
    with app.app_context():
        db.create_all()
    print('Created Database !')