import requests
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy 
from os import environ
from dotenv import load_dotenv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secreting'

db = SQLAlchemy(app)

load_dotenv()
API_KEY = os.getenv('WEATHER_KEY')

# handles city table
class City(db.Model):
    __tablename__ = 'city'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True ,nullable=False)

    def __init__(self, name):
        self.name = name

db.create_all()

def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}'
    r = requests.get(url).json()
    return r

# Get weather for cities in city table
@app.route('/', methods=['GET'])
def index_get():
    cities = City.query.all()

    weather_data = []

    for city in cities: 
            r = get_weather_data(city.name)

            weather = {
                'city': city.name.title(),
                'temperature': r['main']['temp'],
                'description': r['weather'][0]['description'],
                'icon': r['weather'][0]['icon'],
            }

            weather_data.append(weather)


    return render_template('weather.html', weather_data=weather_data)

# Add location to city table
@app.route('/', methods=['POST'])
def index_post():
    new_city = request.form.get('city')
    err_msg = ''

    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()

        if not existing_city:
            new_city_data = get_weather_data(new_city)
            if new_city_data['cod'] == 200:
                new_city_obj = City(name=new_city)

                db.session.add(new_city_obj)
                db.session.commit()
            else:
                 err_msg = 'Invalid City'
        else:
             err_msg = 'City already exists'
    
    if err_msg:
         flash(err_msg, 'error')
    else:
         flash('City added successfully')
         

    return redirect(url_for('index_get'))

# Delete city in city table
@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()

    flash('City deleted', 'success')
    return redirect(url_for('index_get'))
