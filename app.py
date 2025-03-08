### Integrate HTML With Flask
### HTTP verb GET And POST

import re
import os
import json
import requests

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app=Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://zarox:newnew@localhost/flask_auth'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Explicit table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Regex Validation Functions
def validate_username(username):
    """Validate username: alphanumeric, '.', '_' only."""
    return bool(re.match(r'^[a-zA-Z0-9._]+$', username))

def validate_email(email):
    """Validate email: strict Gmail regex."""
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', email))

def validate_password(password):
    """Validate password: minimum 8 characters."""
    return len(password) >= 8


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        if not validate_email(email):
            flash('Please enter a valid Gmail address.', 'danger')

        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:  # In a real app, use password hashing (e.g., bcrypt)
            login_user(user)
            return redirect(url_for('profile'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Validate username
        if not validate_username(username):
            flash('Username can only contain alphanumeric characters, ".", and "_".', 'danger')
            return redirect(url_for('signup'))

        # Validate email
        if not validate_email(email):
            flash('Please enter a valid Gmail address.', 'danger')
            return redirect(url_for('signup'))

        # Validate password
        if not validate_password(password):
            flash('Password must be at least 8 characters long.', 'danger')
            return redirect(url_for('signup'))

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('signup'))

        # Check if email already registered
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email.', 'danger')
            return redirect(url_for('signup'))

        # Create new user
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/bmi_final.html')
def bmi():
    return render_template('bmi_final.html')

@app.route('/Calorie-Counter.html')
def CalCount():
    return render_template('Calorie-Counter.html')

@app.route('/blog.html')
def blog():
    return render_template('blog.html')

@app.route('/video.html')
def vid():
    return render_template('video.html')

@app.route('/blog-post-1.html')
def blog1():
    return render_template('blog-post-1.html')

@app.route('/video-post-1.html')
def vid1():
    return render_template('video-post-1.html')

@app.route('/blog-post-2.html')
def blog2():
    return render_template('blog-post-2.html')

@app.route('/video-post-2.html')
def vid2():
    return render_template('video-post-3.html')

@app.route('/blog-post-3.html')
def blog3():
    return render_template('blog-post-3.html')

@app.route('/video-post-3.html')
def vid3():
    return render_template('video-post-3.html')

@app.route('/blog-post-4.html')
def blog4():
    return render_template('blog-post-4.html')

@app.route('/video-post-4.html')
def vid4():
    return render_template('video-post-4.html')

@app.route('/blog-post-5.html')
def blog5():
    return render_template('blog-post-5.html')

@app.route('/video-post-5.html')
def vid5():
    return render_template('video-post-5.html')

@app.route('/blog-post-6.html')
def blog6():
    return render_template('blog-post-6.html')

@app.route('/video-post-6.html')
def vid6():
    return render_template('video-post-6.html')

# Calorie Counter (meal)

@app.route('/submit', methods=['POST'])
def submit():
    output = request.form.to_dict()
    food_item = output['meal1']

    end_pt_url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    query = {
        "query": food_item,
    }
    api_id = "API ID"
    api_key = "API KEY"

    headers = {
        "x-app-id": api_id,
        "x-app-key": api_key,
        "Content-Type": "application/json"
    }

    r = requests.post(end_pt_url, headers=headers, json=query)
    data = json.loads(r.text)

    for food in data['foods']:
        name = food['food_name']
        cal = food['nf_calories']
        serving_qty = food["serving_qty"]
        serving_unit = food["serving_unit"]
        return render_template('result.html', cal=cal)

# bmi counter

@app.route('/bmi', methods=['POST'])
def bmi_res():
    output = request.form.to_dict()
    height = int(output['height'])
    weight = int(output['weight'])
    height_ = int(height) / 100
    bmi = (weight / (height ** 2)) * 10000
    if bmi <= 18.5:
        bmi_ = 'Underweight'
        bmi__ = 'Underweight'

    elif 18.5 < bmi <= 24.9:
        bmi_ = 'Normal'
        bmi__ = 'Normal'

    elif 25 <= bmi <= 29.9:
        bmi_ = 'Overweight'
        bmi__ = 'Overweight'

    elif 30 <= bmi <= 39.9:
        bmi_ = 'Obese'
        bmi__ = 'Obese'
    elif bmi >= 40:
        bmi_ = 'Morbidly'
        bmi__ = 'Morbidly Obese'
    else:
        bmi_ = 'Incorrect'
        bmi__ = 'Incorrect input'
    return render_template('bmi.html', bmi=round(bmi,2), bmi_ = bmi_, bmi__ = bmi__)
    
# Calorie counter (exercise)

@app.route('/result', methods=['POST'])
def calculate_calories_burnt():
    exercise = request.form.get('exercise')
    gender = request.form.get('gender')
    weight = float(request.form.get('weight'))
    height = float(request.form.get('height'))
    age = int(request.form.get('age'))

    # Make API request to calculate calories burnt
    end_pt_url = "https://trackapi.nutritionix.com/v2/natural/exercise"

    query = {
        "query": exercise,
        "gender": gender,
        "weight_kg": weight,
        "height_cm": height,
        "age": age
    }


    headers = {
        "x-app-id": "66e88fcd",
        "x-app-key": "915bd34e3996d68e870d3be75c07b467",
        "Content-Type": "application/json"
    }

    response = requests.post(end_pt_url, headers=headers, json=query)
    data = json.loads(response.text)

    exercise_details = []
    for exercise in data['exercises']:
        name = exercise['name']
        calories_burnt = exercise['nf_calories']
        duration = exercise["duration_min"]
        exercise_details.append((name, calories_burnt, duration))

    return render_template('submit.html', calories_burnt=calories_burnt)


app.static_folder = 'static'

if __name__=='__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(debug=True)